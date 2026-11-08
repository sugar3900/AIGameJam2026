using System.Text.Json.Nodes;
using StoryWriter.Model;

namespace StoryWriter.Runtime;

/// <summary>Mirror of FHunkProgress in the save game.</summary>
public sealed class HunkProgress
{
	public int Romance, Friendship, Friction, Visits;
	public bool Met, Fixed;
	public string Ending = "";
	public HashSet<string> Seen = new();

	public HunkProgress Clone() => new()
	{
		Romance = Romance, Friendship = Friendship, Friction = Friction, Visits = Visits,
		Met = Met, Fixed = Fixed, Ending = Ending, Seen = new HashSet<string>(Seen),
	};
}

/// <summary>Everything the game would keep in its save file, for previews.</summary>
public sealed class PreviewState
{
	public Dictionary<string, HunkProgress> Hunks { get; } = new();
	public SortedDictionary<string, int> Flags { get; } = new();
	public string PlayerName = "Rosie";

	public event Action? Changed;
	public void NotifyChanged() => Changed?.Invoke();

	public HunkProgress Hunk(string id)
	{
		if (!Hunks.TryGetValue(id, out var p)) Hunks[id] = p = new HunkProgress();
		return p;
	}

	public void Reset()
	{
		Hunks.Clear();
		Flags.Clear();
		Changed?.Invoke();
	}

	public int CountFixed() => Hunks.Values.Count(h => h.Fixed);

	/// <summary>Port of UFixHimDialogueSubsystem::ResolveVariable.</summary>
	public int Resolve(string hunkId, string identifier)
	{
		int dot = identifier.IndexOf('.');
		string scope = dot >= 0 ? identifier[..dot] : hunkId;
		string name = dot >= 0 ? identifier[(dot + 1)..] : identifier;
		if (scope == "flag") return Flags.GetValueOrDefault(name);
		if (scope == "seen") return Hunks.TryGetValue(hunkId, out var sp) && sp.Seen.Contains(name) ? 1 : 0;
		if (name == "fixedcount" || identifier == "fixedcount") return CountFixed();
		if (!Hunks.TryGetValue(scope, out var p)) return 0;
		return name switch
		{
			"romance" => p.Romance,
			"friendship" => p.Friendship,
			"friction" => p.Friction,
			"visits" => p.Visits,
			"met" => p.Met ? 1 : 0,
			"fixed" => p.Fixed ? 1 : 0,
			_ when name.StartsWith("ending_") => p.Ending == name[7..] ? 1 : 0,
			_ => 0,
		};
	}

	public bool IsTrue(string hunkId, string? condition) => Condition.IsTrue(condition, id => Resolve(hunkId, id));

	/// <summary>Port of ResolveAutoEnding: ties fall on the friendship track.</summary>
	public string ResolveAutoEnding(string hunkId)
	{
		if (!Hunks.TryGetValue(hunkId, out var p)) return "friend_failure";
		bool romantic = p.Romance > p.Friendship;
		bool sour = p.Friction >= Math.Max(p.Romance, p.Friendship);
		return romantic ? (sour ? "romance_failure" : "romance_success") : (sour ? "friend_failure" : "friend_success");
	}

	/// <summary>Applies a "do" object; returns a readable summary like "romance +2".</summary>
	public List<string> Apply(string hunkId, JsonObject? effects)
	{
		var applied = new List<string>();
		if (effects == null) return applied;
		foreach (var (key, v) in effects)
		{
			int val = Dialogue.Num(v);
			var k = key.ToLowerInvariant();
			int dot = k.IndexOf('.');
			string scope = dot >= 0 ? k[..dot] : hunkId;
			string name = dot >= 0 ? k[(dot + 1)..] : k;
			if (scope == "flag")
			{
				Flags[name] = Flags.GetValueOrDefault(name) + val;
			}
			else
			{
				if (val == 0) continue;
				var p = Hunk(scope);
				switch (name)
				{
					case "romance": p.Romance += val; break;
					case "friendship": p.Friendship += val; break;
					case "friction": p.Friction += val; break;
					default: applied.Add($"unknown effect '{key}'"); continue;
				}
			}
			applied.Add($"{key} {(val >= 0 ? "+" : "")}{val}");
		}
		if (applied.Count > 0) Changed?.Invoke();
		return applied;
	}

	public PreviewState Clone()
	{
		var s = new PreviewState { PlayerName = PlayerName };
		foreach (var (k, v) in Hunks) s.Hunks[k] = v.Clone();
		foreach (var (k, v) in Flags) s.Flags[k] = v;
		return s;
	}

	public void CopyFrom(PreviewState other)
	{
		Hunks.Clear();
		Flags.Clear();
		foreach (var (k, v) in other.Hunks) Hunks[k] = v.Clone();
		foreach (var (k, v) in other.Flags) Flags[k] = v;
		PlayerName = other.PlayerName;
		Changed?.Invoke();
	}
}

public sealed record ChoiceView(int Index, string Text, bool Visible, string? Condition, JsonObject? Effects, string? Goto);

public sealed class DialogueView
{
	public string HunkId = "", HunkName = "", NodeId = "";
	public int LineIndex, LineCount;
	public Speaker Speaker;
	/// <summary>Substituted text with [topic] markup still in place.</summary>
	public string Text = "";
	public List<ChoiceView> Choices = new();
	public HashSet<string> ActiveTopics = new();
	public string Fx = "", FxText = "";
	public bool IsLastLine, WillEnd;
	/// <summary>Re-presenting a node already printed (back from a hypertext tangent, or a refresh): don't print its line again.</summary>
	public bool IsReturn;
	/// <summary>Reading a hypertext node: it is a dead end that returns to the node it was opened from.</summary>
	public bool InTangent;
	public IEnumerable<ChoiceView> VisibleChoices => Choices.Where(c => c.Visible);
}

/// <summary>Port of UFixHimDialogueSubsystem's conversation flow (StartConversation / Advance / Choose / ClickTopic).</summary>
public sealed class DialogueRunner
{
	readonly Func<string, DialogueDocument?> _find;
	public PreviewState State { get; }

	public string? ActiveHunkId { get; private set; }
	public string? ActiveNodeId { get; private set; }
	public DialogueView? View { get; private set; }
	public bool IsActive => ActiveHunkId != null;
	string _pendingEnding = "";
	int _lineIndex, _jumpsWithoutLines;
	/// <summary>Nodes (and the line) we left to read a hypertext node; the top is where "Back" returns to.</summary>
	readonly Stack<(string node, int line)> _tangents = new();
	bool InTangent => _tangents.Count > 0;

	public event Action<DialogueView>? ViewChanged;
	public event Action<string, string>? NodeEntered;              // hunk, node
	public event Action<string, List<string>>? EffectsApplied;      // hunk, summary
	public event Action<string, string, string?>? Warning;          // hunk, node, message
	public event Action<string, string>? Ended;                     // hunk, ending ("" if none)

	public DialogueRunner(PreviewState state, Func<string, DialogueDocument?> find)
	{
		State = state;
		_find = find;
	}

	DialogueDocument? Doc => ActiveHunkId != null ? _find(ActiveHunkId) : null;
	JsonObject? CurrentNode => Doc?.Node(ActiveNodeId);

	/// <summary>Picks the start node from "entries" like clicking the fixture in game. Returns the node or null.</summary>
	public string? PickEntry(string hunkId)
	{
		var doc = _find(hunkId);
		if (doc == null) return null;
		foreach (var e in doc.Entries.OfType<JsonObject>())
		{
			if (State.IsTrue(hunkId, Dialogue.Str(e["if"])))
			{
				var n = Dialogue.Str(e["node"]);
				return doc.Node(n) != null ? n : null;
			}
		}
		return null;
	}

	public bool Start(string hunkId, string? nodeId = null)
	{
		Abort();
		var doc = _find(hunkId);
		nodeId ??= PickEntry(hunkId);
		if (doc == null || nodeId == null || doc.Node(nodeId) == null) return false;
		ActiveHunkId = hunkId;
		_pendingEnding = "";
		_jumpsWithoutLines = 0;
		_tangents.Clear();
		State.Hunk(hunkId).Met = true;
		EnterNode(nodeId);
		return true;
	}

	void EnterNode(string nodeId)
	{
		var node = Doc?.Node(nodeId);
		if (node == null)
		{
			Warning?.Invoke(ActiveHunkId!, nodeId, $"missing node '{nodeId}', ending conversation");
			Finish();
			return;
		}
		ActiveNodeId = nodeId;
		_lineIndex = 0;
		State.Hunk(ActiveHunkId!).Seen.Add(nodeId);
		NodeEntered?.Invoke(ActiveHunkId!, nodeId);
		var fx = State.Apply(ActiveHunkId!, node["do"] as JsonObject);
		if (fx.Count > 0) EffectsApplied?.Invoke(ActiveHunkId!, fx);

		var ending = Dialogue.Str(node["ending"]);
		if (!string.IsNullOrEmpty(ending))
			_pendingEnding = ending == "auto" ? State.ResolveAutoEnding(ActiveHunkId!) : ending;

		if (Dialogue.Lines(node).Count == 0)
		{
			if (InTangent)
			{
				ReturnFromTangent();
				return;
			}
			if (++_jumpsWithoutLines > 32)
			{
				Warning?.Invoke(ActiveHunkId!, nodeId, "goto loop");
				Finish();
				return;
			}
			var g = Dialogue.Str(node["goto"]);
			if (!string.IsNullOrEmpty(g)) EnterNode(g);
			else Finish();
			return;
		}
		_jumpsWithoutLines = 0;
		Rebuild();
	}

	public void Advance()
	{
		var node = CurrentNode;
		if (!IsActive) return;
		if (node == null)
		{
			Finish();
			return;
		}
		var lines = Dialogue.Lines(node);
		if (_lineIndex < lines.Count - 1)
		{
			_lineIndex++;
			Rebuild();
			return;
		}
		if (InTangent)
		{
			ReturnFromTangent();
			return;
		}
		if (VisibleChoiceIndices(node).Count > 0) return;
		var g = Dialogue.Str(node["goto"]);
		if (!string.IsNullOrEmpty(g) && !IsEnd(node))
		{
			EnterNode(g);
			return;
		}
		Finish();
	}

	/// <summary>Hypertext nodes are dead ends: after their text, go back to the node they were opened from.</summary>
	void ReturnFromTangent()
	{
		var (node, line) = _tangents.Pop();
		ActiveNodeId = node;
		_lineIndex = line;
		NodeEntered?.Invoke(ActiveHunkId!, node);
		Rebuild(isReturn: true);
	}

	static bool IsEnd(JsonObject node) => Dialogue.Bool(node["end"]) || !string.IsNullOrEmpty(Dialogue.Str(node["ending"]));

	/// <summary>Choose by index into node.choices (not the visible index), so forced picks of hidden choices work too.</summary>
	public void ChooseRaw(int rawIndex)
	{
		var node = CurrentNode;
		if (node?["choices"] is not JsonArray cs || rawIndex < 0 || rawIndex >= cs.Count || cs[rawIndex] is not JsonObject c) return;
		var fx = State.Apply(ActiveHunkId!, c["do"] as JsonObject);
		if (fx.Count > 0) EffectsApplied?.Invoke(ActiveHunkId!, fx);
		var g = Dialogue.Str(c["goto"]);
		if (string.IsNullOrEmpty(g)) Finish();
		else EnterNode(g);
	}

	public void ClickTopic(string topicId)
	{
		var node = CurrentNode;
		if (node?["topics"] is not JsonObject ts) return;
		var entry = ts.FirstOrDefault(kv => kv.Key.Equals(topicId, StringComparison.OrdinalIgnoreCase));
		if (entry.Key == null) return;
		string? target = Dialogue.Str(entry.Value), cond = null;
		JsonObject? effects = null;
		if (entry.Value is JsonObject to)
		{
			target = Dialogue.Str(to["goto"]);
			cond = Dialogue.Str(to["if"]);
			effects = to["do"] as JsonObject;
		}
		if (!State.IsTrue(ActiveHunkId!, cond)) return;
		var fx = State.Apply(ActiveHunkId!, effects);
		if (fx.Count > 0) EffectsApplied?.Invoke(ActiveHunkId!, fx);
		target ??= "";
		if (Doc is { } doc && doc.Node(target) != null && (InTangent || doc.NodeKinds().GetValueOrDefault(target) == NodeKind.Hypertext))
			_tangents.Push((ActiveNodeId!, _lineIndex));
		EnterNode(target);
	}

	public void Abort()
	{
		ActiveHunkId = null;
		ActiveNodeId = null;
		_pendingEnding = "";
		_tangents.Clear();
		View = null;
	}

	void Finish()
	{
		if (!IsActive) return;
		var hunk = ActiveHunkId!;
		var ending = _pendingEnding;
		var p = State.Hunk(hunk);
		p.Visits++;
		if (!string.IsNullOrEmpty(ending))
		{
			p.Ending = ending;
			p.Fixed = true;
		}
		Abort();
		State.NotifyChanged();
		Ended?.Invoke(hunk, ending);
	}

	List<int> VisibleChoiceIndices(JsonObject node)
	{
		var list = new List<int>();
		if (InTangent || _lineIndex < Dialogue.Lines(node).Count - 1 || node["choices"] is not JsonArray cs) return list;
		for (int i = 0; i < cs.Count; i++)
			if (cs[i] is JsonObject c && State.IsTrue(ActiveHunkId!, Dialogue.Str(c["if"]))) list.Add(i);
		return list;
	}

	public string Substitute(string s)
	{
		s = s.Replace("{player}", State.PlayerName);
		if (Doc is { } d) s = s.Replace("{name}", d.Name);
		return s;
	}

	/// <summary>Re-reads the current node (e.g. after it was edited mid-preview).</summary>
	public void Refresh()
	{
		if (IsActive && CurrentNode != null) Rebuild(isReturn: true);
	}

	void Rebuild(bool isReturn = false)
	{
		var node = CurrentNode;
		var doc = Doc;
		if (node == null || doc == null) return;
		var lines = Dialogue.Lines(node);
		if (_lineIndex >= lines.Count) _lineIndex = Math.Max(0, lines.Count - 1);
		if (lines.Count == 0) return;
		var (speaker, text) = Dialogue.ParseLine(lines[_lineIndex]);
		var v = new DialogueView
		{
			HunkId = ActiveHunkId!,
			HunkName = doc.Name,
			NodeId = ActiveNodeId!,
			LineIndex = _lineIndex,
			LineCount = lines.Count,
			Speaker = speaker,
			Text = Substitute(text),
			IsLastLine = _lineIndex == lines.Count - 1,
			IsReturn = isReturn,
			InTangent = InTangent,
		};
		if (_lineIndex == 0 && !isReturn)
		{
			v.Fx = Dialogue.Str(node["fx"]) ?? "";
			v.FxText = Substitute(Dialogue.Str(node["fxText"]) ?? "");
		}
		var visible = VisibleChoiceIndices(node);
		if (v.IsLastLine && !InTangent && node["choices"] is JsonArray cs)
		{
			for (int i = 0; i < cs.Count; i++)
			{
				if (cs[i] is not JsonObject c) continue;
				v.Choices.Add(new ChoiceView(i, Substitute(Dialogue.Str(c["text"]) ?? ""), visible.Contains(i),
					Dialogue.Str(c["if"]), c["do"] as JsonObject, Dialogue.Str(c["goto"])));
			}
		}
		if (node["topics"] is JsonObject ts)
		{
			foreach (var (k, t) in ts)
			{
				var cond = t is JsonObject to ? Dialogue.Str(to["if"]) : null;
				if (State.IsTrue(ActiveHunkId!, cond)) v.ActiveTopics.Add(k.ToLowerInvariant());
			}
		}
		v.WillEnd = v.IsLastLine && !InTangent && visible.Count == 0 && (IsEnd(node) || string.IsNullOrEmpty(Dialogue.Str(node["goto"])));
		View = v;
		ViewChanged?.Invoke(v);
	}
}
