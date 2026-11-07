using System.Text.Json.Nodes;
using StoryWriter.Runtime;

namespace StoryWriter.Model;

public sealed record Issue(bool IsError, string DocId, string? NodeId, string Message)
{
	public override string ToString() => $"{(IsError ? "error" : "warn")}  {DocId}{(NodeId != null ? " / " + NodeId : "")}: {Message}";
}

/// <summary>Same rules as Tools/validate_dialogue.py (and the game's load-time checks).</summary>
public static class Validator
{
	public static List<Issue> Validate(DialogueDocument d, IReadOnlyCollection<string> hunkIds)
	{
		var issues = new List<Issue>();
		var id = d.Id;
		void Err(string? node, string msg) => issues.Add(new Issue(true, id, node, msg));
		void Warn(string? node, string msg) => issues.Add(new Issue(false, id, node, msg));
		void Ref(string? node, string where, string? target)
		{
			if (!string.IsNullOrEmpty(target) && d.Node(target) == null) Err(node, $"{where} -> missing node '{target}'");
		}
		void Cond(string? node, string where, string? c)
		{
			if (Condition.Check(c) is { } e) Err(node, $"{where} condition '{c}': {e}");
		}
		void Effects(string? node, string where, JsonNode? doNode)
		{
			if (doNode is not JsonObject o) return;
			foreach (var (k, _) in o)
			{
				int dot = k.LastIndexOf('.');
				var scope = dot >= 0 ? k[..dot] : "";
				var name = dot >= 0 ? k[(dot + 1)..] : k;
				if (scope == "flag") continue;
				if (!Dialogue.Stats.Contains(name)) Err(node, $"{where}: unknown effect '{k}'");
				if (scope.Length > 0 && !hunkIds.Contains(scope)) Err(node, $"{where}: unknown hunk '{scope}' in effect '{k}'");
			}
		}

		if (d.Entries.Count == 0) Err(null, "no entries");
		foreach (var e in d.Entries.OfType<JsonObject>())
		{
			Ref(Dialogue.Str(e["node"]), "entry", Dialogue.Str(e["node"]));
			Cond(Dialogue.Str(e["node"]), "entry", Dialogue.Str(e["if"]));
		}

		foreach (var (nid, n) in d.Nodes)
		{
			if (n is not JsonObject node) { Err(nid, "not an object"); continue; }
			var lines = Dialogue.Lines(node);
			if (lines.Count == 0) Err(nid, "no lines");
			var choices = node["choices"] as JsonArray;
			if ((choices == null || choices.Count == 0) && string.IsNullOrEmpty(Dialogue.Str(node["goto"])) && !Dialogue.Bool(node["end"]) && string.IsNullOrEmpty(Dialogue.Str(node["ending"])))
				Err(nid, "dead end (no choices, goto, end or ending)");
			Ref(nid, "goto", Dialogue.Str(node["goto"]));
			Effects(nid, "do", node["do"]);
			var ending = Dialogue.Str(node["ending"]);
			if (!string.IsNullOrEmpty(ending) && ending != "auto" && d.EndingCards[ending] == null)
				Err(nid, $"ending '{ending}' has no card");
			if (Dialogue.Str(node["fx"]) is { Length: > 0 } fx && !Dialogue.FxKinds.Contains(fx))
				Warn(nid, $"unknown fx '{fx}'");

			var topics = new Dictionary<string, JsonNode?>();
			if (node["topics"] is JsonObject to)
				foreach (var (k, v) in to) topics[k.ToLowerInvariant()] = v;
			foreach (var line in lines)
				foreach (var t in Dialogue.Topics(line))
					if (!topics.ContainsKey(t.TopicId)) Err(nid, $"[{t.TopicId}] has no topic entry");
			foreach (var (k, v) in topics)
			{
				var target = v is JsonObject vo ? Dialogue.Str(vo["goto"]) : Dialogue.Str(v);
				Ref(nid, $"topic {k}", target);
				if (v is JsonObject vo2)
				{
					Effects(nid, $"topic {k}", vo2["do"]);
					Cond(nid, $"topic {k}", Dialogue.Str(vo2["if"]));
				}
				if (!lines.Any(l => Dialogue.Topics(l).Any(t => t.TopicId == k)))
					Warn(nid, $"topic '{k}' is never highlighted in a line (unclickable)");
			}
			if (choices != null)
			{
				foreach (var c in choices.OfType<JsonObject>())
				{
					Ref(nid, "choice", Dialogue.Str(c["goto"]));
					Effects(nid, "choice", c["do"]);
					Cond(nid, "choice", Dialogue.Str(c["if"]));
				}
				if (choices.Count > 0 && choices.OfType<JsonObject>().All(c => !string.IsNullOrWhiteSpace(Dialogue.Str(c["if"]))))
					Warn(nid, "every choice is conditional (player could get stuck)");
			}
		}

		// Reachability from entries.
		var seen = new HashSet<string>();
		var stack = new Stack<string>(d.Entries.OfType<JsonObject>().Select(e => Dialogue.Str(e["node"])).Where(x => x != null && d.Node(x) != null)!);
		var links = d.Links().Where(l => l.Source != null).ToLookup(l => l.Source!);
		while (stack.Count > 0)
		{
			var n = stack.Pop();
			if (!seen.Add(n)) continue;
			foreach (var l in links[n])
				if (d.Node(l.Target) != null) stack.Push(l.Target);
		}
		foreach (var nid in d.NodeIds)
			if (!seen.Contains(nid)) Warn(nid, "unreachable from any entry");
		var missing = Dialogue.Endings.Where(e => d.EndingCards[e] == null).ToList();
		if (missing.Count > 0) Warn(null, "missing ending cards: " + string.Join(", ", missing));
		return issues;
	}
}
