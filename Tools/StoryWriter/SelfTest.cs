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
		Console.WriteLine(failures == 0 ? "SELFTEST OK" : $"SELFTEST FAILED ({failures})");
		return failures == 0 ? 0 : 1;
	}
}
