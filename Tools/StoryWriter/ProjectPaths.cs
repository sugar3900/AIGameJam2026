namespace StoryWriter;

static class ProjectPaths
{
	public const string DialogueRelative = "Content/ICanFixHim/Data/Dialogue";
	public const string VoiceRelative = "Art Source/Audio/VO";
	public const string MusicRelative = "Art Source/Audio/BGM";

	/// <summary>Walks up from <paramref name="start"/> looking for the Unreal project and returns its root folder.</summary>
	public static string? FindRoot(string start)
	{
		for (var dir = new DirectoryInfo(start); dir != null; dir = dir.Parent)
		{
			try
			{
				if (dir.GetFiles("*.uproject").Length > 0) return dir.FullName;
			}
			catch (IOException)
			{
				// Unreadable folder on the way up: keep walking.
			}
		}
		return null;
	}

	/// <summary>Walks up from <paramref name="start"/> looking for the Unreal project and returns its dialogue folder.</summary>
	public static string? FindDialogueDir(string start)
	{
		var root = FindRoot(start);
		if (root == null) return null;
		var d = Path.Combine(root, DialogueRelative);
		return Directory.Exists(d) ? d : null;
	}

	public static string? DefaultDialogueDir() =>
		FindDialogueDir(Environment.CurrentDirectory) ?? FindDialogueDir(AppContext.BaseDirectory);

	/// <summary>The repository root (where the .uproject lives), used to find voice-over and music files.</summary>
	public static string? DefaultRoot() =>
		FindRoot(Environment.CurrentDirectory) ?? FindRoot(AppContext.BaseDirectory);

	public static string? VoiceDir(string? root = null) => Under(root ?? DefaultRoot(), VoiceRelative);
	public static string? MusicDir(string? root = null) => Under(root ?? DefaultRoot(), MusicRelative);

	static string? Under(string? root, string relative) => root == null ? null : Path.Combine(root, relative);
}
