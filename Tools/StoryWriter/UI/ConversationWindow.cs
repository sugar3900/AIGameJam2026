using System.Text.Json.Nodes;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using StoryWriter.Model;

namespace StoryWriter.UI;

/// <summary>Conversation-level settings: who he is, the entries (which node each visit starts at) and the ending cards.</summary>
public sealed class ConversationWindow : Window
{
	static readonly string[] RootOrder = { "id", "name", "malady", "room", "tagline", "look", "entries", "endings", "nodes" };

	readonly DialogueDocument _doc;
	readonly Func<IEnumerable<DialogueDocument>> _allDocs;
	readonly Dictionary<string, TextBox> _meta = new();
	readonly StackPanel _entryRows = new() { Spacing = 6 };
	readonly List<(JsonObject? original, ConditionEditor cond, ComboBox node, Control view)> _entries = new();
	readonly Dictionary<string, (TextBox title, TextBox text)> _endings = new();
	readonly TextBlock _problems = Ui.Label("", 12, Palette.Error);

	public ConversationWindow(DialogueDocument doc, Func<IEnumerable<DialogueDocument>> allDocs)
	{
		_doc = doc;
		_allDocs = allDocs;
		Title = $"{doc.Name} · conversation settings";
		Width = 860;
		Height = 760;
		Background = Palette.Panel;
		WindowStartupLocation = WindowStartupLocation.CenterOwner;

		var metaGrid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,*"), ColumnSpacing = 10, RowSpacing = 8 };
		int i = 0;
		foreach (var (key, help) in new[]
		{
			("id", "Matches AFixHimMalady.HunkId in the level"),
			("name", "Display name; {name} in lines"),
			("malady", "Shown on the intro card and dialogue header"),
			("room", "Matches AFixHimRoom.RoomId"),
			("tagline", "Intro card tagline"),
		})
		{
			var tb = new TextBox { Text = Dialogue.Str(doc.Root[key]) ?? "" };
			_meta[key] = tb;
			var f = Ui.Field(key, tb, help);
			if (i % 2 == 1) Grid.SetColumn(f, 1);
			if (metaGrid.RowDefinitions.Count <= i / 2) metaGrid.RowDefinitions.Add(new RowDefinition(GridLength.Auto));
			Grid.SetRow(f, i / 2);
			metaGrid.Children.Add(f);
			i++;
		}

		foreach (var e in doc.Entries.OfType<JsonObject>()) AddEntry(e);

		var endingPanel = new StackPanel { Spacing = 10 };
		foreach (var key in Dialogue.Endings)
		{
			var card = doc.EndingCards[key] as JsonObject;
			var title = new TextBox { Text = Dialogue.Str(card?["title"]) ?? "", PlaceholderText = "Title" };
			var text = new TextBox { Text = Dialogue.Str(card?["text"]) ?? "", PlaceholderText = "Ending card text", TextWrapping = TextWrapping.Wrap, AcceptsReturn = false, MinHeight = 54 };
			_endings[key] = (title, text);
			endingPanel.Children.Add(new Border
			{
				Background = Palette.Card,
				CornerRadius = new CornerRadius(6),
				Padding = new Thickness(10),
				Child = Ui.Col(6, Ui.Label(key.Replace('_', ' ').ToUpperInvariant(), 11, Palette.Ending, FontWeight.Bold), title, text),
			});
		}

		var body = Ui.Col(14,
			Ui.Label("Character", 15, Palette.Text, FontWeight.Bold), metaGrid,
			Ui.Label("Entries", 15, Palette.Text, FontWeight.Bold),
			Ui.Label("Checked top to bottom each time Rosie clicks his fixture; the first true condition picks the starting node. `visits` counts finished conversations, `fixed` is set by an ending.", 11, Palette.Muted),
			_entryRows,
			Ui.Btn("+ Add entry", () => AddEntry(null)),
			Ui.Label("Ending cards", 15, Palette.Text, FontWeight.Bold),
			endingPanel);

		var buttons = Ui.Row(8, Ui.Btn("Cancel", Close), Ui.Btn("OK", () => { if (Apply()) Close(); }, accent: true));
		buttons.HorizontalAlignment = HorizontalAlignment.Right;
		var bottom = new DockPanel { Margin = new Thickness(16, 8, 16, 14) };
		DockPanel.SetDock(buttons, Dock.Right);
		bottom.Children.Add(buttons);
		bottom.Children.Add(_problems);

		var root = new DockPanel();
		DockPanel.SetDock(bottom, Dock.Bottom);
		root.Children.Add(bottom);
		root.Children.Add(new ScrollViewer { Content = new Border { Padding = new Thickness(18, 14), Child = body } });
		Content = root;
	}

	void AddEntry(JsonObject? e)
	{
		var cond = new ConditionEditor(Vars.Conditions(_doc, _allDocs()), Dialogue.Str(e?["if"]) ?? "true", "always (true)");
		var kinds = _doc.NodeKinds();
		var current = Dialogue.Str(e?["node"]) ?? "";
		var items = _doc.NodeIds.Where(id => kinds.GetValueOrDefault(id) != NodeKind.Hypertext).ToList();
		if (current.Length > 0 && !items.Contains(current)) items.Add(current);
		var node = new ComboBox { ItemsSource = items, SelectedItem = current.Length > 0 ? current : null, PlaceholderText = "pick a node", MinWidth = 180 };
		(JsonObject?, ConditionEditor, ComboBox, Control) row = default;
		var tools = Ui.Row(2,
			Ui.Btn("↑", () => Move(row, -1)),
			Ui.Btn("↓", () => Move(row, 1)),
			Ui.Btn("✕", () => { _entries.Remove(row); _entryRows.Children.Remove(row.Item4!); }));
		var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,2*,Auto,*,Auto"), ColumnSpacing = 8 };
		var ifl = Ui.Label("if", 12, Palette.Condition, FontWeight.Bold);
		var arrow = Ui.Label("→", 14, Palette.Start);
		foreach (var c in new Control[] { ifl, arrow, node, tools }) c.VerticalAlignment = VerticalAlignment.Top;
		ifl.Margin = new Thickness(0, 6, 0, 0);
		arrow.Margin = new Thickness(0, 4, 0, 0);
		Grid.SetColumn(cond, 1);
		Grid.SetColumn(arrow, 2);
		Grid.SetColumn(node, 3);
		Grid.SetColumn(tools, 4);
		grid.Children.Add(ifl);
		grid.Children.Add(cond);
		grid.Children.Add(arrow);
		grid.Children.Add(node);
		grid.Children.Add(tools);
		row = (e, cond, node, grid);
		_entries.Add(row);
		_entryRows.Children.Add(grid);
	}

	void Move((JsonObject?, ConditionEditor, ComboBox, Control) row, int dir)
	{
		int i = _entries.IndexOf(row), j = i + dir;
		if (i < 0 || j < 0 || j >= _entries.Count) return;
		(_entries[i], _entries[j]) = (_entries[j], _entries[i]);
		_entryRows.Children.Clear();
		foreach (var r in _entries) _entryRows.Children.Add(r.view);
	}

	bool Apply()
	{
		var errors = new List<string>();
		var entries = new JsonArray();
		foreach (var (original, condBox, nodeBox, _) in _entries)
		{
			var cond = condBox.Value;
			var node = nodeBox.SelectedItem as string ?? "";
			if (node.Length == 0) continue;
			if (condBox.Error is { } err) errors.Add($"Entry '{node}': {err}");
			if (_doc.Node(node) == null) errors.Add($"Entry → '{node}': no such node");
			var o = original != null ? (JsonObject)original.DeepClone() : new JsonObject();
			o["if"] = string.IsNullOrEmpty(cond) ? "true" : cond;
			o["node"] = node;
			entries.Add(o);
		}
		if (errors.Count > 0)
		{
			_problems.Text = string.Join("\n", errors);
			return false;
		}

		var root = (JsonObject)_doc.Root.DeepClone();
		foreach (var (key, tb) in _meta)
		{
			var v = tb.Text ?? "";
			if (root.ContainsKey(key) || v.Length > 0) Set(root, key, JsonValue.Create(v)!);
		}
		Set(root, "entries", entries);
		var endings = root["endings"] as JsonObject ?? new JsonObject();
		foreach (var (key, (title, text)) in _endings)
		{
			var t = title.Text ?? "";
			var x = text.Text ?? "";
			if (endings[key] is JsonObject card)
			{
				card["title"] = t;
				card["text"] = x;
			}
			else if (t.Length > 0 || x.Length > 0)
			{
				endings[key] = new JsonObject { ["title"] = t, ["text"] = x };
			}
		}
		Set(root, "endings", endings);

		if (!JsonNode.DeepEquals(root, _doc.Root))
		{
			_doc.Edit("Conversation settings", () =>
			{
				foreach (var key in new[] { "id", "name", "malady", "room", "tagline", "entries", "endings" })
				{
					if (root[key] is { } v) Set(_doc.Root, key, v.DeepClone());
				}
			});
		}
		return true;
	}

	static void Set(JsonObject o, string key, JsonNode value)
	{
		if (o.ContainsKey(key))
		{
			o[key] = value;
			return;
		}
		int rank = Array.IndexOf(RootOrder, key), insertAt = 0, i = 0;
		foreach (var (k, _) in o)
		{
			i++;
			int r = Array.IndexOf(RootOrder, k);
			if (r >= 0 && r < rank) insertAt = i;
		}
		o.Insert(insertAt, key, value);
	}
}
