using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using StoryWriter.Model;
using StoryWriter.Runtime;

namespace StoryWriter.UI;

/// <summary>Edit the simulated save game: per-character stats, visits, endings, and global flags.</summary>
public sealed class StatePanel : Border
{
	readonly PreviewState _state;
	readonly Func<IEnumerable<DialogueDocument>> _docs;
	readonly StackPanel _root = new() { Spacing = 10, Margin = new Thickness(12, 12, 6, 12) };
	bool _editing;
	public Func<string?>? FocusHunk { get; set; }
	/// <summary>When set, a "Hide panel" button is shown in line with Reset.</summary>
	public Action? OnHide { get; set; }

	public StatePanel(PreviewState state, Func<IEnumerable<DialogueDocument>> docs)
	{
		_state = state;
		_docs = docs;
		Background = Palette.Panel;
		// A plain ScrollViewer (not a subclass, which wouldn't pick up the theme's template and so has no scrollbar).
		var scroll = new ScrollViewer
		{
			Content = _root,
			HorizontalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Disabled,
			VerticalScrollBarVisibility = Avalonia.Controls.Primitives.ScrollBarVisibility.Visible,
		};
		ScrollViewer.SetAllowAutoHide(scroll, false);
		Child = scroll;
		_state.Changed += () =>
		{
			if (!_editing) Rebuild();
		};
		Rebuild();
	}

	public void Rebuild()
	{
		_root.Children.Clear();
		var header = new DockPanel();
		if (OnHide != null)
		{
			var hide = Ui.Btn("◨ Hide panel", OnHide, "Hide the game state panel");
			DockPanel.SetDock(hide, Dock.Right);
			header.Children.Add(hide);
		}
		header.Children.Add(Ui.Row(8, Ui.Label("Game state", 14, Palette.Text, FontWeight.Bold),
			Ui.Btn("Reset", () => _state.Reset(), "Forget all stats, visits, endings and flags")));
		_root.Children.Add(header);

		var focus = FocusHunk?.Invoke();
		foreach (var doc in _docs().OrderBy(d => d.Id == focus ? 0 : 1))
			_root.Children.Add(HunkEditor(doc, doc.Id == focus));

		_root.Children.Add(Ui.Label("Flags", 13, Palette.Text, FontWeight.Bold));
		foreach (var (name, value) in _state.Flags.ToList())
		{
			var n = name;
			var row = new DockPanel();
			var del = Ui.Btn("✕", () => { _state.Flags.Remove(n); _state.NotifyChanged(); }, "Remove flag");
			DockPanel.SetDock(del, Dock.Right);
			row.Children.Add(del);
			var num = Number(value, v => _state.Flags[n] = v);
			DockPanel.SetDock(num, Dock.Right);
			row.Children.Add(num);
			row.Children.Add(Ui.Label("flag." + n, 12));
			_root.Children.Add(row);
		}
		var newFlag = new TextBox { PlaceholderText = "new flag name", FontSize = 12 };
		_root.Children.Add(Ui.Row(6, newFlag, Ui.Btn("Add", () =>
		{
			var f = (newFlag.Text ?? "").Trim().ToLowerInvariant();
			if (f.StartsWith("flag.")) f = f[5..];
			if (f.Length == 0) return;
			_state.Flags[f] = _state.Flags.GetValueOrDefault(f) + 1;
			_state.NotifyChanged();
		})));
	}

	Control HunkEditor(DialogueDocument doc, bool expanded)
	{
		var p = _state.Hunk(doc.Id);
		var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto"), RowSpacing = 4 };
		int row = 0;
		void Add(string label, Control c)
		{
			grid.RowDefinitions.Add(new RowDefinition(GridLength.Auto));
			var l = Ui.Label(label, 12, Palette.Muted);
			Grid.SetRow(l, row);
			Grid.SetRow(c, row);
			Grid.SetColumn(c, 1);
			grid.Children.Add(l);
			grid.Children.Add(c);
			row++;
		}
		Add("romance", Number(p.Romance, v => p.Romance = v));
		Add("friendship", Number(p.Friendship, v => p.Friendship = v));
		Add("friction", Number(p.Friction, v => p.Friction = v));
		Add("visits", Number(p.Visits, v => p.Visits = v));
		Add("met", Check(p.Met, v => p.Met = v));
		Add("fixed", Check(p.Fixed, v => p.Fixed = v));
		var ending = new ComboBox { ItemsSource = new[] { "(none)" }.Concat(Dialogue.Endings).ToList(), SelectedItem = string.IsNullOrEmpty(p.Ending) ? "(none)" : p.Ending, FontSize = 12, MinWidth = 140 };
		ending.SelectionChanged += (_, _) => Edit(() => p.Ending = ending.SelectedItem as string is { } s && s != "(none)" ? s : "");
		Add("ending", ending);
		var seen = Ui.Label($"{p.Seen.Count} nodes seen", 11, Palette.Faint);
		var clearSeen = Ui.Btn("clear", () => { p.Seen.Clear(); _state.NotifyChanged(); });
		Add("seen.*", Ui.Row(6, seen, clearSeen));
		var summary = $"{doc.Name}  ·  ♥\uFE0E{p.Romance} ☺{p.Friendship} ϟ{p.Friction}  ·  visits {p.Visits}{(p.Fixed ? "  ·  " + p.Ending : "")}";
		return new Expander
		{
			Header = new TextBlock { Text = summary, TextWrapping = TextWrapping.Wrap, FontSize = 12.5 },
			IsExpanded = expanded,
			Content = grid,
			HorizontalAlignment = HorizontalAlignment.Stretch,
		};
	}

	void Edit(Action a)
	{
		_editing = true;
		a();
		_state.NotifyChanged();
		_editing = false;
	}

	NumericUpDown Number(int value, Action<int> set)
	{
		var n = new NumericUpDown { Value = value, Increment = 1, FormatString = "0", Width = 120, FontSize = 12, Minimum = -99, Maximum = 999 };
		n.ValueChanged += (_, e) => Edit(() => set((int)(e.NewValue ?? 0)));
		return n;
	}

	CheckBox Check(bool value, Action<bool> set)
	{
		var c = new CheckBox { IsChecked = value };
		c.IsCheckedChanged += (_, _) => Edit(() => set(c.IsChecked == true));
		return c;
	}
}
