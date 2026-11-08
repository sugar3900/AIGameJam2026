using System.Text.RegularExpressions;
using StoryWriter.Model;

namespace StoryWriter.Runtime;

/// <summary>A background-music loop found on disk. <see cref="Name"/> is the file name without "BGM_" ("Lukey", "MainMenu").</summary>
public sealed record MusicTrack(string Name, string Path);

/// <summary>
/// Finds the game's audio by file convention (see Tools/Audio/generate_vo.py): a spoken line at index N of node
/// NODE in dialogue script SCRIPT has the clip "Art Source/Audio/VO/SCRIPT/VO_SCRIPT_NODE_N.wav". Music loops
/// are "Art Source/Audio/BGM/BGM_Name.wav", matched to a conversation by its id.
/// </summary>
public static class AudioLibrary
{
	static readonly string[] MusicExtensions = { ".wav", ".ogg", ".mp3", ".flac" };
	static readonly Regex StageDirection = new(@"\*[^*]*\*", RegexOptions.Compiled);

	/// <summary>Only plain lines are voiced: never narration, never the player.</summary>
	public static bool IsSpoken(Speaker speaker) => speaker == Speaker.Him;

	/// <summary>Mirror of the generator: a spoken line with nothing readable once stage directions go (e.g. "...") gets no clip.</summary>
	public static bool IsVoiceable(string rawLine)
	{
		var (speaker, text) = Dialogue.ParseLine(rawLine);
		return IsSpoken(speaker) && StageDirection.Replace(text, " ").Any(char.IsLetter);
	}

	/// <summary>"VO_lukey_today_1": the key shared with the generator and the game (index = position in the node's lines).</summary>
	public static string VoiceKey(string script, string node, int index) => $"VO_{script}_{node}_{index}";

	/// <summary>The clip path a line would have, whether or not the file exists.</summary>
	public static string? VoicePath(string? voiceDir, string script, string node, int index) =>
		voiceDir == null ? null : Path.Combine(voiceDir, script, VoiceKey(script, node, index) + ".wav");

	/// <summary>The clip for this line if the file exists; null for lines that can't or don't have one.</summary>
	public static string? ResolveVoice(string? voiceDir, string script, string node, int index, string rawLine)
	{
		if (!IsVoiceable(rawLine)) return null;
		var p = VoicePath(voiceDir, script, node, index);
		return p != null && File.Exists(p) ? p : null;
	}

	public static List<MusicTrack> ScanMusic(string? musicDir)
	{
		var list = new List<MusicTrack>();
		if (musicDir == null || !Directory.Exists(musicDir)) return list;
		foreach (var f in Directory.GetFiles(musicDir).OrderBy(x => x, StringComparer.OrdinalIgnoreCase))
		{
			if (!MusicExtensions.Contains(Path.GetExtension(f).ToLowerInvariant())) continue;
			var name = Path.GetFileNameWithoutExtension(f);
			if (name.StartsWith("BGM_", StringComparison.OrdinalIgnoreCase)) name = name[4..];
			else if (name.StartsWith("BGM", StringComparison.OrdinalIgnoreCase) && name.Length > 3 && !char.IsLetterOrDigit(name[3])) name = name[4..];
			if (name.Length > 0) list.Add(new MusicTrack(name, f));
		}
		return list;
	}

	static string Norm(string s) => new(s.Where(char.IsLetterOrDigit).Select(char.ToLowerInvariant).ToArray());

	/// <summary>The loop for a conversation / character id, matched case-insensitively and ignoring punctuation.</summary>
	public static MusicTrack? MatchMusic(IEnumerable<MusicTrack> tracks, string? id)
	{
		if (string.IsNullOrEmpty(id)) return null;
		var n = Norm(id);
		return n.Length == 0 ? null : tracks.FirstOrDefault(t => Norm(t.Name) == n);
	}

	/// <summary>A random variant of SFX cue <paramref name="cue"/>: SFX_Cue.wav or SFX_Cue_N.wav in <paramref name="sfxDir"/>, or null.</summary>
	public static string? SfxPath(string? sfxDir, string cue)
	{
		if (sfxDir == null || !Directory.Exists(sfxDir) || cue.Length == 0) return null;
		var rx = new System.Text.RegularExpressions.Regex("^SFX_" + System.Text.RegularExpressions.Regex.Escape(cue) + @"(_\d+)?\.wav$");
		var files = Directory.GetFiles(sfxDir, "SFX_*.wav").Where(f => rx.IsMatch(Path.GetFileName(f))).ToList();
		return files.Count == 0 ? null : files[Random.Shared.Next(files.Count)];
	}

	/// <summary>Length of a PCM/float WAV in seconds, or null if it can't be read.</summary>
	public static double? WavDuration(string path)
	{
		try
		{
			using var fs = File.OpenRead(path);
			using var r = new BinaryReader(fs);
			if (fs.Length < 44 || new string(r.ReadChars(4)) != "RIFF") return null;
			r.ReadInt32();
			if (new string(r.ReadChars(4)) != "WAVE") return null;
			int byteRate = 0;
			while (fs.Position + 8 <= fs.Length)
			{
				var id = new string(r.ReadChars(4));
				uint size = r.ReadUInt32();
				if (id == "fmt ")
				{
					r.ReadBytes(8);
					byteRate = r.ReadInt32();
					fs.Position += size - 12 + (size & 1);
				}
				else if (id == "data")
				{
					if (byteRate <= 0) return null;
					long bytes = size == 0xFFFFFFFF || fs.Position + size > fs.Length ? fs.Length - fs.Position : size;
					return (double)bytes / byteRate;
				}
				else fs.Position += size + (size & 1);
			}
		}
		catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or EndOfStreamException)
		{
			// Unreadable or truncated: just no duration.
		}
		return null;
	}

	public static string DescribeClip(string path)
	{
		var d = WavDuration(path);
		return Path.GetFileName(path) + (d is { } s ? $" · {s:0.0} s" : "");
	}
}
