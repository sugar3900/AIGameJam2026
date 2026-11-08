using System.Globalization;
using System.Text.Json.Nodes;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;
using Avalonia.Threading;
using StoryWriter.Model;
using StoryWriter.UI;

namespace StoryWriter.Graph;

/// <summary>
/// Twine-style node graph for one conversation. Conditional links are routed through an amber "if" box placed
/// to the left of the node they flow into, instead of being written on the node itself.
/// </summary>
public sealed class GraphView : Control
{
	public const double NodeW = 240, MinNodeH = 84, HeaderH = 26, PreviewH = 34, RowH = 20, FooterH = 18;
	public const double CondW = 180, CondH = 50, CondGap = 26;
	const double PortR = 6;

	DialogueDocument? _doc;
	List<DialogueLink> _links = new();
	Dictionary<string, NodeKind> _kinds = new();
	HashSet<string> _entryTargets = new();
	readonly Dictionary<string, Rect> _nodeRects = new();
	readonly List<(Rect rect, DialogueLink link)> _condBoxes = new();
	readonly Dictionary<DialogueLink, Point> _ports = new(ReferenceEqualityComparer.Instance);
	readonly Dictionary<string, List<PortRow>> _rows = new();
	static readonly IBrush RowFill = new SolidColorBrush(Color.Parse("#3A3244"));

	/// <summary>One outgoing option drawn inside a node (choice, "next" goto, or hypertext link) with its own link port.</summary>
	sealed class PortRow
	{
		public string NodeId = "";
		public LinkKind Kind;
		public int Index;
		public string? TopicKey;
		public string Text = "";
		public string? Target;
		public DialogueLink? Link;
		public Rect Rect;
		public Point Port;
	}
	Rect _startRect;

	// View transform: screen = world * zoom + pan
	double _zoom = 0.8;
	Vector _pan = new(40, 40);

	public string? SelectedId { get; private set; }
	bool _startSelected;
	public string? PreviewNodeId { get; private set; }
	public HashSet<string> PreviewTrail { get; } = new();
	public Dictionary<string, (int errors, int warnings)> NodeIssues { get; set; } = new();
	/// <summary>When a preview is running: evaluates a condition against its state (null = no preview).</summary>
	public Func<string?, bool?>? EvaluateCondition { get; set; }

	public event Action<string>? EditNodeRequested;
	public event Action? EditConversationRequested;
	public event Action<string?>? PreviewRequested; // null = from start
	public event Action<string?>? SelectionChanged;
	/// <summary>Source of the variable names offered when editing a condition.</summary>
	public Func<IEnumerable<DialogueDocument>>? AllDocs { get; set; }

	// Interaction state
	enum Drag { None, Pan, Move, Connect, Reconnect }
	Drag _drag;
	Point _dragStartScreen, _lastScreen;
	Point _moveOffset;
	string? _dragNode;
	PortRow? _dragRow;
	PortRow? _hoverRow;
bool _moved;
	Point _connectEnd;
	string? _hoverNode;
	bool _connectAsTopic;

	static readonly Typeface Regular = new(FontFamily.Default);
	static readonly Typeface Bold = new(FontFamily.Default, FontStyle.Normal, FontWeight.Bold);
	static readonly Typeface Italic = new(FontFamily.Default, FontStyle.Italic);

	public GraphView()
	{
		Focusable = true;
		ClipToBounds = true;
	}

	public DialogueDocument? Document
	{
		get => _doc;
		set
		{
			if (_doc == value) return;
			if (_doc != null) _doc.Changed -= OnDocChanged;
			_doc = value;
			if (_doc != null) _doc.Changed += OnDocChanged;
			SelectedId = null;
			PreviewNodeId = null;
			PreviewTrail.Clear();
			Rebuild();
			// Frame the new conversation once layout has settled. Never from Render(): changing the view
			// there invalidates the visual mid-render, which Avalonia 12 treats as fatal.
			_fitPending = true;
			Dispatcher.UIThread.Post(ApplyPendingView, DispatcherPriority.Loaded);
			InvalidateVisual();
		}
	}

	void ApplyPendingView()
	{
		if (!_fitPending || Bounds.Width < 10) return; // OnSizeChanged will pick it up
		_fitPending = false;
		InitialView();
	}

	bool _fitPending;

	void OnDocChanged()
	{
		Rebuild();
		if (SelectedId != null && _doc?.Node(SelectedId) == null) Select(null);
		InvalidateVisual();
	}

	public double Zoom => _zoom;

	// ------------------------------------------------------------------ Model -> geometry

	public void Rebuild()
	{
		_nodeRects.Clear();
		_condBoxes.Clear();
		_ports.Clear();
		_rows.Clear();
		if (_doc == null) return;
		GraphLayout.FillMissing(_doc);
		_links = _doc.Links();
		_kinds = _doc.NodeKinds(_links);
		_entryTargets = _links.Where(l => l.Kind == LinkKind.Entry).Select(l => l.Target).ToHashSet();

		var byKey = new Dictionary<(string, LinkKind, string), DialogueLink>();
		foreach (var l in _links.Where(l => l.Source != null))
			byKey.TryAdd((l.Source!, l.Kind, l.Kind == LinkKind.Topic ? l.TopicKey ?? "" : l.Index.ToString()), l);

		foreach (var id in _doc.NodeIds)
		{
			var node = _doc.Node(id)!;
			var rows = new List<PortRow>();
			PortRow Row(LinkKind kind, int index, string? topicKey, string text, JsonObject? fx, string? target)
			{
				var link = byKey.GetValueOrDefault((id, kind, kind == LinkKind.Topic ? topicKey ?? "" : index.ToString()));
				var f = Dialogue.FormatEffectsShort(fx);
				return new PortRow
				{
					NodeId = id, Kind = kind, Index = index, TopicKey = topicKey,
					Text = f.Length > 0 ? text + "  " + f : text,
					Target = string.IsNullOrEmpty(target) ? null : target,
					Link = link,
				};
			}
			if (node["choices"] is JsonArray cs)
				for (int i = 0; i < cs.Count; i++)
					if (cs[i] is JsonObject c)
						rows.Add(Row(LinkKind.Choice, i, null, $"{i + 1}. {Dialogue.Str(c["text"]) ?? ""}", c["do"] as JsonObject, Dialogue.Str(c["goto"])));
			if (!string.IsNullOrEmpty(Dialogue.Str(node["goto"])))
				rows.Add(Row(LinkKind.Goto, 0, null, "→ next", null, Dialogue.Str(node["goto"])));
			if (node["topics"] is JsonObject ts)
				foreach (var (key, t) in ts)
					rows.Add(Row(LinkKind.Topic, 0, key, "[" + key + "]", (t as JsonObject)?["do"] as JsonObject, t is JsonObject to ? Dialogue.Str(to["goto"]) : Dialogue.Str(t)));

			var p = _doc.Layout[id];
			double h = Math.Max(MinNodeH, HeaderH + PreviewH + rows.Count * RowH + 6 + (FooterBits(node).text.Length > 0 ? FooterH : 0));
			var rect = new Rect(p.X, p.Y, NodeW, h);
			_nodeRects[id] = rect;
			for (int i = 0; i < rows.Count; i++)
			{
				rows[i].Rect = new Rect(rect.X + 8, rect.Y + HeaderH + PreviewH + i * RowH, NodeW - 16, RowH - 3);
				rows[i].Port = new Point(rect.Right, rows[i].Rect.Center.Y);
				if (rows[i].Link != null) _ports[rows[i].Link!] = rows[i].Port;
			}
			_rows[id] = rows;
		}

		// START box: one out port per entry, spread down the right edge.
		var entries = _links.Where(l => l.Source == null).ToList();
		var sp = _doc.Layout.GetValueOrDefault(DialogueDocument.StartKey);
		_startRect = new Rect(sp.X, sp.Y, 170, Math.Max(64, 34 + entries.Count * 20));
		double top = _startRect.Top + HeaderH + 4, span = _startRect.Height - HeaderH - 8;
		for (int i = 0; i < entries.Count; i++)
			_ports[entries[i]] = new Point(_startRect.Right, top + span * (i + 0.5) / entries.Count);

		// Condition boxes: stacked to the left of the node the link flows into.
		foreach (var g in _links.Where(l => l.IsConditional && _nodeRects.ContainsKey(l.Target)).GroupBy(l => l.Target))
		{
			var r = _nodeRects[g.Key];
			int i = 0;
			var list = g.ToList();
			double total = list.Count * CondH + (list.Count - 1) * 8;
			double y0 = r.Center.Y - total / 2;
			foreach (var l in list)
				_condBoxes.Add((new Rect(r.Left - CondGap - CondW, y0 + i++ * (CondH + 8), CondW, CondH), l));
		}
	}

	/// <summary>What happens at the end of the node, shown in its footer.</summary>
	static (string text, bool isEnding) FooterBits(JsonObject node)
	{
		var bits = new List<string>();
		var ending = Dialogue.Str(node["ending"]);
		if (!string.IsNullOrEmpty(ending)) bits.Add("ending: " + ending);
		else if (Dialogue.Bool(node["end"])) bits.Add("■ end");
		if (Dialogue.Str(node["fx"]) is { Length: > 0 } fx) bits.Add("fx " + fx);
		if (node["do"] is JsonObject d) bits.Add(Dialogue.FormatEffectsShort(d));
		int lines = Dialogue.Lines(node).Count;
		if (lines > 2) bits.Add($"{lines} lines");
		return (string.Join("  ·  ", bits), !string.IsNullOrEmpty(ending));
	}

	Point ToWorld(Point screen) => new((screen.X - _pan.X) / _zoom, (screen.Y - _pan.Y) / _zoom);
	Point ToScreen(Point world) => new(world.X * _zoom + _pan.X, world.Y * _zoom + _pan.Y);

	Rect ContentBounds()
	{
		var rects = _nodeRects.Values.Concat(_condBoxes.Select(c => c.rect)).Append(_startRect).ToList();
		if (rects.Count == 0) return new Rect(0, 0, 100, 100);
		return rects.Aggregate((a, b) => a.Union(b));
	}

	public void FitToView()
	{
		if (Bounds.Width < 10) { _fitPending = true; return; }
		var b = ContentBounds().Inflate(40);
		_zoom = Math.Clamp(Math.Min(Bounds.Width / b.Width, Bounds.Height / b.Height), 0.15, 1.1);
		_pan = new Vector(Bounds.Width / 2 - b.Center.X * _zoom, Bounds.Height / 2 - b.Center.Y * _zoom);
		InvalidateVisual();
		ZoomChanged?.Invoke(_zoom);
	}

	/// <summary>Opening view: the whole graph if it's readable, otherwise the node a fresh save would start at.</summary>
	public void InitialView()
	{
		if (_doc == null || Bounds.Width < 10) { _fitPending = true; return; }
		var b = ContentBounds().Inflate(40);
		if (Math.Min(Bounds.Width / b.Width, Bounds.Height / b.Height) >= 0.5) { FitToView(); return; }
		var fresh = new Runtime.DialogueRunner(new Runtime.PreviewState(), _ => _doc).PickEntry(_doc.Id);
		_zoom = 0.75;
		if (fresh != null && _nodeRects.TryGetValue(fresh, out var r))
			_pan = new Vector(60 - (r.Left - CondGap - CondW) * _zoom, Bounds.Height / 2 - r.Center.Y * _zoom);
		else
			_pan = new Vector(40 - b.Left * _zoom, 40 - b.Top * _zoom);
		InvalidateVisual();
		ZoomChanged?.Invoke(_zoom);
	}

	public void SetZoom(double z, Point? anchorScreen = null)
	{
		var anchor = anchorScreen ?? new Point(Bounds.Width / 2, Bounds.Height / 2);
		var world = ToWorld(anchor);
		_zoom = Math.Clamp(z, 0.12, 2.5);
		_pan = new Vector(anchor.X - world.X * _zoom, anchor.Y - world.Y * _zoom);
		InvalidateVisual();
		ZoomChanged?.Invoke(_zoom);
	}

	public event Action<double>? ZoomChanged;

	/// <summary>Pans so the node is visible (centres it if it's off-screen).</summary>
	public void Reveal(string id, bool force = false)
	{
		if (!_nodeRects.TryGetValue(id, out var r)) return;
		var tl = ToScreen(r.TopLeft);
		var br = ToScreen(r.BottomRight);
		var view = new Rect(Bounds.Size).Deflate(30);
		if (!force && view.Contains(tl) && view.Contains(br)) return;
		_pan = new Vector(Bounds.Width / 2 - r.Center.X * _zoom, Bounds.Height / 2 - r.Center.Y * _zoom);
		InvalidateVisual();
	}

	public void Select(string? id)
	{
		_startSelected = false;
		if (SelectedId == id) return;
		SelectedId = id;
		SelectionChanged?.Invoke(id);
		InvalidateVisual();
	}

	public void SetPreviewNode(string? id)
	{
		PreviewNodeId = id;
		if (id != null)
		{
			PreviewTrail.Add(id);
			Reveal(id);
		}
		InvalidateVisual();
	}

	public void ClearPreview()
	{
		PreviewNodeId = null;
		PreviewTrail.Clear();
		EvaluateCondition = null;
		InvalidateVisual();
	}

	public void AutoArrange()
	{
		if (_doc == null) return;
		_doc.Edit("Auto-arrange", () =>
		{
			foreach (var (k, v) in GraphLayout.Compute(_doc)) _doc.Layout[k] = v;
		});
		FitToView();
	}

	// ------------------------------------------------------------------ Rendering

	protected override void OnSizeChanged(SizeChangedEventArgs e)
	{
		base.OnSizeChanged(e);
		if (_fitPending && e.NewSize.Width > 10)
			Dispatcher.UIThread.Post(ApplyPendingView, DispatcherPriority.Loaded);
	}

	public override void Render(DrawingContext ctx)
	{
		ctx.FillRectangle(Palette.Canvas, new Rect(Bounds.Size));
		DrawGrid(ctx);
		if (_doc == null)
		{
			DrawText(ctx, "Pick a conversation on the left.", new Point(30, 30), 14, Palette.Muted, Regular, 400);
			return;
		}

		using (ctx.PushTransform(Matrix.CreateScale(_zoom, _zoom) * Matrix.CreateTranslation(_pan.X, _pan.Y)))
		{
			foreach (var l in _links) DrawLink(ctx, l);
			foreach (var (rect, link) in _condBoxes) DrawCondition(ctx, rect, link);
			DrawStart(ctx);
			foreach (var (id, r) in _nodeRects) DrawNode(ctx, id, r);
if (_drag == Drag.Reconnect && _dragRow != null)
{
	// Dropping on empty canvas clears an existing link, so draw that case in red.
	bool drops = _hoverNode == null && _dragRow.Target != null;
	var rpen = new Pen(drops ? Palette.Error : Palette.Selection, 2, drops || _dragRow.Kind == LinkKind.Topic ? new DashStyle(new double[] { 4, 3 }, 0) : null);
	ctx.DrawGeometry(null, rpen, Curve(_dragRow.Port, _connectEnd));
	if (_hoverNode != null && _nodeRects.TryGetValue(_hoverNode, out var rhr))
		ctx.DrawRectangle(null, new Pen(Palette.Selection, 2.5), rhr.Inflate(4), 10, 10);
}
if (_drag == Drag.Connect && _dragNode != null && _nodeRects.TryGetValue(_dragNode, out var from))
{
	var p0 = new Point(from.Right, from.Top + HeaderH / 2);
				var pen = new Pen(_connectAsTopic ? Palette.EdgeTopic : Palette.Selection, 2, _connectAsTopic ? new DashStyle(new double[] { 4, 3 }, 0) : null);
				ctx.DrawGeometry(null, pen, Curve(p0, _connectEnd));
				if (_hoverNode != null && _nodeRects.TryGetValue(_hoverNode, out var hr))
					ctx.DrawRectangle(null, new Pen(Palette.Selection, 2.5), hr.Inflate(4), 10, 10);
			}
		}
	}

	void DrawGrid(DrawingContext ctx)
	{
		double step = 40 * _zoom;
		if (step < 12) return;
		double ox = _pan.X % step, oy = _pan.Y % step;
		for (double x = ox; x < Bounds.Width; x += step)
			for (double y = oy; y < Bounds.Height; y += step)
				ctx.FillRectangle(Palette.GridDot, new Rect(x, y, 2, 2));
	}

	static StreamGeometry Curve(Point a, Point b)
	{
		double dx = b.X >= a.X + 20 ? Math.Max(40, (b.X - a.X) * 0.5) : 140 + Math.Abs(b.X - a.X) * 0.15;
		var g = new StreamGeometry();
		using (var c = g.Open())
		{
			c.BeginFigure(a, false);
			c.CubicBezierTo(new Point(a.X + dx, a.Y), new Point(b.X - dx, b.Y), b);
			c.EndFigure(false);
		}
		return g;
	}

	static void Arrow(DrawingContext ctx, Point tip, IBrush brush)
	{
		var g = new StreamGeometry();
		using (var c = g.Open())
		{
			c.BeginFigure(tip, true);
			c.LineTo(new Point(tip.X - 10, tip.Y - 5));
			c.LineTo(new Point(tip.X - 10, tip.Y + 5));
			c.EndFigure(true);
		}
		ctx.DrawGeometry(brush, null, g);
	}

	static IBrush LinkBrush(DialogueLink l) => l.Kind switch
	{
		LinkKind.Entry => Palette.EdgeEntry,
		LinkKind.Topic => Palette.EdgeTopic,
		LinkKind.Choice => Palette.EdgeChoice,
		_ => Palette.EdgeGoto,
	};

	void DrawLink(DrawingContext ctx, DialogueLink l)
	{
		if (!_ports.TryGetValue(l, out var p0)) return;
		var brush = LinkBrush(l);
		bool onTrail = l.Source != null && PreviewTrail.Contains(l.Source) && PreviewTrail.Contains(l.Target);
		var pen = new Pen(brush, onTrail ? 3 : 1.6, l.Kind == LinkKind.Topic ? new DashStyle(new double[] { 5, 3 }, 0) : null);
		if (!_nodeRects.TryGetValue(l.Target, out var target))
		{
			// Broken link: red stub with the missing id.
			var end = p0 + new Point(60, 0);
			ctx.DrawLine(new Pen(Palette.Error, 2, new DashStyle(new double[] { 3, 3 }, 0)), p0, end);
			DrawText(ctx, "? " + l.Target, end + new Point(4, -8), 11, Palette.Error, Bold, 200);
			return;
		}
		var cond = _condBoxes.FirstOrDefault(c => ReferenceEquals(c.link, l));
		if (cond.link != null)
		{
			var a = new Point(cond.rect.Left, cond.rect.Center.Y);
			ctx.DrawGeometry(null, pen, Curve(p0, a));
			Arrow(ctx, a, brush);
			var b = new Point(target.Left, Math.Clamp(cond.rect.Center.Y, target.Top + 14, target.Bottom - 14));
			ctx.DrawGeometry(null, new Pen(Palette.Condition, pen.Thickness, pen.DashStyle), Curve(new Point(cond.rect.Right, cond.rect.Center.Y), b));
			Arrow(ctx, b, Palette.Condition);
		}
		else
		{
			var b = new Point(target.Left, target.Center.Y);
			ctx.DrawGeometry(null, pen, Curve(p0, b));
			Arrow(ctx, b, brush);
		}
		ctx.DrawEllipse(brush, null, p0, 3.5, 3.5);
	}

	void DrawCondition(DrawingContext ctx, Rect r, DialogueLink l)
	{
		bool? result = EvaluateCondition?.Invoke(l.Condition);
		var border = result switch { true => Palette.Start, false => Palette.Error, _ => Palette.Condition };
		ctx.DrawRectangle(Palette.ConditionFill, new Pen(border, 1.5), r, 6, 6);
		var caption = result switch { true => "IF  ✓", false => "IF  ✗", _ => "IF" };
		DrawText(ctx, caption, new Point(r.X + 7, r.Y + 3), 9, border, Bold, CondW - 14);
		var t = Text(l.Condition ?? "", 11.5, Palette.Text, Regular, CondW - 14, 2);
		t.TextAlignment = TextAlignment.Left;
		ctx.DrawText(t, new Point(r.X + 7, r.Y + 16));
	}

	void DrawStart(DrawingContext ctx)
	{
		var r = _startRect;
		ctx.DrawRectangle(new SolidColorBrush(Color.Parse("#1F3A2C")), new Pen(_startSelected ? Palette.Selection : Palette.Start, _startSelected ? 2.5 : 1.5), r, 14, 14);
		DrawText(ctx, "► START", new Point(r.X + 12, r.Y + 7), 12, Palette.Start, Bold, r.Width - 20);
		DrawText(ctx, $"{_doc!.Name} · entries", new Point(r.X + 12, r.Bottom - 20), 10, Palette.Muted, Regular, r.Width - 20);
	}

	void DrawNode(DrawingContext ctx, string id, Rect r)
	{
		var node = _doc!.Node(id)!;
		var kind = _kinds.GetValueOrDefault(id);
		var accent = Palette.ForKind(kind);
		bool selected = id == SelectedId;
		bool current = id == PreviewNodeId;
		double radius = kind == NodeKind.Hypertext ? 16 : 7;

		if (current)
			ctx.DrawRectangle(null, new Pen(new SolidColorBrush(((ISolidColorBrush)Palette.PreviewHere).Color, 0.35), 10), r.Inflate(3), radius + 3, radius + 3);
		var border = selected ? new Pen(Palette.Selection, 2.5)
			: kind == NodeKind.Hypertext ? new Pen(accent, 1.6, new DashStyle(new double[] { 4, 3 }, 0))
			: new Pen(current ? Palette.PreviewHere : Palette.CardBorder, current ? 2.5 : 1.2);
		ctx.DrawRectangle(Palette.Card, border, r, radius, radius);

		// Header strip
		using (ctx.PushClip(new RoundedRect(r, radius)))
			ctx.FillRectangle(new SolidColorBrush(((ISolidColorBrush)accent).Color, 0.22), new Rect(r.X, r.Y, r.Width, HeaderH));
		string tag = kind switch { NodeKind.Hypertext => "LINK", NodeKind.Ending => "ENDING", _ => "" };
		if (_entryTargets.Contains(id)) tag = tag.Length > 0 ? "ENTRY · " + tag : "ENTRY";
		var tagFt = Text(tag, 9, accent, Bold, 90);
		ctx.DrawText(tagFt, new Point(r.Right - tagFt.Width - 10, r.Y + 8));
		DrawText(ctx, id, new Point(r.X + 10, r.Y + 5), 12.5, Palette.Text, Bold, r.Width - tagFt.Width - 26);

		// Body: a 1-2 line preview of the dialogue
		var lines = Dialogue.Lines(node);
		double y = r.Y + HeaderH + 5;
		if (lines.Count > 0)
		{
			var (sp, text) = Dialogue.ParseLine(lines[0]);
			var ft = Text(sp == Speaker.You ? "You: " + text : text, 11, Palette.ForSpeaker(sp), sp == Speaker.Narration ? Italic : Regular, r.Width - 20, 2);
			ctx.DrawText(ft, new Point(r.X + 10, y));
			if (ft.Height < 22 && lines.Count > 1)
			{
				var (sp2, text2) = Dialogue.ParseLine(lines[1]);
				DrawText(ctx, sp2 == Speaker.You ? "You: " + text2 : text2, new Point(r.X + 10, y + 16), 11, Palette.ForSpeaker(sp2), sp2 == Speaker.Narration ? Italic : Regular, r.Width - 20);
			}
		}

		// Options, each inside the node with a link port on the right edge
		foreach (var row in _rows.GetValueOrDefault(id) ?? new())
		{
			ctx.DrawRectangle(RowFill, null, row.Rect, 4, 4);
			var color = row.Kind == LinkKind.Topic ? Palette.Hypertext : row.Kind == LinkKind.Goto ? Palette.Muted : Palette.You;
			var rft = Text(row.Text, 10.5, color, row.Kind == LinkKind.Topic ? Bold : Regular, row.Rect.Width - 16);
			ctx.DrawText(rft, new Point(row.Rect.X + 6, row.Rect.Center.Y - rft.Height / 2));
			bool broken = row.Target != null && !_nodeRects.ContainsKey(row.Target);
			var brush = broken ? Palette.Error : row.Link != null ? LinkBrush(row.Link) : Palette.Faint;
			bool hot = row == _hoverRow || row == _dragRow;
			ctx.DrawEllipse(row.Target != null ? brush : Palette.Card, new Pen(hot ? Palette.Selection : brush, hot ? 2.5 : 1.5), row.Port, PortR - 1, PortR - 1);
		}

		// Footer: what happens at the end of the node
		var (footer, isEnding) = FooterBits(node);
		if (footer.Length > 0)
			DrawText(ctx, footer, new Point(r.X + 10, r.Bottom - FooterH), 10, isEnding ? Palette.Ending : Palette.Muted, Bold, r.Width - 20);

		// Issue dot / preview trail dot
		if (NodeIssues.TryGetValue(id, out var iss) && (iss.errors > 0 || iss.warnings > 0))
			ctx.DrawEllipse(iss.errors > 0 ? Palette.Error : Palette.Warn, null, new Point(r.Left + 2, r.Top + 2), 5, 5);
		if (PreviewTrail.Contains(id) && !current)
			ctx.DrawEllipse(Palette.PreviewHere, null, new Point(r.Right - 4, r.Bottom - 4), 3.5, 3.5);

		// Link handle
		if (selected || id == _hoverNode || _drag == Drag.Connect)
		{
			var c = new Point(r.Right, r.Top + HeaderH / 2);
			ctx.DrawEllipse(Palette.Card, new Pen(Palette.Selection, 1.5), c, PortR, PortR);
			ctx.DrawEllipse(Palette.Selection, null, c, 2.5, 2.5);
		}
	}

	static FormattedText Text(string s, double size, IBrush brush, Typeface tf, double maxWidth, int maxLines = 1) => new(s, CultureInfo.CurrentCulture, FlowDirection.LeftToRight, tf, size, brush)
	{
		MaxTextWidth = Math.Max(10, maxWidth),
		MaxLineCount = maxLines,
		Trimming = TextTrimming.CharacterEllipsis,
	};

	static void DrawText(DrawingContext ctx, string s, Point at, double size, IBrush brush, Typeface tf, double maxWidth) =>
		ctx.DrawText(Text(s, size, brush, tf, maxWidth), at);

	// ------------------------------------------------------------------ Hit testing

	string? NodeAt(Point world) => _nodeRects.LastOrDefault(kv => kv.Value.Contains(world)).Key;

	bool OnHandle(string id, Point world) =>
		_nodeRects.TryGetValue(id, out var r) && Distance(world, new Point(r.Right, r.Top + HeaderH / 2)) <= PortR + 5;

	string? HandleAt(Point world) => _nodeRects.Keys.FirstOrDefault(id => (id == SelectedId || id == _hoverNode) && OnHandle(id, world));

	PortRow? PortAt(Point world)
	{
		foreach (var rows in _rows.Values)
			foreach (var row in rows)
				if (Distance(world, row.Port) <= PortR + 4) return row;
		return null;
	}

	DialogueLink? ConditionAt(Point world) => _condBoxes.LastOrDefault(c => c.rect.Contains(world)).link;

	static double Distance(Point a, Point b) => Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Y - b.Y) * (a.Y - b.Y));

	// ------------------------------------------------------------------ Input

	protected override void OnPointerPressed(PointerPressedEventArgs e)
	{
		base.OnPointerPressed(e);
		Focus();
		if (_doc == null) return;
		var screen = e.GetPosition(this);
		var world = ToWorld(screen);
		var props = e.GetCurrentPoint(this).Properties;
		_dragStartScreen = _lastScreen = screen;
		_moved = false;

		if (props.IsMiddleButtonPressed)
		{
			_drag = Drag.Pan;
			e.Pointer.Capture(this);
			return;
		}

		var port = props.IsLeftButtonPressed ? PortAt(world) : null;
		var handle = port == null ? HandleAt(world) : null;
		var node = port != null ? null : handle ?? NodeAt(world);
		var cond = node == null ? ConditionAt(world) : null;
		bool onStart = node == null && cond == null && _startRect.Contains(world);

		if (props.IsRightButtonPressed)
		{
			if (node != null) Select(node);
			ShowContextMenu(node, cond, onStart, world);
			e.Handled = true;
			return;
		}
		if (!props.IsLeftButtonPressed) return;

		if (e.ClickCount == 2)
		{
			if (node != null) EditNodeRequested?.Invoke(node);
			else if (onStart) EditConversationRequested?.Invoke();
			else if (cond != null && cond.Source != null) EditNodeRequested?.Invoke(cond.Source);
			else if (cond != null) EditConversationRequested?.Invoke();
			e.Handled = true;
			return;
		}

		if (port != null)
		{
			_drag = Drag.Reconnect;
			_dragRow = port;
			_connectEnd = world;
			e.Pointer.Capture(this);
		}
		else if (handle != null)
		{
			_drag = Drag.Connect;
			_dragNode = handle;
			_connectAsTopic = e.KeyModifiers.HasFlag(KeyModifiers.Alt);
			_connectEnd = world;
			e.Pointer.Capture(this);
		}
		else if (node != null)
		{
			Select(node);
			_drag = Drag.Move;
			_dragNode = node;
			_moveOffset = world - _nodeRects[node].TopLeft;
			e.Pointer.Capture(this);
		}
		else if (onStart)
		{
			Select(null);
			_startSelected = true;
			_drag = Drag.Move;
			_dragNode = DialogueDocument.StartKey;
			_moveOffset = world - _startRect.TopLeft;
			e.Pointer.Capture(this);
		}
		else
		{
			Select(null);
			_drag = Drag.Pan;
			e.Pointer.Capture(this);
		}
		InvalidateVisual();
	}

	protected override void OnPointerMoved(PointerEventArgs e)
	{
		base.OnPointerMoved(e);
		if (_doc == null) return;
		var screen = e.GetPosition(this);
		var world = ToWorld(screen);
		switch (_drag)
		{
			case Drag.Pan:
				_pan += screen - _lastScreen;
				InvalidateVisual();
				break;
			case Drag.Move when _dragNode != null:
				if (!_moved && Distance(screen, _dragStartScreen) < 4) break;
				if (!_moved) _doc.BeginMove();
				_moved = true;
				var p = world - _moveOffset;
				_doc.MoveNode(_dragNode, new Point(Math.Round(p.X / 10) * 10, Math.Round(p.Y / 10) * 10));
				Rebuild();
				InvalidateVisual();
				break;
			case Drag.Connect or Drag.Reconnect:
				_connectEnd = world;
				_hoverNode = NodeAt(world);
				InvalidateVisual();
				break;
			default:
				var hover = NodeAt(world);
				if (hover == null && SelectedId != null && OnHandle(SelectedId, world)) hover = SelectedId;
				var hoverRow = PortAt(world);
				if (hover != _hoverNode || hoverRow != _hoverRow)
				{
					_hoverNode = hover;
					_hoverRow = hoverRow;
					InvalidateVisual();
				}
				Cursor = hoverRow != null || HandleAt(world) != null ? new Cursor(StandardCursorType.Cross)
					: hover != null ? new Cursor(StandardCursorType.Hand) : Cursor.Default;
				UpdateTooltip(world);
				break;
		}
		_lastScreen = screen;
	}

	DialogueLink? _tipLink;

	void UpdateTooltip(Point world)
	{
		var cond = ConditionAt(world);
		if (cond == _tipLink) return;
		_tipLink = cond;
		ToolTip.SetTip(this, cond == null ? null
			: $"{(cond.Kind == LinkKind.Entry ? "Entry" : cond.Source + " → " + cond.Kind.ToString().ToLowerInvariant())} into {cond.Target}\nif {cond.Condition}" +
			(cond.Kind == LinkKind.Choice ? $"\n\"{cond.Label}\"" : ""));
		ToolTip.SetIsOpen(this, cond != null);
	}

	protected override void OnPointerReleased(PointerReleasedEventArgs e)
	{
		base.OnPointerReleased(e);
		if (_doc == null) return;
		var world = ToWorld(e.GetPosition(this));
		if (_drag == Drag.Move && _moved) _doc.EndMove();
		if (_drag == Drag.Connect && _dragNode != null)
		{
			var from = _dragNode;
			var target = NodeAt(world);
			bool topic = _connectAsTopic || e.KeyModifiers.HasFlag(KeyModifiers.Alt);
			if (target != null)
			{
				_doc.Edit("Link", () => _doc.Connect(from, target, topic));
			}
			else if (Distance(e.GetPosition(this), _dragStartScreen) > 20)
			{
				var id = _doc.UniqueNodeId(from + (topic ? "_link" : "_next"));
				_doc.Edit("New node", () =>
				{
					_doc.AddNode(id, new Point(Math.Round(world.X / 10) * 10, Math.Round(world.Y / 10) * 10 - 20));
					_doc.Connect(from, id, topic);
				});
				Select(id);
			}
		}
		if (_drag == Drag.Reconnect && _dragRow is { } row && Distance(e.GetPosition(this), _dragStartScreen) > 6)
		{
			// Drop on a node = make / change the link; drop on nothing = drop the link.
			var to = NodeAt(world);
			if (to != row.Target)
				_doc.Edit(to == null ? "Drop link" : "Relink", () => _doc.SetTarget(row.NodeId, row.Kind, row.Index, row.TopicKey, to));
		}
		_drag = Drag.None;
		_dragNode = null;
		_dragRow = null;
		_hoverNode = null;
		e.Pointer.Capture(null);
		InvalidateVisual();
	}

	protected override void OnPointerWheelChanged(PointerWheelEventArgs e)
	{
		base.OnPointerWheelChanged(e);
		if (e.Delta.Y != 0)
			SetZoom(_zoom * Math.Pow(1.1, e.Delta.Y), e.GetPosition(this));
		else if (e.Delta.X != 0)
		{
			_pan += new Vector(e.Delta.X * 40, 0);
			InvalidateVisual();
		}
		e.Handled = true;
	}

	protected override void OnKeyDown(KeyEventArgs e)
	{
		base.OnKeyDown(e);
		if (_doc == null || e.Handled) return;
		switch (e.Key)
		{
			case Key.Delete or Key.Back when SelectedId != null:
				_ = DeleteNode(SelectedId);
				e.Handled = true;
				break;
			case Key.Enter when SelectedId != null:
				EditNodeRequested?.Invoke(SelectedId);
				e.Handled = true;
				break;
			case Key.P when SelectedId != null && e.KeyModifiers == KeyModifiers.None:
				PreviewRequested?.Invoke(SelectedId);
				e.Handled = true;
				break;
			case Key.F when e.KeyModifiers == KeyModifiers.None:
				FitToView();
				e.Handled = true;
				break;
			case Key.OemPlus or Key.Add:
				SetZoom(_zoom * 1.2);
				e.Handled = true;
				break;
			case Key.OemMinus or Key.Subtract:
				SetZoom(_zoom / 1.2);
				e.Handled = true;
				break;
		}
	}

	// ------------------------------------------------------------------ Commands

	Window? Owner => TopLevel.GetTopLevel(this) as Window;

	public void NewNodeAt(Point world)
	{
		if (_doc == null) return;
		var id = _doc.UniqueNodeId("new_node");
		_doc.Edit("New node", () => _doc.AddNode(id, new Point(Math.Round(world.X / 10) * 10, Math.Round(world.Y / 10) * 10)));
		Select(id);
		EditNodeRequested?.Invoke(id);
	}

	public void NewNodeInView() => NewNodeAt(ToWorld(new Point(Bounds.Width / 2 - NodeW / 2 * _zoom, Bounds.Height / 2)));

	public async Task DeleteNode(string id)
	{
		if (_doc == null || Owner == null) return;
		int refs = _doc.CountReferences(id);
		var msg = refs > 0
			? $"Delete node '{id}'? {refs} link(s) point to it and will be cleared."
			: $"Delete node '{id}'?";
		if (await Ui.Ask(Owner, "Delete node", msg, "Delete", "Cancel") != 0) return;
		_doc.Edit("Delete node", () => _doc.DeleteNode(id));
		Select(null);
	}

	public async Task RenameNode(string id)
	{
		if (_doc == null || Owner == null) return;
		var name = await Ui.Prompt(Owner, "Rename node", "New id (links to it are updated):", id, v =>
			v.Length == 0 ? "Required"
			: !System.Text.RegularExpressions.Regex.IsMatch(v, "^[A-Za-z0-9_]+$") ? "Letters, digits and _ only"
			: v != id && _doc.Node(v) != null ? "That id is taken" : null);
		if (name == null || name == id) return;
		_doc.Edit("Rename node", () => _doc.RenameNode(id, name));
		Select(name);
	}

	void ShowContextMenu(string? node, DialogueLink? cond, bool onStart, Point world)
	{
		var items = new List<Control>();
		MenuItem Item(string header, Action a, string? gesture = null)
		{
			var mi = new MenuItem { Header = header };
			if (gesture != null) mi.InputGesture = KeyGesture.Parse(gesture);
			mi.Click += (_, _) => a();
			return mi;
		}
		if (node != null)
		{
			items.Add(Item("Edit…", () => EditNodeRequested?.Invoke(node), "Enter"));
			items.Add(Item("► Preview from here", () => PreviewRequested?.Invoke(node), "P"));
			items.Add(new Separator());
			items.Add(Item("Add choice → new node", () => AddLinked(node, false)));
			items.Add(Item("Add hypertext link → new node", () => AddLinked(node, true)));
			items.Add(Item("Rename…", () => _ = RenameNode(node)));
			items.Add(new Separator());
			items.Add(Item("Delete", () => _ = DeleteNode(node), "Delete"));
		}
		else if (cond != null)
		{
			items.Add(Item("Edit condition…", () => _ = EditCondition(cond)));
			items.Add(Item("Remove condition", () => _doc!.Edit("Remove condition", () => SetCondition(cond, null))));
			items.Add(Item("Remove link", () => _doc!.Edit("Remove link", () => _doc.RemoveLink(cond))));
		}
		else if (onStart)
		{
			items.Add(Item("Edit entries & conversation…", () => EditConversationRequested?.Invoke()));
			items.Add(Item("► Preview from start", () => PreviewRequested?.Invoke(null)));
		}
		else
		{
			items.Add(Item("New node here", () => NewNodeAt(world)));
			items.Add(Item("Conversation settings…", () => EditConversationRequested?.Invoke()));
			items.Add(Item("► Preview from start", () => PreviewRequested?.Invoke(null)));
			items.Add(new Separator());
			items.Add(Item("Fit to view", FitToView, "F"));
			items.Add(Item("Auto-arrange", AutoArrange));
		}
		var menu = new ContextMenu { ItemsSource = items };
		menu.Open(this);
	}

	void AddLinked(string from, bool topic)
	{
		if (_doc == null) return;
		var id = _doc.UniqueNodeId(from + (topic ? "_link" : "_next"));
		var r = _nodeRects[from];
		_doc.Edit(topic ? "Add hypertext link" : "Add choice", () =>
		{
			var p = new Point(r.X + GraphLayout.ColumnPitch, r.Y);
			while (_doc.Layout.Values.Any(q => Math.Abs(q.X - p.X) < 200 && Math.Abs(q.Y - p.Y) < 120)) p += new Point(0, GraphLayout.RowPitch);
			_doc.AddNode(id, p);
			_doc.Connect(from, id, topic);
		});
		Select(id);
		Reveal(id);
	}

	async Task EditCondition(DialogueLink l)
	{
		if (Owner == null || _doc == null) return;
		var v = await Ui.EditCondition(Owner, "Edit condition", $"Condition for the link into '{l.Target}':",
			Vars.Conditions(_doc, AllDocs?.Invoke() ?? new[] { _doc }), l.Condition);
		if (v == null) return;
		_doc.Edit("Edit condition", () => SetCondition(l, v));
	}

	void SetCondition(DialogueLink l, string? cond)
	{
		JsonObject? holder = l.Kind switch
		{
			LinkKind.Entry => _doc!.Entries[l.Index] as JsonObject,
			LinkKind.Choice => (_doc!.Node(l.Source)?["choices"] as JsonArray)?[l.Index] as JsonObject,
			LinkKind.Topic => TopicObject(l),
			_ => null,
		};
		if (holder == null) return;
		if (string.IsNullOrWhiteSpace(cond))
		{
			if (l.Kind == LinkKind.Entry) holder["if"] = "true";
			else holder.Remove("if");
		}
		else holder["if"] = cond;
	}

	JsonObject? TopicObject(DialogueLink l)
	{
		if (_doc!.Node(l.Source)?["topics"] is not JsonObject ts || l.TopicKey == null) return null;
		if (ts[l.TopicKey] is JsonObject o) return o;
		var o2 = new JsonObject { ["goto"] = Dialogue.Str(ts[l.TopicKey]) };
		ts[l.TopicKey] = o2;
		return o2;
	}
}
