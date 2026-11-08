using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using StoryWriter.Model;

namespace StoryWriter.UI;

/// <summary>The variable names that "if" and "do" fields can pick from.</summary>
public static class Vars
{
	static readonly Regex FlagRx = new(@"flag\.[a-z0-9_]+", RegexOptions.Compiled | RegexOptions.IgnoreCase);

	/// <summary>Every flag.* any file sets or tests.</summary>
	public static List<string> Flags(IEnumerable<DialogueDocument> all)
	{
		var set = new SortedSet<string>(StringComparer.Ordinal);
		void Walk(JsonNode? n)
		{
			switch (n)
			{
				case JsonObject o:
					foreach (var (k, v) in o)
					{
						if (k == "do" && v is JsonObject d)
							foreach (var (dk, _) in d)
								if (dk.StartsWith("flag.", StringComparison.OrdinalIgnoreCase)) set.Add(dk.ToLowerInvariant());
						if (k == "if" && Dialogue.Str(v) is { } c)
							foreach (Match m in FlagRx.Matches(c)) set.Add(m.Value.ToLowerInvariant());
						Walk(v);
					}
					break;
				case JsonArray a:
					foreach (var x in a) Walk(x);
					break;
			}
		}
		foreach (var d in all) Walk(d.Root);
		return set.ToList();
	}

	/// <summary>Things a "do" can add to: this character's stats, other characters' stats, flags.</summary>
	public static List<string> Effects(DialogueDocument doc, IEnumerable<DialogueDocument> all)
	{
		var list = new List<string>(Dialogue.Stats);
		foreach (var d in all.Where(d => d.Id != doc.Id))
			foreach (var s in Dialogue.Stats) list.Add($"{d.Id}.{s}");
		list.AddRange(Flags(all));
		return list;
	}

	/// <summary>Things an "if" can test.</summary>
	public static List<string> Conditions(DialogueDocument doc, IEnumerable<DialogueDocument> all)
	{
		var docs = all.ToList();
		var list = new List<string>(Dialogue.Stats) { "visits", "met", "fixed", "fixedcount" };
		list.AddRange(Dialogue.Endings.Select(e => "ending_" + e));
		foreach (var d in docs.Where(d => d.Id != doc.Id))
		{
			foreach (var s in Dialogue.Stats) list.Add($"{d.Id}.{s}");
			list.Add($"{d.Id}.visits");
			list.Add($"{d.Id}.fixed");
		}
		list.AddRange(Flags(docs));
		list.AddRange(doc.NodeIds.Select(n => "seen." + n));
		return list;
	}

	public static ComboBox Combo(IEnumerable<string> options, string current, double minWidth = 150)
	{
		var items = options.ToList();
		if (current.Length > 0 && !items.Contains(current)) items.Insert(0, current);
		var cb = new ComboBox { ItemsSource = items, IsEditable = true, MinWidth = minWidth, FontSize = 12, HorizontalAlignment = HorizontalAlignment.Stretch };
		cb.Text = current;
		if (current.Length > 0) cb.SelectedItem = current;
		return cb;
	}

	public static string ComboValue(ComboBox cb) => (cb.Text ?? (cb.SelectedItem as string) ?? "").Trim().ToLowerInvariant();
}

/// <summary>Guided "do": rows of (variable dropdown, amount to add).</summary>
public sealed class EffectsEditor : StackPanel
{
	readonly List<string> _options;
	readonly StackPanel _rows = new() { Spacing = 4 };
	readonly List<(ComboBox name, NumericUpDown amount, Control view)> _list = new();
	public event Action? Changed;

	public EffectsEditor(IEnumerable<string> options, JsonObject? initial)
	{
		_options = options.ToList();
		Spacing = 4;
		if (initial != null)
			foreach (var (k, v) in initial) AddRow(k, Dialogue.Num(v));
		_rows.IsVisible = _list.Count > 0;
		Children.Add(_rows);
		var add = Ui.Btn("+ Add effect", () =>
		{
			var used = _list.Select(r => Vars.ComboValue(r.name)).ToHashSet();
			AddRow(_options.FirstOrDefault(o => !used.Contains(o)) ?? "", 1);
			Changed?.Invoke();
		}, "Add something to change when this happens");
		add.HorizontalAlignment = HorizontalAlignment.Left;
		add.Padding = new Thickness(8, 2);
		Children.Add(add);
	}

	void AddRow(string name, int amount)
	{
		var cb = Vars.Combo(_options, name.ToLowerInvariant());
		var num = new NumericUpDown { Value = amount, Increment = 1, FormatString = "+0;-0;0", Minimum = -99, Maximum = 99, Width = 110, FontSize = 12 };
		var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto,Auto"), ColumnSpacing = 6 };
		var del = Ui.Btn("✕", () =>
		{
			_list.RemoveAll(r => r.view == grid);
			_rows.Children.Remove(grid);
			_rows.IsVisible = _list.Count > 0;
			Changed?.Invoke();
		}, "Remove effect");
		Grid.SetColumn(num, 1);
		Grid.SetColumn(del, 2);
		grid.Children.Add(cb);
		grid.Children.Add(num);
		grid.Children.Add(del);
		cb.SelectionChanged += (_, _) => Changed?.Invoke();
		cb.PropertyChanged += (_, e) => { if (e.Property == ComboBox.TextProperty) Changed?.Invoke(); };
		num.ValueChanged += (_, _) => Changed?.Invoke();
		_list.Add((cb, num, grid));
		_rows.Children.Add(grid);
		_rows.IsVisible = true;
	}

	/// <summary>Null when there are no effects. Sets <paramref name="error"/> for blank or repeated variables.</summary>
	public JsonObject? Value(out string? error)
	{
		error = null;
		var o = new JsonObject();
		foreach (var (name, amount, _) in _list)
		{
			var key = Vars.ComboValue(name);
			if (key.Length == 0) { error = "pick a variable for every effect"; return null; }
			if (!Regex.IsMatch(key, @"^[a-z_][a-z0-9_.]*$")) { error = $"'{key}' isn't a valid variable name"; return null; }
			if (o.ContainsKey(key)) { error = $"'{key}' is listed twice"; return null; }
			o[key] = (int)(amount.Value ?? 0);
		}
		return o.Count > 0 ? o : null;
	}

	public string Snapshot => string.Join(",", _list.Select(r => $"{Vars.ComboValue(r.name)}={r.amount.Value}"));
}

/// <summary>Guided "if": rows of (variable, comparison, number) joined by all-of / any-of. Unusual expressions fall back to text.</summary>
public sealed class ConditionEditor : StackPanel
{
	static readonly string[] Ops = { "is set", "is not set", "==", "!=", ">=", "<=", ">", "<" };
	static readonly Regex ClauseRx = new(@"^(!)?\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(==|!=|>=|<=|>|<)?\s*(-?\d+)?$", RegexOptions.Compiled);

	readonly List<string> _vars;
	readonly StackPanel _rows = new() { Spacing = 4 };
	readonly List<(ComboBox name, ComboBox op, NumericUpDown value, Control view)> _list = new();
	readonly ComboBox _join = new() { ItemsSource = new[] { "all of these (AND)", "any of these (OR)" }, SelectedIndex = 0, FontSize = 12, VerticalAlignment = VerticalAlignment.Center };
	readonly TextBox _text = new() { FontSize = 12, IsVisible = false };
	readonly TextBlock _always = Ui.Label("always", 12, Palette.Muted);
	readonly TextBlock _error = new() { FontSize = 11, Foreground = Palette.Error, TextWrapping = TextWrapping.Wrap, IsVisible = false };
	readonly Button _toggle;
	readonly Button _add;
	bool _asText;
	public event Action? Changed;

	public ConditionEditor(IEnumerable<string> vars, string? initial, string alwaysText = "always")
	{
		_vars = vars.ToList();
		Spacing = 4;
		_always.Text = alwaysText;
		_add = Ui.Btn("+ condition", () => { AddRow(_vars.FirstOrDefault() ?? "", "==", 0); Refresh(); Changed?.Invoke(); }, "Add a test that must hold");
		_toggle = Ui.Btn("edit as text", ToggleText, "Type the expression by hand (supports &&, ||, !, parentheses)");
		_join.SelectionChanged += (_, _) => { Refresh(); Changed?.Invoke(); };
		_text.TextChanged += (_, _) => { Validate(); Changed?.Invoke(); };
		_add.Padding = new Thickness(8, 2);
		_toggle.Padding = new Thickness(8, 2);
		var bar = Ui.Row(6, _add, _join, _toggle);
		Children.Add(_always);
		Children.Add(_rows);
		Children.Add(_text);
		Children.Add(bar);
		Children.Add(_error);
		Load(initial ?? "");
	}

	void Load(string expr)
	{
		_list.Clear();
		_rows.Children.Clear();
		if (TryParse(expr, out var any, out var clauses))
		{
			_asText = false;
			_join.SelectedIndex = any ? 1 : 0;
			foreach (var c in clauses) AddRow(c.name, c.op, c.value);
		}
		else
		{
			_asText = true;
			_text.Text = expr;
		}
		Refresh();
	}

	record Clause(string name, string op, int value);

	static bool TryParse(string expr, out bool any, out List<Clause> clauses)
	{
		any = false;
		clauses = new();
		expr = (expr ?? "").Trim();
		if (expr.Length == 0 || expr.Equals("true", StringComparison.OrdinalIgnoreCase)) return true;
		if (expr.Contains('(') || expr.Contains(')')) return false;
		bool hasAnd = expr.Contains("&&"), hasOr = expr.Contains("||");
		if (hasAnd && hasOr) return false;
		any = hasOr;
		foreach (var part in expr.Split(any ? "||" : "&&"))
		{
			var m = ClauseRx.Match(part.Trim());
			if (!m.Success) return false;
			bool neg = m.Groups[1].Success;
			var name = m.Groups[2].Value.ToLowerInvariant();
			if (m.Groups[3].Success)
			{
				if (neg || !m.Groups[4].Success) return false;
				clauses.Add(new Clause(name, m.Groups[3].Value, int.Parse(m.Groups[4].Value)));
			}
			else
			{
				if (m.Groups[4].Success) return false;
				clauses.Add(new Clause(name, neg ? "is not set" : "is set", 0));
			}
		}
		return true;
	}

	void AddRow(string name, string op, int value)
	{
		var cb = Vars.Combo(_vars, name);
		var opBox = new ComboBox { ItemsSource = Ops, SelectedItem = op, FontSize = 12, MinWidth = 96 };
		var num = new NumericUpDown { Value = value, Increment = 1, FormatString = "0", Minimum = -999, Maximum = 999, Width = 100, FontSize = 12, IsVisible = op is not ("is set" or "is not set") };
		var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto,Auto,Auto"), ColumnSpacing = 6 };
		var del = Ui.Btn("✕", () =>
		{
			_list.RemoveAll(r => r.view == grid);
			_rows.Children.Remove(grid);
			Refresh();
			Changed?.Invoke();
		}, "Remove this test");
		Grid.SetColumn(opBox, 1);
		Grid.SetColumn(num, 2);
		Grid.SetColumn(del, 3);
		grid.Children.Add(cb);
		grid.Children.Add(opBox);
		grid.Children.Add(num);
		grid.Children.Add(del);
		cb.SelectionChanged += (_, _) => Changed?.Invoke();
		cb.PropertyChanged += (_, e) => { if (e.Property == ComboBox.TextProperty) Changed?.Invoke(); };
		opBox.SelectionChanged += (_, _) =>
		{
			num.IsVisible = opBox.SelectedItem is string s && s is not ("is set" or "is not set");
			Changed?.Invoke();
		};
		num.ValueChanged += (_, _) => Changed?.Invoke();
		_list.Add((cb, opBox, num, grid));
		_rows.Children.Add(grid);
	}

	void Refresh()
	{
		_rows.IsVisible = !_asText && _list.Count > 0;
		_text.IsVisible = _asText;
		_add.IsVisible = !_asText;
		_join.IsVisible = !_asText && _list.Count > 1;
		_always.IsVisible = !_asText && _list.Count == 0;
		_toggle.Content = _asText ? "use builder" : "edit as text";
		Validate();
	}

	void ToggleText()
	{
		if (!_asText)
		{
			_text.Text = BuildValue();
			_asText = true;
		}
		else if (TryParse(_text.Text ?? "", out _, out _))
		{
			Load(_text.Text ?? "");
		}
		else
		{
			_error.Text = "That expression is too complex for the builder; keep editing it as text.";
			_error.IsVisible = true;
			return;
		}
		Refresh();
		Changed?.Invoke();
	}

	string BuildValue()
	{
		var parts = _list.Select(r =>
		{
			var name = Vars.ComboValue(r.name);
			return (r.op.SelectedItem as string) switch
			{
				"is set" or null => name,
				"is not set" => "!" + name,
				var op => $"{name} {op} {(int)(r.value.Value ?? 0)}",
			};
		}).ToList();
		return string.Join(_join.SelectedIndex == 1 ? " || " : " && ", parts);
	}

	void Validate()
	{
		_error.Text = Error ?? "";
		_error.IsVisible = _error.Text.Length > 0;
	}

	/// <summary>The expression, or "" for "always".</summary>
	public string Value => _asText ? (_text.Text ?? "").Trim() : BuildValue();

	public string? Error
	{
		get
		{
			if (!_asText && _list.Any(r => Vars.ComboValue(r.name).Length == 0)) return "pick a variable for every test";
			return Runtime.Condition.Check(Value);
		}
	}
}
