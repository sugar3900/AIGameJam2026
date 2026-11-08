using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using AvaloniaEdit;
using AvaloniaEdit.Document;
using AvaloniaEdit.Editing;
using AvaloniaEdit.Rendering;
using StoryWriter.Graph;
using StoryWriter.Model;
using StoryWriter.Runtime;

namespace StoryWriter.UI;

/// <summary>Colours dialogue lines: You: lines blue, *narration* italic, [topics] pink, {player}/{name} teal.</summary>
sealed class LineColorizer : DocumentColorizingTransformer
{
	protected override void ColorizeLine(DocumentLine line)
	{
		var text = CurrentContext.Document.GetText(line);
		if (text.Length == 0) return;
		int o = line.Offset;
		var (speaker, _) = Dialogue.ParseLine(text);
		var trimmedStart = text.Length - text.TrimStart().Length;
		if (speaker == Speaker.You)
		{
			ChangeLinePart(o, o + line.Length, e => e.TextRunProperties.SetForegroundBrush(Palette.You));
			ChangeLinePart(o + trimmedStart, o + trimmedStart + 4, e =>
				e.TextRunProperties.SetTypeface(new Typeface(e.TextRunProperties.Typeface.FontFamily, FontStyle.Normal, FontWeight.Bold)));
		}
		else if (speaker == Speaker.Narration)
		{
			ChangeLinePart(o, o + line.Length, e =>
			{
				e.TextRunProperties.SetForegroundBrush(Palette.Narration);
				e.TextRunProperties.SetTypeface(new Typeface(e.TextRunProperties.Typeface.FontFamily, FontStyle.Italic));
			});
		}
		foreach (Match m in Regex.Matches(text, @"\{(player|name)\}"))
		{
			var color = m.Groups[1].Value == "player" ? Palette.You : Palette.Start;
			var fill = new SolidColorBrush(((ISolidColorBrush)color).Color, 0.28);
			ChangeLinePart(o + m.Index, o + m.Index + m.Length, e =>
			{
				e.TextRunProperties.SetForegroundBrush(color);
				e.TextRunProperties.SetBackgroundBrush(fill);
			});
		}
		foreach (var t in Dialogue.Topics(text))
		{
			ChangeLinePart(o + t.Start, o + t.Start + t.Length, e =>
			{
				e.TextRunProperties.SetForegroundBrush(Palette.Hypertext);
				e.TextRunProperties.SetTypeface(new Typeface(e.TextRunProperties.Typeface.FontFamily, e.TextRunProperties.Typeface.Style, FontWeight.Bold));
				e.TextRunProperties.SetTextDecorations(TextDecorations.Underline);
			});
		}
	}
}

/// <summary>Where the [shown|key] hyperlink markup lives in the text: its words are editable, the delimiters are not.</summary>
static class LinkMarkup
{
	public static readonly Regex Rx = new(@"\[([^\[\]|\n]*)(\|[^\[\]\n]*)?\]", RegexOptions.Compiled);

	/// <summary>The hidden pieces: the opening "[" and the closing "|key]" (or just "]").</summary>
	public static IEnumerable<(int start, int length)> Delimiters(string text, int baseOffset = 0)
	{
		foreach (Match m in Rx.Matches(text))
		{
			yield return (baseOffset + m.Index, 1);
			int suffix = m.Index + 1 + m.Groups[1].Length;
			yield return (baseOffset + suffix, m.Length - 1 - m.Groups[1].Length);
		}
	}
}

/// <summary>Hides the hyperlink delimiters so a link reads as plain, editable words (coloured by <see cref="LineColorizer"/>).</summary>
sealed class LinkDelimiterGenerator : VisualLineElementGenerator
{
	IEnumerable<(int start, int length)> Pieces()
	{
		int from = CurrentContext.VisualLine.FirstDocumentLine.Offset, to = CurrentContext.VisualLine.LastDocumentLine.EndOffset;
		return LinkMarkup.Delimiters(CurrentContext.Document.GetText(from, to - from), from);
	}

	public override int GetFirstInterestedOffset(int startOffset)
	{
		foreach (var (start, _) in Pieces())
			if (start >= startOffset) return start;
		return -1;
	}

	public override VisualLineElement? ConstructElement(int offset)
	{
		foreach (var (start, length) in Pieces())
			if (start == offset) return new FormattedTextElement("\u200B", length);
		return null;
	}
}

/// <summary>{player} / {name} as single, uneditable inline objects: "Player Name" (blue) and the character's name (green).</summary>
sealed class PlaceholderGenerator : VisualLineElementGenerator
{
	static readonly Regex Rx = new(@"\{(player|name)\}", RegexOptions.Compiled);
	readonly Func<string> _name;

	public PlaceholderGenerator(Func<string> name) => _name = name;

	public override int GetFirstInterestedOffset(int startOffset)
	{
		int to = CurrentContext.VisualLine.LastDocumentLine.EndOffset;
		var m = Rx.Match(CurrentContext.Document.GetText(startOffset, to - startOffset));
		return m.Success ? startOffset + m.Index : -1;
	}

	public override VisualLineElement? ConstructElement(int offset)
	{
		int to = CurrentContext.VisualLine.LastDocumentLine.EndOffset;
		var m = Rx.Match(CurrentContext.Document.GetText(offset, to - offset));
		if (!m.Success || m.Index != 0) return null;
		return new FormattedTextElement(m.Groups[1].Value == "player" ? " Player Name " : " " + _name() + " ", m.Length);
	}
}

/// <summary>Keeps the hidden hyperlink delimiters from being typed into or deleted by hand.</summary>
sealed class LinkProtector : IReadOnlySectionProvider
{
	readonly TextEditor _editor;

	public LinkProtector(TextEditor editor) => _editor = editor;

	List<(int s, int e)> Protected() =>
		LinkMarkup.Delimiters(_editor.Document.Text).Select(d => (d.start, d.start + d.length)).ToList();

	public bool CanInsert(int offset) => !Protected().Any(p => offset > p.s && offset < p.e);

	public IEnumerable<ISegment> GetDeletableSegments(ISegment segment)
	{
		int pos = segment.Offset, end = segment.EndOffset;
		if (segment.Length == 0)
		{
			yield return segment;
			yield break;
		}
		foreach (var (s, e) in Protected())
		{
			if (e <= pos || s >= end) continue;
			if (s > pos) yield return new TextSegment { StartOffset = pos, EndOffset = s };
			pos = Math.Max(pos, e);
		}
		if (pos < end) yield return new TextSegment { StartOffset = pos, EndOffset = end };
	}
}

/// <summary>Double-click a node: edit its lines as rich text plus choices, hypertext links and flow.</summary>
public sealed class NodeEditorWindow : Window
{
	static readonly string[] NodeOrder = { "lines", "say", "do", "topics", "choices", "goto", "end", "ending", "fx", "fxText" };
	static readonly string[] ChoiceOrder = { "text", "if", "goto", "do" };
	static readonly string[] TopicOrder = { "goto", "if", "do" };

	readonly DialogueDocument _doc;
	string _nodeId;
	readonly TextBox _id = new() { FontSize = 15, FontWeight = FontWeight.Bold, Width = 260 };
	readonly TextBlock _kind = Ui.Label("", 12, Palette.Muted);
	readonly TextEditor _editor;
	readonly StackPanel _preview = new() { Spacing = 8 };
	readonly StackPanel _choiceRows = new() { Spacing = 8 };
	readonly StackPanel _topicRows = new() { Spacing = 8 };
	readonly TextBlock _problems = Ui.Label("", 12, Palette.Error);
	readonly TabControl _tabs = new();

	const string NoneLabel = "(none)";
	readonly Func<IEnumerable<DialogueDocument>> _allDocs;
	readonly ComboBox _goto = new() { MinWidth = 200 };
	readonly CheckBox _end = new() { Content = "end conversation after the last line" };
	readonly ComboBox _ending = new() { ItemsSource = new[] { "(none)", "auto" }.Concat(Dialogue.Endings).ToList(), MinWidth = 200 };
	readonly ComboBox _fx = new() { ItemsSource = new[] { "(none)" }.Concat(Dialogue.FxKinds).ToList(), MinWidth = 200 };
	readonly TextBox _fxText = new() { PlaceholderText = "text shown during the fade", TextWrapping = TextWrapping.Wrap, AcceptsReturn = false };
	readonly EffectsEditor _do;
	readonly List<string> _nodeIds;
	string _initialSnapshot = "";

	public string NodeId => _nodeId;
	public DialogueDocument Doc => _doc;
	public event Action<string>? PreviewRequested;

	public NodeEditorWindow(DialogueDocument doc, string nodeId, Func<IEnumerable<DialogueDocument>> allDocs)
	{
		_doc = doc;
		_allDocs = allDocs;
		_nodeId = nodeId;
		_do = new EffectsEditor(Vars.Effects(doc, allDocs()), doc.Node(nodeId)?["do"] as JsonObject);
		_do.Changed += () => { };
		_nodeIds = doc.NodeIds.ToList();
		Title = $"{doc.Name} · {nodeId}";
		Width = 1100;
		Height = 780;
		MinWidth = 760;
		MinHeight = 520;
		Background = Palette.Panel;
		WindowStartupLocation = WindowStartupLocation.CenterOwner;

		_editor = new TextEditor
		{
			FontSize = 15,
			WordWrap = true,
			ShowLineNumbers = true,
			Foreground = Palette.Him,
			Background = Palette.Card,
			Padding = new Thickness(6),
			FontFamily = FontFamily.Default,
		};
		_editor.Options.EnableHyperlinks = false;
		_editor.Options.EnableEmailHyperlinks = false;
		_editor.TextArea.TextView.LineTransformers.Add(new LineColorizer());
		_editor.TextArea.TextView.ElementGenerators.Add(new LinkDelimiterGenerator());
		_editor.TextArea.TextView.ElementGenerators.Add(new PlaceholderGenerator(() => _doc.Name));
		_editor.TextArea.ReadOnlySectionProvider = new LinkProtector(_editor);
		_editor.TextChanged += (_, _) =>
		{
			SyncTopics();
			RefreshPreview();
		};

		Content = BuildLayout();
		Load();
		KeyDown += OnKey;
		Closed += (_, _) => AudioService.StopVoice();
		Opened += (_, _) => _editor.Focus();
	}

	/// <summary>Next-node dropdown: every other node except hypertext link nodes.</summary>
	ComboBox GotoBox(string current, bool forLink = false)
	{
		var cb = new ComboBox { MinWidth = 160, HorizontalAlignment = HorizontalAlignment.Stretch };
		FillGoto(cb, current, forLink);
		return cb;
	}

	/// <param name="forLink">Hyperlink targets: hypertext nodes are the point, so they are listed.</param>
	void FillGoto(ComboBox cb, string current, bool forLink = false)
	{
		var kinds = _doc.NodeKinds();
		var items = new List<string> { NoneLabel };
		items.AddRange(_doc.NodeIds.Where(id => id != _nodeId && (forLink || kinds.GetValueOrDefault(id) != NodeKind.Hypertext)));
		// Keep whatever is already set (a self-loop, a link node, a node that doesn't exist yet) so it isn't lost silently.
		if (current.Length > 0 && !items.Contains(current)) items.Add(current);
		cb.ItemsSource = items;
		cb.SelectedItem = current.Length == 0 ? NoneLabel : current;
	}

	static string GotoValue(ComboBox cb) => cb.SelectedItem is string s && s != NoneLabel ? s : "";

	IEnumerable<string> ConditionVars() => Vars.Conditions(_doc, _allDocs());

	/// <summary>A toolbar button that looks like the inline token it inserts (same colour and background).</summary>
	static Button TokenButton(string label, IBrush color, string tip, Action click)
	{
		var fill = new SolidColorBrush(((ISolidColorBrush)color).Color, 0.28);
		var b = Ui.Btn(label, click, tip);
		b.Foreground = color;
		b.Background = fill;
		b.Padding = new Thickness(4, 4);
		b.Resources["ButtonForegroundPointerOver"] = color;
		b.Resources["ButtonForegroundPressed"] = color;
		b.Resources["ButtonBackgroundPointerOver"] = new SolidColorBrush(((ISolidColorBrush)color).Color, 0.45);
		b.Resources["ButtonBackgroundPressed"] = new SolidColorBrush(((ISolidColorBrush)color).Color, 0.6);
		return b;
	}

	// ------------------------------------------------------------ Layout

	Control BuildLayout()
	{
		var header = new DockPanel { Margin = new Thickness(16, 12, 16, 6) };
		var headerLeft = Ui.Row(10, Ui.Label("Node", 12, Palette.Muted), _id, _kind);
		header.Children.Add(headerLeft);

		Button Tool(string label, string tip, Action a) => Ui.Btn(label, a, tip);
		var toolbar = new WrapPanel { Margin = new Thickness(16, 0, 16, 6) };
		foreach (var c in new Control[]
		{
			Ui.Label("Line speaker:", 12, Palette.Muted),
			Tool("Him", "Plain line: the hunk speaks", () => SetSpeaker(Speaker.Him)),
			Tool("You", "\"You: ...\" — Rosie speaks", () => SetSpeaker(Speaker.You)),
			Tool("Narration", "\"*...*\" — narration (italic)", () => SetSpeaker(Speaker.Narration)),
			new Border { Width = 16 },
			Tool("⛓ Hypertext link", "Turn the selected word(s) into a clickable [topic] that leads to its own node", MakeLink),
			TokenButton(" Player Name ", Palette.You, "Insert the player's name", () => Insert("{player}")),
			TokenButton(" " + _doc.Name + " ", Palette.Start, "Insert this character's name", () => Insert("{name}")),
		})
		{
			c.Margin = new Thickness(0, 0, 6, 4);
			toolbar.Children.Add(c);
		}

		var linesHelp = Ui.Label("One dialogue line per row. Plain = him, \"You: …\" = Rosie, \"*…*\" = narration. [word] or [shown text|topic] makes a hypertext link.", 11, Palette.Muted);
		var editorBorder = new Border { BorderBrush = Palette.CardBorder, BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(6), Child = _editor, MinHeight = 160 };
		var previewScroll = new ScrollViewer { Content = new Border { Padding = new Thickness(12), Child = _preview }, Background = Palette.Canvas };
		var left = new Grid { RowDefinitions = new RowDefinitions("Auto,2*,Auto,*"), Margin = new Thickness(16, 0, 8, 0), RowSpacing = 6 };
		left.Children.Add(linesHelp);
		Grid.SetRow(editorBorder, 1);
		left.Children.Add(editorBorder);
		var pvLabel = Ui.Caption("AS IT PLAYS");
		Grid.SetRow(pvLabel, 2);
		left.Children.Add(pvLabel);
		Grid.SetRow(previewScroll, 3);
		left.Children.Add(previewScroll);

		_tabs.Items.Add(new TabItem { Header = "Choices", Content = Section(_choiceRows, "+ Add choice", () => AddChoiceRow(null), "Shown under the last line. Hidden in game when \"if\" is false. Empty goto = end conversation.") });
		_tabs.Items.Add(new TabItem { Header = "Hypertext links", Content = Section(_topicRows, null, null, "Select words in the lines and press ⛓ Hypertext link to make one. Each link opens its own node, then returns here. Delete a link from the text by deleting it like a single character.") });
		_tabs.Items.Add(new TabItem { Header = "Flow & effects", Content = new ScrollViewer { Content = FlowSection() } });
		var right = new Border { Margin = new Thickness(8, 0, 16, 0), Child = _tabs };

		var main = new Grid { ColumnDefinitions = new ColumnDefinitions("1.1*,4,*") };
		main.Children.Add(left);
		var split = new GridSplitter { Background = Palette.PanelAlt };
		Grid.SetColumn(split, 1);
		main.Children.Add(split);
		Grid.SetColumn(right, 2);
		main.Children.Add(right);

		var buttons = Ui.Row(8,
			Ui.Btn("► Apply & preview from here", () => { if (Apply()) PreviewRequested?.Invoke(_nodeId); }),
			Ui.Btn("Cancel", () => _ = CloseAsk()),
			Ui.Btn("Apply", () => Apply()),
			Ui.Btn("OK", () => { if (Apply()) Close(); }, "⌘/Ctrl+Enter", accent: true));
		buttons.HorizontalAlignment = HorizontalAlignment.Right;
		var bottom = new DockPanel { Margin = new Thickness(16, 8, 16, 14) };
		DockPanel.SetDock(buttons, Dock.Right);
		bottom.Children.Add(buttons);
		bottom.Children.Add(_problems);

		var root = new DockPanel();
		DockPanel.SetDock(header, Dock.Top);
		DockPanel.SetDock(toolbar, Dock.Top);
		DockPanel.SetDock(bottom, Dock.Bottom);
		root.Children.Add(header);
		root.Children.Add(toolbar);
		root.Children.Add(bottom);
		root.Children.Add(main);
		return root;
	}

	static Control Section(StackPanel rows, string? addLabel, Action? add, string help) =>
		new ScrollViewer
		{
			Content = addLabel == null ? Ui.Col(10, Ui.Label(help, 11, Palette.Muted), rows) : Ui.Col(10, Ui.Label(help, 11, Palette.Muted), rows, Ui.Btn(addLabel, add!)),
			Padding = new Thickness(4, 8, 10, 8),
		};

	Control FlowSection() => Ui.Col(12,
		Ui.Label("What happens after the last line when there are no (visible) choices.", 11, Palette.Muted),
		Ui.Field("goto (next node)", _goto),
		_end,
		Ui.Field("ending (repairs the malady + shows the ending card)", _ending),
		Ui.Field("fx (plays when the node is entered)", _fx),
		Ui.Field("fxText", _fxText),
		Ui.Field("do (effects applied when the node is entered)", _do,
			"romance / friendship / friction (this hunk), <hunk>.<stat> (another hunk), flag.<name>"));

	// ------------------------------------------------------------ Rows

	sealed class ChoiceRow
	{
		public JsonObject? Original;
		public TextBox Text = null!;
		public ConditionEditor If = null!;
		public EffectsEditor Do = null!;
		public ComboBox Goto = null!;
		public Control View = null!;
	}

	sealed class TopicRow
	{
		public JsonNode? Original;
		/// <summary>Internal id (hidden); <see cref="Shown"/> is the wording in the text.</summary>
		public TextBox Key = null!, Shown = null!;
		public ConditionEditor If = null!;
		public EffectsEditor Do = null!;
		public ComboBox Goto = null!;
		public Control View = null!;
	}

	readonly List<ChoiceRow> _choices = new();
	readonly List<TopicRow> _topics = new();

	void AddChoiceRow(JsonObject? c)
	{
		var row = new ChoiceRow { Original = c };
		row.Text = new TextBox { Text = Dialogue.Str(c?["text"]) ?? "", PlaceholderText = "What Rosie says", TextWrapping = TextWrapping.Wrap };
		row.Goto = GotoBox(Dialogue.Str(c?["goto"]) ?? "");
		row.If = new ConditionEditor(ConditionVars(), Dialogue.Str(c?["if"]), "always shown");
		row.Do = new EffectsEditor(Vars.Effects(_doc, _allDocs()), c?["do"] as JsonObject);
		var tools = Ui.Row(2,
			Ui.Btn("↑", () => MoveRow(_choices, _choiceRows, row, -1, r => r.View), "Move up"),
			Ui.Btn("↓", () => MoveRow(_choices, _choiceRows, row, 1, r => r.View), "Move down"),
			Ui.Btn("✕", () => { _choices.Remove(row); _choiceRows.Children.Remove(row.View); RefreshPreview(); }, "Remove choice"));
		var fields = Ui.Col(4,
			Ui.Field("go to", row.Goto, "Next node. (none) ends the conversation."),
			Ui.Field("if", row.If),
			Ui.Field("do", row.Do));
		var top = new DockPanel();
		DockPanel.SetDock(tools, Dock.Right);
		top.Children.Add(tools);
		top.Children.Add(row.Text);
		row.View = new Border
		{
			Background = Palette.Card,
			CornerRadius = new CornerRadius(6),
			Padding = new Thickness(8),
			Child = Ui.Col(6, top, fields),
		};
		row.Text.TextChanged += (_, _) => RefreshPreview();
		row.If.Changed += RefreshPreview;
		_choices.Add(row);
		_choiceRows.Children.Add(row.View);
	}

	void AddTopicRow(string? key, JsonNode? t, string? shown = null)
	{
		var row = new TopicRow { Original = t };
		var to = t as JsonObject;
		row.Key = new TextBox { Text = key ?? "" };
		row.Shown = new TextBox { Text = shown ?? key ?? "", PlaceholderText = "link text" };
		row.Goto = GotoBox(to != null ? Dialogue.Str(to["goto"]) ?? "" : Dialogue.Str(t) ?? "", forLink: true);
		row.If = new ConditionEditor(ConditionVars(), Dialogue.Str(to?["if"]), "always clickable");
		row.Do = new EffectsEditor(Vars.Effects(_doc, _allDocs()), to?["do"] as JsonObject);
		var del = Ui.Btn("✕", () => RemoveLinkFromText(row), "Remove this link (its words stay in the text as plain text)");
		var top = new DockPanel();
		DockPanel.SetDock(del, Dock.Right);
		top.Children.Add(del);
		top.Children.Add(Ui.Row(6, Ui.Label("⛓", 14, Palette.Hypertext, FontWeight.Bold), row.Shown));
		row.Shown.MinWidth = 220;
		var grid = Ui.Col(4, Ui.Field("goes to", row.Goto), Ui.Field("if", row.If), Ui.Field("do", row.Do));
		row.View = new Border
		{
			Background = Palette.Card,
			BorderBrush = Palette.Hypertext,
			BorderThickness = new Thickness(1),
			CornerRadius = new CornerRadius(14),
			Padding = new Thickness(10, 8),
			Child = Ui.Col(4, top, grid),
		};
		row.Shown.TextChanged += (_, _) =>
		{
			// Only the user's typing rewrites the text; the box being filled in or refreshed must not.
			if (!_syncing && row.Shown.IsKeyboardFocusWithin) RewriteLink(row);
		};
		row.If.Changed += RefreshPreview;
		_topics.Add(row);
		_topicRows.Children.Add(row.View);
	}

	// ------------------------------------------------------------ Link <-> text sync

	bool _syncing, _loading;
	HashSet<string> _knownKeys = new();

	static string KeyOf(TopicRow r) => (r.Key.Text ?? "").Trim().ToLowerInvariant();

	/// <summary>Keeps the Hypertext links tab in step with the [links] in the text: new ones get a row, deleted ones lose theirs.</summary>
	void SyncTopics()
	{
		if (_loading || _syncing) return;
		_syncing = true;
		try
		{
			CleanupEmptyLinks();
			var inText = Dialogue.Topics(_editor.Text ?? "");
			var keys = inText.Select(t => t.TopicId).ToHashSet();
			foreach (var row in _topics.ToList())
				if (_knownKeys.Contains(KeyOf(row)) && !keys.Contains(KeyOf(row)))
				{
					_topics.Remove(row);
					_topicRows.Children.Remove(row.View);
				}
			foreach (var t in inText)
			{
				var row = _topics.FirstOrDefault(x => KeyOf(x) == t.TopicId);
				if (row == null)
					AddTopicRow(t.TopicId, JsonValue.Create(SuggestNewNodeId((_id.Text ?? _nodeId).Trim() + "_" + Regex.Replace(t.TopicId, @"[^a-z0-9_]+", "_"))), t.Shown);
				else if (row.Shown.Text != t.Shown && inText.First(x => x.TopicId == t.TopicId) == t)
					row.Shown.Text = t.Shown;
			}
			_knownKeys = keys;
		}
		finally
		{
			_syncing = false;
		}
	}

	/// <summary>A link whose words were all deleted (or are just whitespace) stops being a link.</summary>
	void CleanupEmptyLinks()
	{
		var text = _editor.Text ?? "";
		var empty = LinkMarkup.Rx.Matches(text).Where(m => m.Groups[1].Value.Trim().Length == 0).Reverse().ToList();
		if (empty.Count == 0) return;
		foreach (var m in empty) _editor.Document.Replace(m.Index, m.Length, m.Groups[1].Value);
	}

	/// <summary>The link's wording was edited in the tab: rewrite its markup in the text.</summary>
	void RewriteLink(TopicRow row)
	{
		var shown = row.Shown.Text ?? "";
		if (shown.Length == 0 || shown.IndexOfAny(new[] { '[', ']', '|', '\n' }) >= 0)
		{
			_problems.Foreground = Palette.Warn;
			_problems.Text = "Link text can't be empty or contain [ ] |";
			return;
		}
		var key = KeyOf(row);
		var t = Dialogue.Topics(_editor.Text ?? "").FirstOrDefault(x => x.TopicId == key);
		if (t == null) return;
		var markup = shown.Trim().ToLowerInvariant() == key ? $"[{shown}]" : $"[{shown}|{key}]";
		if (_editor.Document.GetText(t.Start, t.Length) == markup) return;
		_syncing = true;
		try { _editor.Document.Replace(t.Start, t.Length, markup); }
		finally { _syncing = false; }
		_problems.Text = "";
	}

	void RemoveLinkFromText(TopicRow row)
	{
		var key = KeyOf(row);
		_syncing = true;
		try
		{
			foreach (var t in Dialogue.Topics(_editor.Text ?? "").Where(x => x.TopicId == key).Reverse().ToList())
				_editor.Document.Replace(t.Start, t.Length, t.Shown);
			_topics.Remove(row);
			_topicRows.Children.Remove(row.View);
			_knownKeys.Remove(key);
		}
		finally { _syncing = false; }
		RefreshPreview();
	}

	static void MoveRow<T>(List<T> list, StackPanel panel, T row, int dir, Func<T, Control> view)
	{
		int i = list.IndexOf(row), j = i + dir;
		if (j < 0 || j >= list.Count) return;
		(list[i], list[j]) = (list[j], list[i]);
		panel.Children.Clear();
		foreach (var r in list) panel.Children.Add(view(r));
	}

	// ------------------------------------------------------------ Load / preview

	void Load()
	{
		_loading = true;
		var node = _doc.Node(_nodeId) ?? new JsonObject();
		_id.Text = _nodeId;
		var kind = _doc.NodeKinds().GetValueOrDefault(_nodeId);
		_kind.Text = kind switch
		{
			NodeKind.Hypertext => "hypertext link node (only reached by clicking a [word])",
			NodeKind.Ending => "ending node",
			_ => "story node",
		};
		_kind.Foreground = Palette.ForKind(kind);
		_editor.Document = new TextDocument(string.Join("\n", Dialogue.Lines(node)));
		if (node["choices"] is JsonArray cs)
			foreach (var c in cs.OfType<JsonObject>()) AddChoiceRow(c);
		if (node["topics"] is JsonObject ts)
			foreach (var (k, v) in ts) AddTopicRow(k, v, Dialogue.TopicLabel(node, k));
		FillGoto(_goto, Dialogue.Str(node["goto"]) ?? "");
		_end.IsChecked = Dialogue.Bool(node["end"]);
		var ending = Dialogue.Str(node["ending"]);
		_ending.SelectedItem = string.IsNullOrEmpty(ending) ? "(none)" : ending;
		if (_ending.SelectedItem == null) _ending.SelectedIndex = 0;
		var fx = Dialogue.Str(node["fx"]);
		_fx.SelectedItem = string.IsNullOrEmpty(fx) ? "(none)" : fx;
		if (_fx.SelectedItem == null) _fx.SelectedIndex = 0;
		_fxText.Text = Dialogue.Str(node["fxText"]) ?? "";
		if (_choices.Count == 0 && _topics.Count > 0) _tabs.SelectedIndex = 1;
		else if (_choices.Count == 0) _tabs.SelectedIndex = 2;
		else _tabs.SelectedIndex = 0;
		_loading = false;
		_knownKeys = Dialogue.Topics(_editor.Text ?? "").Select(t => t.TopicId).ToHashSet();
		RefreshPreview();
		_initialSnapshot = Snapshot();
	}

	string Snapshot() => string.Join("\u0001", new[] { _id.Text, _editor.Text, GotoValue(_goto), _end.IsChecked?.ToString(), _ending.SelectedItem as string, _fx.SelectedItem as string, _fxText.Text, _do.Snapshot }
		.Concat(_choices.SelectMany(c => new[] { c.Text.Text, GotoValue(c.Goto), c.If.Value, c.Do.Snapshot }))
		.Concat(_topics.SelectMany(t => new[] { t.Key.Text, GotoValue(t.Goto), t.If.Value, t.Do.Snapshot })));

	IEnumerable<string> EditorLines() => (_editor.Text ?? "").Replace("\r", "").Split('\n').Where(l => l.Trim().Length > 0);

	/// <summary>
	/// Speaker widget for one line, keyed like the game: script id, node id as saved, index in the node's lines.
	/// Narration and the player's lines are never voiced (nothing shown); a spoken line without a recording shows "no clip".
	/// </summary>
	Control LineAudio(string raw, int index)
	{
		if (!AudioLibrary.IsVoiceable(raw)) return new Panel();
		var dir = ProjectPaths.VoiceDir();
		var clip = AudioLibrary.ResolveVoice(dir, _doc.Id, _nodeId, index, raw);
		return clip != null ? AudioUi.ClipButton(clip) : AudioUi.NoClip(AudioLibrary.VoiceKey(_doc.Id, _nodeId, index));
	}

	void RefreshPreview()
	{
		_preview.Children.Clear();
		var topicKeys = _topics.Select(t => (t.Key.Text ?? "").Trim().ToLowerInvariant()).ToHashSet();
		var missing = new List<string>();
		int lineIndex = 0;
		foreach (var raw in EditorLines())
		{
			var (sp, text) = Dialogue.ParseLine(raw);
			var name = sp switch { Speaker.You => "ROSIE", Speaker.Narration => "", _ => _doc.Name.ToUpperInvariant() };
			var tb = RichLine.Build(text, sp, null, null, 14, substituteHints: true);
			Control audio = LineAudio(raw, lineIndex++);
			var head = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
			head.Children.Add(Ui.Caption(name));
			Grid.SetColumn(audio, 1);
			head.Children.Add(audio);
			_preview.Children.Add(name.Length > 0 ? Ui.Col(1, head, tb) : tb);
			missing.AddRange(Dialogue.Topics(text).Select(t => t.TopicId).Where(t => !topicKeys.Contains(t)));
		}
		var shownChoices = _choices.Where(c => !string.IsNullOrWhiteSpace(c.Text.Text)).ToList();
		for (int i = 0; i < shownChoices.Count; i++)
		{
			var c = shownChoices[i];
			var cond = c.If.Value;
			_preview.Children.Add(new TextBlock
			{
				Text = $"{i + 1}.  {c.Text.Text}" + (string.IsNullOrEmpty(cond) ? "" : $"    [if {cond}]"),
				Foreground = string.IsNullOrEmpty(cond) ? Palette.You : Palette.Condition,
				FontSize = 13,
				TextWrapping = TextWrapping.Wrap,
				Margin = new Thickness(20, 0, 0, 0),
			});
		}
		_problems.Foreground = Palette.Muted;
		_problems.Text = missing.Count > 0
			? $"New link(s) {string.Join(", ", missing.Distinct().Select(m => "\"" + (Dialogue.Topics(_editor.Text ?? "").FirstOrDefault(t => t.TopicId == m)?.Shown.Trim() ?? m) + "\""))} will get their own node on Apply."
			: "";
	}

	// ------------------------------------------------------------ Toolbar actions

	void SetSpeaker(Speaker s)
	{
		var line = _editor.Document.GetLineByNumber(_editor.TextArea.Caret.Line);
		var (_, text) = Dialogue.ParseLine(_editor.Document.GetText(line));
		_editor.Document.Replace(line.Offset, line.Length, Dialogue.ComposeLine(s, text));
		_editor.Focus();
	}

	void Insert(string token)
	{
		_editor.Document.Replace(_editor.SelectionStart, _editor.SelectionLength, token);
		_editor.Focus();
	}

	void MakeLink()
	{
		var sel = _editor.SelectedText;
		if (string.IsNullOrWhiteSpace(sel) || sel.Contains('\n') || sel.Contains('[') || sel.Contains(']'))
		{
			_problems.Foreground = Palette.Warn;
			_problems.Text = "Select a word or phrase on one line first.";
			return;
		}
		var key = Regex.Replace(sel.Trim().ToLowerInvariant(), @"[^a-z0-9_]+", "_").Trim('_');
		if (key.Length == 0) key = "topic";
		var existing = _topics.Select(t => (t.Key.Text ?? "").Trim().ToLowerInvariant()).ToHashSet();
		var k = key;
		for (int i = 2; existing.Contains(k); i++) k = key + i;
		var markup = sel.Trim().ToLowerInvariant() == k ? $"[{sel}]" : $"[{sel}|{k}]";
		_editor.Document.Replace(_editor.SelectionStart, _editor.SelectionLength, markup);
		// The text change adds the link's row (see SyncTopics).
		_tabs.SelectedIndex = 1;
		RefreshPreview();
	}

	string SuggestNewNodeId(string b)
	{
		var pending = _choices.Select(c => GotoValue(c.Goto)).Concat(_topics.Select(t => GotoValue(t.Goto))).ToHashSet();
		var id = _doc.UniqueNodeId(b);
		for (int i = 2; pending.Contains(id); i++) id = _doc.UniqueNodeId($"{b}_{i}");
		return id;
	}

	// ------------------------------------------------------------ Apply

	bool Apply()
	{
		var errors = new List<string>();
		var newId = (_id.Text ?? "").Trim();
		if (!Regex.IsMatch(newId, "^[A-Za-z0-9_]+$")) errors.Add("Node id: letters, digits and _ only.");
		else if (newId != _nodeId && _doc.Node(newId) != null) errors.Add($"Node id '{newId}' is taken.");
		if (_doc.Node(_nodeId) == null) errors.Add($"Node '{_nodeId}' no longer exists (deleted or renamed elsewhere).");

		void Cond(string where, ConditionEditor c)
		{
			if (c.Error is { } e) errors.Add($"{where} condition: {e}");
		}
		JsonObject? Fx(string where, EffectsEditor ed)
		{
			var o = ed.Value(out var err);
			if (err != null) errors.Add($"{where}: {err}");
			return o;
		}

		var lines = EditorLines().Select(l => l.TrimEnd()).ToList();
		if (lines.Count == 0) errors.Add("A node needs at least one line.");

		var original = _doc.Node(_nodeId) ?? new JsonObject();
		var node = (JsonObject)original.DeepClone();
		var created = new List<string>();
		string Target(string? raw)
		{
			var t = (raw ?? "").Trim();
			if (t.Length > 0 && t != newId && _doc.Node(t) == null && !created.Contains(t))
			{
				if (!Regex.IsMatch(t, "^[A-Za-z0-9_]+$")) errors.Add($"'{t}' isn't a valid node id.");
				else created.Add(t);
			}
			return t;
		}

		// lines
		node.Remove("say");
		SetOrdered(node, "lines", new JsonArray(lines.Select(l => (JsonNode)JsonValue.Create(l)!).ToArray()), NodeOrder);

		// topics (auto-create entries for [words] that have none, Twine style)
		var topics = new JsonObject();
		foreach (var row in _topics)
		{
			var key = (row.Key.Text ?? "").Trim().ToLowerInvariant();
			if (key.Length == 0) continue;
			if (topics.ContainsKey(key)) { errors.Add($"Link \"{row.Shown.Text}\" is listed twice."); continue; }
			var target = Target(GotoValue(row.Goto));
			var cond = row.If.Value;
			Cond($"Link \"{row.Shown.Text}\"", row.If);
			var fx = Fx($"Link \"{row.Shown.Text}\" do", row.Do);
			if (string.IsNullOrEmpty(cond) && fx == null && row.Original is not JsonObject)
			{
				topics[key] = target;
				continue;
			}
			var o = row.Original is JsonObject ro ? (JsonObject)ro.DeepClone() : new JsonObject();
			SetOrRemove(o, "goto", target.Length > 0 ? JsonValue.Create(target) : null, TopicOrder);
			SetOrRemove(o, "if", string.IsNullOrEmpty(cond) ? null : JsonValue.Create(cond), TopicOrder);
			SetOrRemove(o, "do", fx, TopicOrder);
			topics[key] = o;
		}
		foreach (var t in lines.SelectMany(l => Dialogue.Topics(l)).Select(t => t.TopicId).Distinct())
		{
			if (topics.ContainsKey(t)) continue;
			var target = SuggestNewNodeId(newId + "_" + Regex.Replace(t, @"[^a-z0-9_]+", "_"));
			topics[t] = Target(target);
		}
		SetOrRemove(node, "topics", topics.Count > 0 ? topics : null, NodeOrder);

		// choices
		var choices = new JsonArray();
		int ci = 0;
		foreach (var row in _choices)
		{
			ci++;
			var text = (row.Text.Text ?? "").Trim();
			if (text.Length == 0) { errors.Add($"Choice {ci} has no text."); continue; }
			var o = row.Original != null ? (JsonObject)row.Original.DeepClone() : new JsonObject();
			var cond = row.If.Value;
			Cond($"Choice {ci}", row.If);
			SetOrRemove(o, "text", JsonValue.Create(text), ChoiceOrder);
			SetOrRemove(o, "if", string.IsNullOrEmpty(cond) ? null : JsonValue.Create(cond), ChoiceOrder);
			var target = Target(GotoValue(row.Goto));
			SetOrRemove(o, "goto", target.Length > 0 ? JsonValue.Create(target) : null, ChoiceOrder);
			SetOrRemove(o, "do", Fx($"Choice {ci} do", row.Do), ChoiceOrder);
			choices.Add(o);
		}
		SetOrRemove(node, "choices", choices.Count > 0 ? choices : null, NodeOrder);

		// flow
		var g = Target(GotoValue(_goto));
		SetOrRemove(node, "goto", g.Length > 0 ? JsonValue.Create(g) : null, NodeOrder);
		SetOrRemove(node, "end", _end.IsChecked == true ? JsonValue.Create(true) : null, NodeOrder);
		var ending = _ending.SelectedItem as string;
		SetOrRemove(node, "ending", ending is null or "(none)" ? null : JsonValue.Create(ending), NodeOrder);
		var fxKind = _fx.SelectedItem as string;
		SetOrRemove(node, "fx", fxKind is null or "(none)" ? null : JsonValue.Create(fxKind), NodeOrder);
		var fxText = _fxText.Text?.Trim();
		SetOrRemove(node, "fxText", string.IsNullOrEmpty(fxText) ? null : JsonValue.Create(fxText), NodeOrder);
		SetOrRemove(node, "do", Fx("Node do", _do), NodeOrder);

		if (errors.Count > 0)
		{
			_problems.Foreground = Palette.Error;
			_problems.Text = string.Join("\n", errors.Distinct());
			return false;
		}

		bool changed = newId != _nodeId || !JsonNode.DeepEquals(node, original);
		if (changed)
		{
			var oldId = _nodeId;
			_doc.Edit($"Edit {oldId}", () =>
			{
				_doc.Nodes[oldId] = node;
				if (newId != oldId) _doc.RenameNode(oldId, newId);
				// New link targets become placeholder nodes (Twine style), placed next to whatever links to them.
				foreach (var c in created)
				{
					if (_doc.Node(c) == null) _doc.AddNode(c, default, "...");
					_doc.Layout.Remove(c);
				}
				GraphLayout.FillMissing(_doc);
			});
			_nodeId = newId;
			Title = $"{_doc.Name} · {newId}";
			_nodeIds.Clear();
			_nodeIds.AddRange(_doc.NodeIds);
			foreach (var c in _choices) FillGoto(c.Goto, GotoValue(c.Goto));
			foreach (var tr in _topics) FillGoto(tr.Goto, GotoValue(tr.Goto), forLink: true);
			FillGoto(_goto, GotoValue(_goto));
		}
		_initialSnapshot = Snapshot();
		_problems.Foreground = Palette.Start;
		_problems.Text = changed ? (created.Count > 0 ? $"Applied. Created {string.Join(", ", created)}." : "Applied.") : "No changes.";
		RefreshAfterApply();
		return true;
	}

	void RefreshAfterApply()
	{
		var node = _doc.Node(_nodeId);
		if (node == null) return;
		// Re-bind rows to the stored objects so later applies keep unknown fields.
		if (node["choices"] is JsonArray cs)
			for (int i = 0; i < Math.Min(cs.Count, _choices.Count); i++) _choices[i].Original = cs[i] as JsonObject;
		if (node["topics"] is JsonObject ts)
			foreach (var row in _topics)
				row.Original = ts[(row.Key.Text ?? "").Trim().ToLowerInvariant()];
		var known = _topics.Select(t => (t.Key.Text ?? "").Trim().ToLowerInvariant()).ToHashSet();
		if (node["topics"] is JsonObject ts2)
			foreach (var (k, v) in ts2.Where(kv => !known.Contains(kv.Key)).ToList())
				AddTopicRow(k, v, Dialogue.TopicLabel(node, k));
	}

	/// <summary>Set a key, inserting new keys in the house order so files stay tidy.</summary>
	static void SetOrdered(JsonObject o, string key, JsonNode value, string[] order)
	{
		if (o.ContainsKey(key))
		{
			o[key] = value;
			return;
		}
		int rank = Array.IndexOf(order, key);
		int insertAt = o.Count;
		if (rank >= 0)
		{
			insertAt = 0;
			int i = 0;
			foreach (var (k, _) in o)
			{
				i++;
				int r = Array.IndexOf(order, k);
				if (r >= 0 && r < rank) insertAt = i;
			}
		}
		o.Insert(insertAt, key, value);
	}

	static void SetOrRemove(JsonObject o, string key, JsonNode? value, string[] order)
	{
		if (value == null) o.Remove(key);
		else SetOrdered(o, key, value, order);
	}

	// ------------------------------------------------------------ Closing

	bool _closeConfirmed;

	async Task CloseAsk()
	{
		if (Snapshot() != _initialSnapshot)
		{
			int r = await Ui.Ask(this, "Unapplied changes", "Apply your changes to this node?", "Apply", "Discard", "Keep editing");
			if (r == 0 && !Apply()) return;
			if (r == 2 || r == -1) return;
		}
		_closeConfirmed = true;
		Close();
	}

	protected override void OnClosing(WindowClosingEventArgs e)
	{
		base.OnClosing(e);
		if (!_closeConfirmed && Snapshot() != _initialSnapshot)
		{
			e.Cancel = true;
			_ = CloseAsk();
		}
	}

	void OnKey(object? sender, KeyEventArgs e)
	{
		if (e.Key == Key.Enter && Ui.IsCommand(e.KeyModifiers))
		{
			if (Apply()) { _closeConfirmed = true; Close(); }
			e.Handled = true;
		}
		else if (e.Key == Key.Escape)
		{
			_ = CloseAsk();
			e.Handled = true;
		}
		else if (e.Key == Key.S && Ui.IsCommand(e.KeyModifiers))
		{
			Apply();
			SaveRequested?.Invoke();
			e.Handled = true;
		}
	}

	public event Action? SaveRequested;
}
