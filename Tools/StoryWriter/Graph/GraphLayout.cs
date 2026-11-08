using System.Text.Json.Nodes;
using Avalonia;
using StoryWriter.Model;

namespace StoryWriter.Graph;

/// <summary>
/// Automatic placement: each entry (v1, v2, ... after_*) gets a horizontal lane, nodes are columns by depth from
/// that entry. Only used for nodes that have no saved position.
/// </summary>
public static class GraphLayout
{
	public const double ColumnPitch = 640;
	public const double RowPitch = 150;
	public const double FirstColumnX = 560;

	public static Dictionary<string, Point> Compute(DialogueDocument doc)
	{
		var pos = new Dictionary<string, Point>();
		var links = doc.Links();
		var outgoing = links.Where(l => l.Source != null).ToLookup(l => l.Source!);
		var assigned = new HashSet<string>();
		double laneTop = 0;

		var roots = doc.Entries.OfType<JsonObject>().Select(e => Dialogue.Str(e["node"])).Where(n => n != null && doc.Node(n) != null).Distinct().ToList();
		// Anything unreachable gets its own lane at the bottom.
		var rest = doc.NodeIds.ToList();

		void Lane(string root)
		{
			if (assigned.Contains(root)) return;
			var columns = new List<List<string>>();
			var queue = new Queue<(string id, int depth)>();
			queue.Enqueue((root, 0));
			assigned.Add(root);
			while (queue.Count > 0)
			{
				var (id, depth) = queue.Dequeue();
				while (columns.Count <= depth) columns.Add(new List<string>());
				columns[depth].Add(id);
				foreach (var l in outgoing[id])
				{
					if (doc.Node(l.Target) != null && assigned.Add(l.Target)) queue.Enqueue((l.Target, depth + 1));
				}
			}
			int rows = columns.Max(c => c.Count);
			for (int c = 0; c < columns.Count; c++)
			{
				// Centre short columns in the lane so the lane reads as a flow.
				double offset = (rows - columns[c].Count) * RowPitch / 2;
				for (int r = 0; r < columns[c].Count; r++)
					pos[columns[c][r]] = new Point(FirstColumnX + c * ColumnPitch, laneTop + offset + r * RowPitch);
			}
			laneTop += rows * RowPitch + 70;
		}

		foreach (var r in roots) Lane(r!);
		foreach (var r in rest) Lane(r);
		double startY = roots.Count > 0 && pos.TryGetValue(roots[0]!, out var p0) ? p0.Y : 0;
		pos[DialogueDocument.StartKey] = new Point(40, startY);
		return pos;
	}

	/// <summary>Gives every node that lacks a position one: full layout when none exist, else next to a linked node.</summary>
	public static bool FillMissing(DialogueDocument doc)
	{
		var missing = doc.NodeIds.Where(id => !doc.Layout.ContainsKey(id)).ToList();
		bool startMissing = !doc.Layout.ContainsKey(DialogueDocument.StartKey);
		if (missing.Count == 0 && !startMissing) return false;
		var auto = Compute(doc);
		if (doc.Layout.Count == 0 || missing.Count == doc.Nodes.Count)
		{
			foreach (var (k, v) in auto) doc.Layout[k] = v;
			return true;
		}
		if (startMissing) doc.Layout[DialogueDocument.StartKey] = auto[DialogueDocument.StartKey];
		var links = doc.Links();
		foreach (var id in missing)
		{
			var src = links.FirstOrDefault(l => l.Target == id && l.Source != null && doc.Layout.ContainsKey(l.Source));
			var p = src != null ? doc.Layout[src.Source!] + new Point(ColumnPitch, 0) : auto[id];
			while (doc.Layout.Values.Any(q => Math.Abs(q.X - p.X) < 200 && Math.Abs(q.Y - p.Y) < 120)) p += new Point(0, RowPitch);
			doc.Layout[id] = p;
		}
		return true;
	}
}
