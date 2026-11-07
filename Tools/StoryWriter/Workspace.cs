using System.Text.Json.Nodes;
using Avalonia.Threading;
using StoryWriter.Model;

namespace StoryWriter;

/// <summary>The open dialogue folder: every character file, plus a watcher for edits made outside the app.</summary>
public sealed class Workspace : IDisposable
{
	public string Folder { get; }
	public List<DialogueDocument> Docs { get; } = new();
	FileSystemWatcher? _watcher;

	public event Action? DocsChanged;                      // added / removed / renamed / dirty state
	public event Action<DialogueDocument>? ExternalConflict; // changed on disk while we have unsaved edits

	public Workspace(string folder)
	{
		Folder = folder;
		foreach (var f in Directory.GetFiles(folder, "*.json").OrderBy(x => x, StringComparer.OrdinalIgnoreCase))
		{
			try { Add(DialogueDocument.Load(f)); }
			catch (Exception e) { LoadErrors.Add($"{Path.GetFileName(f)}: {e.Message}"); }
		}
		_watcher = new FileSystemWatcher(folder, "*.json") { NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName | NotifyFilters.Size };
		_watcher.Changed += (_, e) => Post(() => OnDiskChange(e.FullPath));
		_watcher.Created += (_, e) => Post(() => OnDiskChange(e.FullPath));
		_watcher.Renamed += (_, e) => Post(() => OnDiskChange(e.FullPath));
		_watcher.Deleted += (_, e) => Post(() => OnDiskChange(e.FullPath));
		_watcher.EnableRaisingEvents = true;
	}

	public List<string> LoadErrors { get; } = new();

	static void Post(Action a) => Dispatcher.UIThread.Post(a);

	void Add(DialogueDocument d)
	{
		Docs.Add(d);
		d.Changed += () => DocsChanged?.Invoke();
	}

	public DialogueDocument? Find(string id) => Docs.FirstOrDefault(d => d.Id == id);
	public IReadOnlyCollection<string> HunkIds => Docs.Select(d => d.Id).ToList();

	void OnDiskChange(string path)
	{
		var doc = Docs.FirstOrDefault(d => string.Equals(d.FilePath, path, StringComparison.OrdinalIgnoreCase));
		if (!File.Exists(path))
		{
			if (doc != null && !doc.Dirty)
			{
				Docs.Remove(doc);
				DocsChanged?.Invoke();
			}
			return;
		}
		if (doc == null)
		{
			try
			{
				Add(DialogueDocument.Load(path));
				Docs.Sort((a, b) => string.Compare(a.FileName, b.FileName, StringComparison.OrdinalIgnoreCase));
				DocsChanged?.Invoke();
			}
			catch
			{
				// Probably mid-write; the next change event will retry.
			}
			return;
		}
		DateTime t;
		try { t = File.GetLastWriteTimeUtc(path); } catch { return; }
		if (t == doc.LoadedWriteTime) return; // our own save
		if (doc.Dirty)
		{
			ExternalConflict?.Invoke(doc);
			return;
		}
		try { doc.Reload(); }
		catch { /* half-written file; wait for the next event */ }
	}

	public DialogueDocument CreateConversation(string id, string name)
	{
		var path = Path.Combine(Folder, id + ".json");
		var root = new JsonObject
		{
			["id"] = id,
			["name"] = name,
			["malady"] = "",
			["room"] = "",
			["tagline"] = "",
			["entries"] = new JsonArray(
				new JsonObject { ["if"] = "visits == 0", ["node"] = "v1" },
				new JsonObject { ["if"] = "true", ["node"] = "v2" }),
			["endings"] = new JsonObject(Dialogue.Endings.Select(e =>
				new KeyValuePair<string, JsonNode?>(e, new JsonObject { ["title"] = "", ["text"] = "" }))),
			["nodes"] = new JsonObject
			{
				["v1"] = new JsonObject { ["lines"] = new JsonArray("*Something in the house stirs.*", "Hi. I'm {name}."), ["end"] = true },
				["v2"] = new JsonObject { ["lines"] = new JsonArray("Back again, {player}?"), ["end"] = true },
			},
		};
		File.WriteAllText(path, HouseJson.Serialize(root));
		var doc = Docs.FirstOrDefault(d => d.FilePath == path);
		if (doc == null)
		{
			doc = DialogueDocument.Load(path);
			Add(doc);
			Docs.Sort((a, b) => string.Compare(a.FileName, b.FileName, StringComparison.OrdinalIgnoreCase));
		}
		DocsChanged?.Invoke();
		return doc;
	}

	public void Dispose()
	{
		_watcher?.Dispose();
		_watcher = null;
	}
}

/// <summary>Remembers the last folder between sessions.</summary>
public static class AppSettings
{
	static string FilePath => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "StoryWriter", "settings.json");

	public static string? LastFolder
	{
		get
		{
			try { return Dialogue.Str((JsonNode.Parse(File.ReadAllText(FilePath)) as JsonObject)?["lastFolder"]); }
			catch { return null; }
		}
		set
		{
			try
			{
				Directory.CreateDirectory(Path.GetDirectoryName(FilePath)!);
				File.WriteAllText(FilePath, new JsonObject { ["lastFolder"] = value }.ToJsonString());
			}
			catch
			{
				// Not worth bothering anyone about.
			}
		}
	}
}
