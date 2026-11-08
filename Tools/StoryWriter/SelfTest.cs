using StoryWriter.Model;
using StoryWriter.Runtime;

namespace StoryWriter;

/// <summary>`dotnet run -- --selftest [dir]`: round-trips every file, validates, and auto-plays every arc.</summary>
static class SelfTest
{
	public static int Run(string? dir)
	{
		dir ??= ProjectPaths.FindDialogueDir(Environment.CurrentDirectory) ?? throw new Exception("No dialogue dir");
		var docs = Directory.GetFiles(dir, "*.json").OrderBy(x => x).Select(DialogueDocument.Load).ToList();
		var ids = docs.Select(d => d.Id).ToList();
		int failures = 0;
		foreach (var d in docs)
		{
			var original = File.ReadAllText(d.FilePath);
			var again = d.SerializedText();
			bool same = original == again;
			if (!same)
			{
				failures++;
				var a = original.Split('\n');
				var b = again.Split('\n');
				int i = 0;
				while (i < Math.Min(a.Length, b.Length) && a[i] == b[i]) i++;
				Console.WriteLine($"ROUNDTRIP DIFF {d.FileName} line {i + 1}:\n  - {(i < a.Length ? a[i] : "<eof>")}\n  + {(i < b.Length ? b[i] : "<eof>")}");
			}
			var issues = Validator.Validate(d, ids);
			Console.WriteLine($"{d.Id,-10} {d.Nodes.Count,3} nodes  roundtrip {(same ? "ok" : "DIFF")}  {issues.Count(x => x.IsError)} errors {issues.Count(x => !x.IsError)} warnings");
			foreach (var x in issues) Console.WriteLine("   " + x);
		}

		// Auto-play each arc with each "strategy" (always first / last visible choice) and report the endings.
		foreach (var pick in new[] { "first", "last" })
		{
			var state = new PreviewState();
			var runner = new DialogueRunner(state, id => docs.FirstOrDefault(d => d.Id == id));
			foreach (var d in docs)
			{
				var path = new List<string>();
				for (int visit = 0; visit < 8 && !state.Hunk(d.Id).Fixed; visit++)
				{
					if (!runner.Start(d.Id)) { Console.WriteLine($"  {d.Id}: no entry"); failures++; break; }
					path.Add("|" + runner.ActiveNodeId);
					for (int guard = 0; runner.IsActive && guard < 500; guard++)
					{
						var v = runner.View!;
						var vis = v.VisibleChoices.ToList();
						if (v.IsLastLine && vis.Count > 0)
						{
							runner.ChooseRaw((pick == "first" ? vis[0] : vis[^1]).Index);
							if (runner.IsActive) path.Add(runner.ActiveNodeId!);
						}
						else
						{
							var before = runner.ActiveNodeId;
							runner.Advance();
							if (runner.IsActive && runner.ActiveNodeId != before) path.Add(runner.ActiveNodeId!);
						}
					}
				}
				var h = state.Hunk(d.Id);
				Console.WriteLine($"  [{pick}] {d.Id}: visits={h.Visits} R{h.Romance} F{h.Friendship} X{h.Friction} ending={h.Ending}  {string.Join(" ", path)}");
				if (!h.Fixed) failures++;
			}
		}
		failures += AudioChecks(docs);
		Console.WriteLine(failures == 0 ? "SELFTEST OK" : $"SELFTEST FAILED ({failures})");
		return failures == 0 ? 0 : 1;
	}

	/// <summary>
	/// `--audioloop [file.wav] [seconds]`: loops a music file through the real audio backend (default: a generated
	/// 1.5 s tone) and reports every (re)start, so a loop that stops or leaves gaps shows up. Audible.
	/// </summary>
	public static int AudioLoop(string? file, double seconds)
	{
		if (!AudioService.Available) { Console.WriteLine("audio unavailable: " + AudioService.UnavailableReason); return 1; }
		if (string.IsNullOrEmpty(file) || file == "-")
		{
			file = Path.Combine(Path.GetTempPath(), "storywriter_loop_test.wav");
			const int rate = 44100;
			var n = (int)(rate * 1.5);
			using var w = new BinaryWriter(File.Create(file));
			w.Write("RIFF"u8); w.Write(36 + n * 2); w.Write("WAVE"u8); w.Write("fmt "u8); w.Write(16); w.Write((short)1); w.Write((short)1);
			w.Write(rate); w.Write(rate * 2); w.Write((short)2); w.Write((short)16); w.Write("data"u8); w.Write(n * 2);
			for (int i = 0; i < n; i++) w.Write((short)(Math.Sin(2 * Math.PI * 440 * i / rate) * 3000));
		}
		var starts = new List<double>();
		var clock = System.Diagnostics.Stopwatch.StartNew();
		AudioDiagnostics.Spawned += () => { lock (starts) starts.Add(clock.Elapsed.TotalSeconds); };
		var owner = new object();
		AudioService.PlayMusic(owner, file);
		Thread.Sleep(TimeSpan.FromSeconds(seconds));
		var stillPlaying = AudioService.CurrentMusic != null;
		AudioService.StopMusic(owner);
		var d = AudioLibrary.WavDuration(file) ?? 0;
		lock (starts)
		{
			Console.WriteLine($"audioloop: backend {AudioService.BackendName}, clip {d:0.00} s, {starts.Count} starts in {seconds:0.#} s, still playing: {stillPlaying}");
			for (int i = 0; i < starts.Count; i++)
				Console.WriteLine($"  start {i}: {starts[i]:0.000} s" + (i > 0 ? $"  (+{starts[i] - starts[i - 1]:0.000})" : ""));
			var expected = d > 0 ? (int)Math.Floor(seconds / d) : 1;
			var ok = stillPlaying && starts.Count >= Math.Max(1, expected);
			Console.WriteLine(ok ? "AUDIOLOOP OK" : "AUDIOLOOP FAILED");
			return ok ? 0 : 1;
		}
	}

	/// <summary>Voice-over key rules and music matching, plus a cross-check against the clips already on disk.</summary>
	static int AudioChecks(List<DialogueDocument> docs)
	{
		int failures = 0;
		void Check(bool ok, string what)
		{
			if (ok) return;
			failures++;
			Console.WriteLine("AUDIO FAIL: " + what);
		}

		Check(AudioLibrary.VoiceKey("lukey", "today", 1) == "VO_lukey_today_1", "voice key format");
		Check(Dialogue.StripInlineTags("*{sfx:Spark}The fuse box pops.*", out var fx1, out var sfx1) == "*The fuse box pops.*" && fx1 == null && sfx1.SequenceEqual(new[] { "Spark" }), "sfx tag stripped from narration");
		Check(Dialogue.StripInlineTags("{sfx:Thunder} You: Hi. {fx:hearts}{sfx:Rain}", out var fx2, out var sfx2) == "You: Hi." && fx2 == "hearts" && sfx2.SequenceEqual(new[] { "Thunder", "Rain" }), "several tags, speaker kept");
		Check(AudioLibrary.IsVoiceable("Hey, sweetheart."), "plain line is voiced");
		Check(!AudioLibrary.IsVoiceable("*He grins.*"), "narration is not voiced");
		Check(!AudioLibrary.IsVoiceable("You: Hi."), "player line is not voiced");
		Check(!AudioLibrary.IsVoiceable("*...* ..."), "line with no words is not voiced");

		var tmp = Path.Combine(Path.GetTempPath(), "storywriter-audio-" + Guid.NewGuid().ToString("N"));
		try
		{
			Directory.CreateDirectory(Path.Combine(tmp, "vo", "lukey"));
			Directory.CreateDirectory(Path.Combine(tmp, "bgm"));
			var vo = Path.Combine(tmp, "vo");
			File.WriteAllBytes(Path.Combine(vo, "lukey", "VO_lukey_today_1.wav"), new byte[44]);
			Check(AudioLibrary.ResolveVoice(vo, "lukey", "today", 1, "Hey.") != null, "existing clip resolves");
			Check(AudioLibrary.ResolveVoice(vo, "lukey", "today", 0, "Hey.") == null, "missing clip is null");
			Check(AudioLibrary.ResolveVoice(vo, "lukey", "today", 1, "*Hey.*") == null, "narration never resolves");
			Check(AudioLibrary.ResolveVoice(vo, "lukey", "today", 1, "You: Hey.") == null, "player line never resolves");
			Check(AudioLibrary.ResolveVoice(null, "lukey", "today", 1, "Hey.") == null, "no voice dir is null");
			foreach (var n in new[] { "BGM_MainMenu.wav", "BGM_Lukey.wav", "BGM_Explore.WAV", "notes.txt" })
				File.WriteAllBytes(Path.Combine(tmp, "bgm", n), new byte[1]);
			var tracks = AudioLibrary.ScanMusic(Path.Combine(tmp, "bgm"));
			Check(tracks.Count == 3, $"scan finds 3 tracks (got {tracks.Count})");
			Check(AudioLibrary.MatchMusic(tracks, "lukey")?.Name == "Lukey", "BGM_Lukey matches 'lukey'");
			Check(AudioLibrary.MatchMusic(tracks, "LUKEY")?.Name == "Lukey", "match ignores case");
			Check(AudioLibrary.MatchMusic(tracks, "main_menu")?.Name == "MainMenu", "match ignores punctuation");
			Check(AudioLibrary.MatchMusic(tracks, "wyatt") == null, "no track for wyatt");
			Check(AudioLibrary.ScanMusic(Path.Combine(tmp, "missing")).Count == 0, "missing BGM folder is empty");
		}
		finally
		{
			Directory.Delete(tmp, true);
		}

		// Every clip the generator recorded must map back to a spoken line by the same key rules.
		var voDir = ProjectPaths.VoiceDir();
		int clips = 0;
		if (voDir != null && Directory.Exists(voDir))
		{
			foreach (var doc in docs)
			{
				var dir = Path.Combine(voDir, doc.Id);
				if (!Directory.Exists(dir)) continue;
				var expected = new HashSet<string>();
				foreach (var id in doc.NodeIds)
				{
					var lines = Dialogue.Lines(doc.Node(id)!);
					for (int i = 0; i < lines.Count; i++)
						if (AudioLibrary.ResolveVoice(voDir, doc.Id, id, i, lines[i]) != null) expected.Add(AudioLibrary.VoiceKey(doc.Id, id, i) + ".wav");
				}
				var onDisk = Directory.GetFiles(dir, "*.wav").Select(Path.GetFileName).ToList();
				clips += onDisk.Count;
				foreach (var f in onDisk.Where(f => !expected.Contains(f!)))
					Check(false, $"clip {doc.Id}/{f} has no matching spoken line");
			}
		}
		Console.WriteLine($"audio: {clips} voice clips checked, {AudioLibrary.ScanMusic(ProjectPaths.MusicDir()).Count} music tracks, backend {AudioService.BackendName}");
		return failures;
	}
}
