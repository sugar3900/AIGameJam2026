namespace StoryWriter;

static class ProjectPaths
{
	public const string DialogueRelative = "Content/ICanFixHim/Data/Dialogue";

	/// <summary>Walks up from <paramref name="start"/> looking for the Unreal project and returns its dialogue folder.</summary>
	public static string? FindDialogueDir(string start)
	{
		for (var dir = new DirectoryInfo(start); dir != null; dir = dir.Parent)
		{
			if (dir.GetFiles("*.uproject").Length > 0)
			{
				var d = Path.Combine(dir.FullName, DialogueRelative);
				return Directory.Exists(d) ? d : null;
			}
		}
		return null;
	}

	public static string? DefaultDialogueDir() =>
		FindDialogueDir(Environment.CurrentDirectory) ?? FindDialogueDir(AppContext.BaseDirectory);
}
