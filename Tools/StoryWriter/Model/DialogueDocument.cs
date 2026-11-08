using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using Avalonia;

namespace StoryWriter.Model;

public enum LinkKind { Entry, Goto, Choice, Topic }

/// <summary>An arrow in the graph: entry -> node, node.goto, node.choices[i], node.topics[key].</summary>
public sealed record DialogueLink(
	LinkKind Kind,
	string? Source,     // null for entries
	string Target,
	string? Condition,  // the "if", null/empty when unconditional
	string Label,       // choice text / [topic] / entry index
	JsonObject? Effects,
	int Index,          // choice index / entry index
	string? TopicKey)
{
	public bool IsConditional => !Dialogue.IsTrivialCondition(Condition);
}

public enum NodeKind { Story, Hypertext, Ending }

public enum Speaker { Him, You, Narration }

public sealed record TopicRef(int Start, int Length, string Shown, string TopicId);

/// <summary>Static helpers for the dialogue format (mirrors FixHimDialogueSubsystem.cpp).</summary>
public static class Dialogue
{
	public static readonly string[] Endings = { "romance_success", "romance_failure", "friend_success", "friend_failure" };
	public static readonly string[] Stats = { "romance", "friendship", "friction" };
	public static readonly string[] FxKinds = { "fade", "hearts" };
	static readonly Regex TopicRx = new(@"\[([^\[\]]+)\]", RegexOptions.Compiled);

	public static bool IsTrivialCondition(string? c) =>
		string.IsNullOrWhiteSpace(c) || c.Trim().Equals("true", StringComparison.OrdinalIgnoreCase);

	public static (Speaker speaker, string text) ParseLine(string raw)
	{
		var t = raw.Trim();
		if (t.StartsWith("You:", StringComparison.OrdinalIgnoreCase)) return (Speaker.You, t[4..].TrimStart());
		if (t.Length > 1 && t.StartsWith('*') && t.EndsWith('*')) return (Speaker.Narration, t[1..^1]);
		return (Speaker.Him, t);
	}

	public static string ComposeLine(Speaker s, string text) => s switch
	{
		Speaker.You => "You: " + text,
		Speaker.Narration => "*" + text + "*",
		_ => text,
	};

	public static List<TopicRef> Topics(string text)
	{
		var list = new List<TopicRef>();
		foreach (Match m in TopicRx.Matches(text))
		{
			var inner = m.Groups[1].Value;
			int bar = inner.IndexOf('|');
			var shown = bar >= 0 ? inner[..bar] : inner;
			var topic = (bar >= 0 ? inner[(bar + 1)..] : inner).Trim().ToLowerInvariant();
			list.Add(new TopicRef(m.Index, m.Length, shown, topic));
		}
		return list;
	}

	/// <summary>"romance: 2, flag.x: 1" (also accepts "romance +2", "romance=2").</summary>
	public static string FormatEffects(JsonObject? o)
	{
		if (o == null || o.Count == 0) return "";
		return string.Join(", ", o.Select(kv => $"{kv.Key}: {Num(kv.Value)}"));
	}

	public static string FormatEffectsShort(JsonObject? o)
	{
		if (o == null || o.Count == 0) return "";
		return string.Join(" ", o.Select(kv =>
		{
			var n = Num(kv.Value);
			return $"{kv.Key}{(n >= 0 ? "+" : "")}{n}";
		}));
	}

	public static JsonObject? ParseEffects(string? text, out string? error)
	{
		error = null;
		if (string.IsNullOrWhiteSpace(text)) return null;
		var o = new JsonObject();
		foreach (var part in text.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
		{
			var m = Regex.Match(part, @"^([A-Za-z_][A-Za-z0-9_.]*)\s*(?:[:=]\s*)?([+-]?\s*\d+)$");
			if (!m.Success) { error = $"Can't read effect '{part}' (use e.g. romance: 2)"; return null; }
			o[m.Groups[1].Value.ToLowerInvariant()] = int.Parse(m.Groups[2].Value.Replace(" ", "").TrimStart('+'));
		}
		return o.Count > 0 ? o : null;
	}

	public static int Num(JsonNode? n)
	{
		if (n is JsonValue v)
		{
			if (v.TryGetValue<int>(out var i)) return i;
			if (v.TryGetValue<double>(out var d)) return (int)Math.Round(d);
			if (v.TryGetValue<bool>(out var b)) return b ? 1 : 0;
			if (v.TryGetValue<System.Text.Json.JsonElement>(out var e))
			{
				if (e.ValueKind == System.Text.Json.JsonValueKind.Number) return (int)Math.Round(e.GetDouble());
				if (e.ValueKind == System.Text.Json.JsonValueKind.True) return 1;
			}
		}
		return 0;
	}

	public static string? Str(JsonNode? n) => n is JsonValue v && v.TryGetValue<string>(out var s) ? s : null;
	public static bool Bool(JsonNode? n) => n is JsonValue v && v.TryGetValue<bool>(out var b) && b;

	/// <summary>The words a link shows in the text (never its internal key); falls back to the key if it isn't in the text.</summary>
	public static string TopicLabel(JsonObject node, string key) =>
		Lines(node).SelectMany(Topics).FirstOrDefault(t => t.TopicId.Equals(key, StringComparison.OrdinalIgnoreCase))?.Shown.Trim() is { Length: > 0 } s ? s : key;

	public static List<string> Lines(JsonObject node)
	{
		var list = new List<string>();
		if (node["lines"] is JsonArray a) list.AddRange(a.Select(x => Str(x) ?? ""));
		if (Str(node["say"]) is { } say) list.Add(say);
		return list;
	}
}

/// <summary>One character's dialogue file, edited in place as a JSON tree so unknown fields survive.</summary>
public sealed class DialogueDocument
{
	public string FilePath { get; private set; }
	public JsonObject Root { get; private set; } = new();
	public Dictionary<string, Point> Layout { get; private set; } = new();
	HouseJson.StyleHints _style = new();
	public bool Dirty { get; private set; }
	public DateTime LoadedWriteTime { get; private set; }
	/// <summary>Disk version the user chose to keep their own edits over; not asked about again.</summary>
	public DateTime IgnoredDiskTime { get; set; }

	/// <summary>Raised after any edit, undo, redo or reload.</summary>
	public event Action? Changed;

	readonly Stack<(string json, Dictionary<string, Point> layout, string label)> _undo = new();
	readonly Stack<(string json, Dictionary<string, Point> layout, string label)> _redo = new();

	/// <summary>Layout key for the "Start" (entries) box.</summary>
	public const string StartKey = "@start";

	public DialogueDocument(string path)
	{
		FilePath = path;
	}

	public string Id => (Dialogue.Str(Root["id"]) ?? System.IO.Path.GetFileNameWithoutExtension(FilePath)).ToLowerInvariant();
	public string Name => Dialogue.Str(Root["name"]) is { Length: > 0 } n ? n : Id;
	public string FileName => System.IO.Path.GetFileName(FilePath);

	public JsonObject Nodes => Child(Root, "nodes", () => new JsonObject());
	public JsonArray Entries => Child(Root, "entries", () => new JsonArray());
	public JsonObject EndingCards => Child(Root, "endings", () => new JsonObject());

	public JsonObject? Node(string? id) => id != null && Root["nodes"] is JsonObject n && n[id] is JsonObject o ? o : null;
	public IEnumerable<string> NodeIds => Root["nodes"] is JsonObject n ? n.Select(kv => kv.Key) : Enumerable.Empty<string>();

	static T Child<T>(JsonObject parent, string key, Func<T> make) where T : JsonNode
	{
		if (parent[key] is T t) return t;
		var created = make();
		parent[key] = created;
		return created;
	}

	string LayoutPath => System.IO.Path.Combine(System.IO.Path.GetDirectoryName(FilePath)!, ".storywriter",
		System.IO.Path.GetFileNameWithoutExtension(FilePath) + ".layout.json");

	// ---------------------------------------------------------------- IO

	public static DialogueDocument Load(string path)
	{
		var d = new DialogueDocument(path);
		d.Reload();
		return d;
	}

	/// <summary>A new file that only exists in memory until the user saves it.</summary>
	public static DialogueDocument CreateUnsaved(string path, JsonObject root)
	{
		var d = new DialogueDocument(path) { Root = root, Dirty = true };
		return d;
	}

	public void Reload()
	{
		var text = File.ReadAllText(FilePath);
		Root = HouseJson.Parse(text) as JsonObject ?? new JsonObject();
		_style = HouseJson.ScanStyle(text);
		LoadedWriteTime = File.GetLastWriteTimeUtc(FilePath);
		Layout = new();
		try
		{
			if (File.Exists(LayoutPath) && HouseJson.Parse(File.ReadAllText(LayoutPath)) is JsonObject lo && lo["nodes"] is JsonObject ln)
			{
				foreach (var (k, v) in ln)
				{
					if (v is JsonArray a && a.Count >= 2) Layout[k] = new Point(Dialogue.Num(a[0]), Dialogue.Num(a[1]));
				}
			}
		}
		catch
		{
			// A broken layout file only costs us the positions.
		}
		_undo.Clear();
		_redo.Clear();
		Dirty = ClearBrokenLinks() > 0;
		Changed?.Invoke();
	}

	public void Save()
	{
		File.WriteAllText(FilePath, SerializedText());
		SaveLayout();
		LoadedWriteTime = File.GetLastWriteTimeUtc(FilePath);
		Dirty = false;
		Changed?.Invoke();
	}

	void SaveLayout()
	{
		var nodes = new JsonObject();
		if (Layout.TryGetValue(StartKey, out var sp)) nodes[StartKey] = new JsonArray((int)Math.Round(sp.X), (int)Math.Round(sp.Y));
		foreach (var id in NodeIds)
		{
			if (Layout.TryGetValue(id, out var p)) nodes[id] = new JsonArray((int)Math.Round(p.X), (int)Math.Round(p.Y));
		}
		Directory.CreateDirectory(System.IO.Path.GetDirectoryName(LayoutPath)!);
		File.WriteAllText(LayoutPath, HouseJson.Serialize(new JsonObject { ["nodes"] = nodes }));
	}

	public string SerializedText() => HouseJson.Serialize(Root, _style);

	// ---------------------------------------------------------------- Edits / undo

	public bool CanUndo => _undo.Count > 0;
	public bool CanRedo => _redo.Count > 0;
	public string? UndoLabel => _undo.Count > 0 ? _undo.Peek().label : null;

	/// <summary>Every change goes through here so it can be undone.</summary>
	public void Edit(string label, Action change)
	{
		_undo.Push((Root.ToJsonString(), new Dictionary<string, Point>(Layout), label));
		if (_undo.Count > 200) TrimUndo();
		_redo.Clear();
		change();
		ClearBrokenLinks();
		Dirty = true;
		Changed?.Invoke();
	}

	/// <summary>Moving nodes: undoable, but consecutive moves of a drag are a single step.</summary>
	public void BeginMove() => _undo.Push((Root.ToJsonString(), new Dictionary<string, Point>(Layout), "Move"));

	public void MoveNode(string id, Point p)
	{
		Layout[id] = p;
		Dirty = true;
	}

	public void EndMove() => Changed?.Invoke();

	void TrimUndo()
	{
		var keep = _undo.Take(150).Reverse().ToList();
		_undo.Clear();
		foreach (var k in keep) _undo.Push(k);
	}

	public void Undo() => Swap(_undo, _redo);
	public void Redo() => Swap(_redo, _undo);

	void Swap(Stack<(string, Dictionary<string, Point>, string)> from, Stack<(string, Dictionary<string, Point>, string)> to)
	{
		if (from.Count == 0) return;
		var (json, layout, label) = from.Pop();
		to.Push((Root.ToJsonString(), new Dictionary<string, Point>(Layout), label));
		Root = HouseJson.Parse(json) as JsonObject ?? new JsonObject();
		Layout = layout;
		Dirty = true;
		Changed?.Invoke();
	}

	// ---------------------------------------------------------------- Graph queries

	public List<DialogueLink> Links()
	{
		var list = new List<DialogueLink>();
		int ei = 0;
		foreach (var e in Entries.OfType<JsonObject>())
		{
			var target = Dialogue.Str(e["node"]);
			if (!string.IsNullOrEmpty(target))
				list.Add(new DialogueLink(LinkKind.Entry, null, target, Dialogue.Str(e["if"]), $"entry {ei + 1}", null, ei, null));
			ei++;
		}
		foreach (var (id, n) in Nodes)
		{
			if (n is not JsonObject node) continue;
			if (node["topics"] is JsonObject topics)
			{
				foreach (var (key, t) in topics)
				{
					string? target = Dialogue.Str(t), cond = null;
					JsonObject? fx = null;
					if (t is JsonObject to)
					{
						target = Dialogue.Str(to["goto"]);
						cond = Dialogue.Str(to["if"]);
						fx = to["do"] as JsonObject;
					}
					if (!string.IsNullOrEmpty(target))
						list.Add(new DialogueLink(LinkKind.Topic, id, target, cond, "[" + Dialogue.TopicLabel(node, key) + "]", fx, 0, key));
				}
			}
			if (node["choices"] is JsonArray choices)
			{
				for (int i = 0; i < choices.Count; i++)
				{
					if (choices[i] is not JsonObject c) continue;
					var target = Dialogue.Str(c["goto"]);
					if (!string.IsNullOrEmpty(target))
						list.Add(new DialogueLink(LinkKind.Choice, id, target, Dialogue.Str(c["if"]), Dialogue.Str(c["text"]) ?? "", c["do"] as JsonObject, i, null));
				}
			}
			var g = Dialogue.Str(node["goto"]);
			if (!string.IsNullOrEmpty(g))
				list.Add(new DialogueLink(LinkKind.Goto, id, g, null, "", null, 0, null));
		}
		return list;
	}

	/// <summary>
	/// Hypertext nodes are only reached by clicking a highlighted [word]. They play as full nodes today,
	/// but are drawn differently because they'll become tangents rather than story flow.
	/// </summary>
	public Dictionary<string, NodeKind> NodeKinds(List<DialogueLink>? links = null)
	{
		links ??= Links();
		var viaTopic = links.Where(l => l.Kind == LinkKind.Topic).Select(l => l.Target).ToHashSet();
		var viaStory = links.Where(l => l.Kind != LinkKind.Topic).Select(l => l.Target).ToHashSet();
		var kinds = new Dictionary<string, NodeKind>();
		foreach (var (id, n) in Nodes)
		{
			if (n is JsonObject o && !string.IsNullOrEmpty(Dialogue.Str(o["ending"]))) kinds[id] = NodeKind.Ending;
			else if (viaTopic.Contains(id) && !viaStory.Contains(id)) kinds[id] = NodeKind.Hypertext;
			else kinds[id] = NodeKind.Story;
		}
		return kinds;
	}

	public string UniqueNodeId(string baseId)
	{
		baseId = Regex.Replace(baseId.Trim().ToLowerInvariant(), @"[^a-z0-9_]+", "_").Trim('_');
		if (baseId.Length == 0) baseId = "node";
		if (Node(baseId) == null) return baseId;
		for (int i = 2; ; i++)
		{
			if (Node($"{baseId}_{i}") == null) return $"{baseId}_{i}";
		}
	}

	/// <summary>Adds a node. Callers wrap this in Edit().</summary>
	public JsonObject AddNode(string id, Point at, string? firstLine = null)
	{
		var node = new JsonObject
		{
			["lines"] = new JsonArray(firstLine ?? "..."),
			["end"] = true,
		};
		InsertNodeSorted(id, node);
		Layout[id] = at;
		return node;
	}

	/// <summary>Keep nodes grouped (v1*, v2*...) so the blank-line grouping on save stays sensible.</summary>
	void InsertNodeSorted(string id, JsonObject node)
	{
		var nodes = Nodes;
		var group = HouseJson.NodeGroup(id);
		var all = nodes.ToList();
		int insertAt = all.FindLastIndex(kv => HouseJson.NodeGroup(kv.Key) == group);
		if (insertAt < 0)
		{
			nodes[id] = node;
			return;
		}
		var after = all.Skip(insertAt + 1).ToList();
		foreach (var (k, _) in after) nodes.Remove(k);
		nodes[id] = node;
		foreach (var (k, v) in after) nodes[k] = v;
	}

	/// <summary>Renames a node and every reference to it (entries, goto, choices, topics). Callers wrap in Edit().</summary>
	public void RenameNode(string oldId, string newId)
	{
		var nodes = Nodes;
		var list = nodes.ToList();
		foreach (var (k, _) in list) nodes.Remove(k);
		foreach (var (k, v) in list) nodes[k == oldId ? newId : k] = v;

		foreach (var e in Entries.OfType<JsonObject>())
			if (Dialogue.Str(e["node"]) == oldId) e["node"] = newId;
		foreach (var (_, n) in nodes)
		{
			if (n is not JsonObject o) continue;
			if (Dialogue.Str(o["goto"]) == oldId) o["goto"] = newId;
			if (o["choices"] is JsonArray cs)
				foreach (var c in cs.OfType<JsonObject>())
					if (Dialogue.Str(c["goto"]) == oldId) c["goto"] = newId;
			if (o["topics"] is JsonObject ts)
			{
				foreach (var (k, t) in ts.ToList())
				{
					if (Dialogue.Str(t) == oldId) ts[k] = newId;
					else if (t is JsonObject to && Dialogue.Str(to["goto"]) == oldId) to["goto"] = newId;
				}
			}
		}
		if (Layout.Remove(oldId, out var p)) Layout[newId] = p;
	}

	public int CountReferences(string id) => Links().Count(l => l.Target == id && l.Source != id);

	public void DeleteNode(string id)
	{
		Nodes.Remove(id);
		Layout.Remove(id);
	}

	/// <summary>Connect from -> to the way Twine would: goto when the node has no outgoing links yet, otherwise a new choice.</summary>
	public void Connect(string from, string to, bool asTopic = false)
	{
		var node = Node(from);
		if (node == null) return;
		if (asTopic)
		{
			var topics = node["topics"] as JsonObject ?? new JsonObject();
			node["topics"] = topics;
			var key = UniqueTopicKey(topics, to);
			topics[key] = to;
			if (node["lines"] is JsonArray lines && lines.Count > 0)
				lines[^1] = (Dialogue.Str(lines[^1]) ?? "") + $" [{key}]";
			return;
		}
		var hasChoices = node["choices"] is JsonArray { Count: > 0 };
		var hasGoto = !string.IsNullOrEmpty(Dialogue.Str(node["goto"]));
		if (!hasChoices && !hasGoto)
		{
			node["goto"] = to;
			node.Remove("end");
			return;
		}
		var choices = node["choices"] as JsonArray ?? new JsonArray();
		if (!hasChoices)
		{
			// Turn the existing goto into the first choice so both stay reachable.
			choices.Add(new JsonObject { ["text"] = "Continue", ["goto"] = Dialogue.Str(node["goto"]) });
			node.Remove("goto");
		}
		node["choices"] = choices;
		choices.Add(new JsonObject { ["text"] = "...", ["goto"] = to });
		node.Remove("end");
	}

	static string UniqueTopicKey(JsonObject topics, string target)
	{
		var b = target.Split('_').Last();
		var k = b;
		for (int i = 2; topics.ContainsKey(k); i++) k = b + i;
		return k;
	}

	/// <summary>Drops every link whose target node doesn't exist. Returns how many were cleared.</summary>
	public int ClearBrokenLinks()
	{
		int cleared = 0;
		bool Missing(string? t) => !string.IsNullOrEmpty(t) && Node(t) == null;
		if (Root["entries"] is JsonArray entries)
		{
			for (int i = entries.Count - 1; i >= 0; i--)
			{
				if (entries[i] is JsonObject e && Missing(Dialogue.Str(e["node"])))
				{
					entries.RemoveAt(i);
					cleared++;
				}
			}
		}
		if (Root["nodes"] is not JsonObject nodes) return cleared;
		foreach (var (_, n) in nodes)
		{
			if (n is not JsonObject node) continue;
			if (Missing(Dialogue.Str(node["goto"])))
			{
				node.Remove("goto");
				if (node["choices"] is not JsonArray { Count: > 0 } && string.IsNullOrEmpty(Dialogue.Str(node["ending"]))) node["end"] = true;
				cleared++;
			}
			if (node["choices"] is JsonArray cs)
				foreach (var c in cs.OfType<JsonObject>())
					if (Missing(Dialogue.Str(c["goto"])))
					{
						c.Remove("goto");
						cleared++;
					}
			if (node["topics"] is JsonObject ts)
			{
				foreach (var (k, t) in ts.ToList())
				{
					if (t is JsonObject to)
					{
						if (Missing(Dialogue.Str(to["goto"]))) { to["goto"] = ""; cleared++; }
					}
					else if (Missing(Dialogue.Str(t))) { ts[k] = ""; cleared++; }
				}
			}
		}
		return cleared;
	}

	/// <summary>Points an existing choice / goto / topic at another node, or clears it (target null). Callers wrap in Edit().</summary>
	public void SetTarget(string nodeId, LinkKind kind, int index, string? topicKey, string? target)
	{
		var node = Node(nodeId);
		if (node == null) return;
		switch (kind)
		{
			case LinkKind.Choice when node["choices"] is JsonArray cs && index < cs.Count && cs[index] is JsonObject c:
				if (target == null) c.Remove("goto");
				else c["goto"] = target;
				break;
			case LinkKind.Goto:
				if (target == null)
				{
					node.Remove("goto");
					if (node["choices"] is not JsonArray { Count: > 0 } && string.IsNullOrEmpty(Dialogue.Str(node["ending"]))) node["end"] = true;
				}
				else
				{
					node["goto"] = target;
					node.Remove("end");
				}
				break;
			case LinkKind.Topic when node["topics"] is JsonObject ts && topicKey != null:
				if (ts[topicKey] is JsonObject to) to["goto"] = target ?? "";
				else ts[topicKey] = target ?? "";
				break;
		}
	}

	/// <summary>Removes one link (the arrow, not the target node).</summary>
	public void RemoveLink(DialogueLink l)
	{
		switch (l.Kind)
		{
			case LinkKind.Entry:
				if (l.Index < Entries.Count) Entries.RemoveAt(l.Index);
				break;
			case LinkKind.Goto:
				Node(l.Source)?.Remove("goto");
				break;
			case LinkKind.Choice:
				if (Node(l.Source)?["choices"] is JsonArray cs && l.Index < cs.Count) cs.RemoveAt(l.Index);
				break;
			case LinkKind.Topic:
				if (Node(l.Source)?["topics"] is JsonObject ts && l.TopicKey != null) ts.Remove(l.TopicKey);
				break;
		}
	}
}
