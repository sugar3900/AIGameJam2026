using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Platform.Storage;
using Avalonia.Threading;
using AvaloniaEdit;
using StoryWriter.Graph;
using StoryWriter.Model;
using StoryWriter.Runtime;

namespace StoryWriter.UI;

public sealed class MainWindow : Window
{
	Workspace? _ws;
	DialogueDocument? _current;
	List<Issue> _issues = new();

	// Graph tab
	readonly GraphView _graph = new();
	readonly ListBox _docList = new() { Background = Palette.Panel };
	readonly TextBlock _docTitle = Ui.Label("", 16, Palette.Text, FontWeight.Bold);
	readonly TextBlock _zoomLabel = Ui.Label("", 11, Palette.Muted);
	readonly PreviewState _graphState = new();
	readonly PreviewPanel _graphPreview;
	readonly StatePanel _graphStatePanel;
	readonly TabControl _sideTabs = new();

	// Play tab
	readonly PreviewState _playState = new();
	readonly PreviewPanel _playPanel;
	readonly StatePanel _playStatePanel;
	readonly StackPanel _playCast = new() { Spacing = 8 };

	// Chrome
	readonly TabControl _modeTabs = new();
	readonly TextBlock _folderLabel = Ui.Label("", 12, Palette.Muted);
	readonly ListBox _issueList = new() { Background = Palette.Panel, MaxHeight = 170 };
	readonly Expander _issuePanel = new() { HorizontalAlignment = HorizontalAlignment.Stretch };
	readonly TextBlock _status = Ui.Label("", 11, Palette.Muted);
	readonly Button _undo, _redo, _save;
	readonly Dictionary<(DialogueDocument, string), NodeEditorWindow> _editors = new();
	readonly DispatcherTimer _validateTimer = new() { Interval = TimeSpan.FromMilliseconds(250) };

	public MainWindow(string? folder)
	{
		Title = "Story Writer";
		Width = 1500;
		Height = 920;
		MinWidth = 900;
		MinHeight = 600;
		Background = Palette.Panel;

		_graphPreview = new PreviewPanel(Find, _graphState);
		_graphStatePanel = new StatePanel(_graphState, Docs) { FocusHunk = () => _current?.Id };
		_playPanel = new PreviewPanel(Find, _playState);
		_playStatePanel = new StatePanel(_playState, Docs) { FocusHunk = () => _playPanel.HunkId };

		_undo = Ui.Btn("↶ Undo", Undo, "⌘/Ctrl+Z");
		_redo = Ui.Btn("↷ Redo", Redo, "⌘/Ctrl+Shift+Z");
		_save = Ui.Btn("Save", () => Save(_current), "⌘/Ctrl+S", accent: true);

		Content = BuildLayout();
		WireGraph();
		WirePlay();
		_validateTimer.Tick += (_, _) =>
		{
			_validateTimer.Stop();
			Revalidate();
		};
		AddHandler(KeyDownEvent, OnWindowKey, RoutingStrategies.Tunnel);

		folder ??= AppSettings.LastFolder is { } last && Directory.Exists(last) ? last : ProjectPaths.DefaultDialogueDir();
		if (folder != null && Directory.Exists(folder)) OpenFolder(folder);
		else _folderLabel.Text = "No dialogue folder open — use Open Folder…";
	}

	DialogueDocument? Find(string id) => _ws?.Find(id);
	IEnumerable<DialogueDocument> Docs() => _ws?.Docs ?? Enumerable.Empty<DialogueDocument>();

	// ------------------------------------------------------------------ Layout

	Control BuildLayout()
	{
		// Top bar
		var top = new DockPanel { Background = Palette.PanelAlt, Margin = new Thickness(0) };
		var brand = Ui.Row(8, Ui.Label("✎ Story Writer", 15, Palette.Hypertext, FontWeight.Bold), _folderLabel);
		brand.Margin = new Thickness(14, 8);
		var actions = Ui.Row(6,
			Ui.Btn("Open Folder…", () => _ = PickFolder(), "Open a folder of dialogue JSON (⌘/Ctrl+O)"),
			Ui.Btn("+ Conversation", () => _ = NewConversation(), "Create a new character dialogue file"),
			_undo, _redo, _save,
			Ui.Btn("Save All", SaveAll, "⌘/Ctrl+Shift+S"),
			Ui.Btn("Reload", () => _ = ReloadCurrent(), "Re-read the current file from disk"));
		actions.Margin = new Thickness(8, 6, 14, 6);
		DockPanel.SetDock(actions, Dock.Right);
		top.Children.Add(actions);
		top.Children.Add(brand);

		_modeTabs.Items.Add(new TabItem { Header = "Graph", Content = GraphTab() });
		_modeTabs.Items.Add(new TabItem { Header = "Play-through", Content = PlayTab() });
		_modeTabs.Padding = new Thickness(0);

		_issuePanel.Content = _issueList;
		_issuePanel.Header = "Problems";
		_issueList.SelectionChanged += (_, _) =>
		{
			if (_issueList.SelectedItem is ListBoxItem { Tag: Issue i }) JumpTo(i.DocId, i.NodeId);
		};

		var statusBar = new Border { Background = Palette.PanelAlt, Padding = new Thickness(12, 4), Child = _status };

		var root = new DockPanel();
		DockPanel.SetDock(top, Dock.Top);
		DockPanel.SetDock(statusBar, Dock.Bottom);
		DockPanel.SetDock(_issuePanel, Dock.Bottom);
		root.Children.Add(top);
		root.Children.Add(statusBar);
		root.Children.Add(_issuePanel);
		root.Children.Add(_modeTabs);
		return root;
	}

	Control GraphTab()
	{
		var sidebar = new DockPanel { Background = Palette.Panel };
		var sideHeader = Ui.Caption("CONVERSATIONS");
		sideHeader.Margin = new Thickness(12, 10, 12, 6);
		DockPanel.SetDock(sideHeader, Dock.Top);
		sidebar.Children.Add(sideHeader);
		sidebar.Children.Add(_docList);
		_docList.SelectionChanged += (_, _) =>
		{
			if (_docList.SelectedItem is ListBoxItem { Tag: DialogueDocument d } && d != _current) ShowDoc(d);
		};

		var toolbar = new WrapPanel { Margin = new Thickness(10, 6) };
		foreach (var c in new Control[]
		{
			_docTitle,
			new Border { Width = 14 },
			Ui.Btn("► Preview from start", () => PreviewFrom(null), "Play this conversation from its entries using the preview state", accent: true),
			Ui.Btn("► From selected", () => { if (_graph.SelectedId != null) PreviewFrom(_graph.SelectedId); }, "Play from the selected node (P)"),
			Ui.Btn("+ Node", () => _graph.NewNodeInView(), "New node in the middle of the view"),
			Ui.Btn("Conversation…", () => EditConversation(), "Name, entries (start conditions) and ending cards"),
			Ui.Btn("Fit", _graph.FitToView, "F"),
			Ui.Btn("Auto-arrange", _graph.AutoArrange, "Lay the nodes out again by visit lane"),
			Ui.Btn("−", () => _graph.SetZoom(_graph.Zoom / 1.2)),
			_zoomLabel,
			Ui.Btn("+", () => _graph.SetZoom(_graph.Zoom * 1.2)),
		})
		{
			c.Margin = new Thickness(0, 0, 6, 0);
			toolbar.Children.Add(c);
		}
		var legend = Ui.Row(4,
			Ui.Chip("story", Palette.Story), Ui.Chip("LINK = hypertext", Palette.Hypertext), Ui.Chip("ending", Palette.Ending),
			Ui.Chip("IF condition", Palette.Condition), Ui.Chip("entry", Palette.Start),
			Ui.Label("Double-click a node to edit · drag ● to link (Alt = hypertext link) · right-click for more · ⌘-scroll to zoom", 11, Palette.Faint));
		legend.Margin = new Thickness(10, 0, 10, 6);

		var graphArea = new DockPanel();
		DockPanel.SetDock(toolbar, Dock.Top);
		DockPanel.SetDock(legend, Dock.Top);
		graphArea.Children.Add(toolbar);
		graphArea.Children.Add(legend);
		graphArea.Children.Add(_graph);

		_sideTabs.Items.Add(new TabItem { Header = "Preview", Content = _graphPreview });
		_sideTabs.Items.Add(new TabItem { Header = "State", Content = _graphStatePanel });

		var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("210,*,4,430") };
		grid.Children.Add(sidebar);
		Grid.SetColumn(graphArea, 1);
		grid.Children.Add(graphArea);
		var split = new GridSplitter { Background = Palette.PanelAlt, ResizeDirection = GridResizeDirection.Columns };
		Grid.SetColumn(split, 2);
		grid.Children.Add(split);
		Grid.SetColumn(_sideTabs, 3);
		grid.Children.Add(_sideTabs);
		return grid;
	}

	Control PlayTab()
	{
		var castHeader = Ui.Col(8,
			Ui.Label("Play-through", 16, Palette.Text, FontWeight.Bold),
			Ui.Label("Plays every conversation with one shared save, like the game: pick a character and play all of his visits through to his ending, then move on to the next.", 11, Palette.Muted),
			Ui.Btn("► Play everything (fresh save)", PlayEverything, accent: true),
			Ui.Btn("Reset save", () => { _playState.Reset(); _playPanel.Stop(); }));
		var left = new ScrollViewer { Content = Ui.Col(14, castHeader, _playCast), Padding = new Thickness(14), Background = Palette.Panel };

		var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("280,*,4,340") };
		grid.Children.Add(left);
		var center = new Border { Child = _playPanel, BorderBrush = Palette.PanelAlt, BorderThickness = new Thickness(1, 0) };
		Grid.SetColumn(center, 1);
		grid.Children.Add(center);
		var split = new GridSplitter { Background = Palette.PanelAlt };
		Grid.SetColumn(split, 2);
		grid.Children.Add(split);
		Grid.SetColumn(_playStatePanel, 3);
		grid.Children.Add(_playStatePanel);
		return grid;
	}

	// ------------------------------------------------------------------ Workspace

	void OpenFolder(string folder)
	{
		_ws?.Dispose();
		foreach (var w in _editors.Values.ToList()) w.Close();
		_ws = new Workspace(folder);
		_ws.DocsChanged += OnDocsChanged;
		_ws.ExternalConflict += d => _ = OnConflict(d);
		AppSettings.LastFolder = folder;
		_folderLabel.Text = folder;
		_graphState.Reset();
		_playState.Reset();
		_graphPreview.Stop();
		_playPanel.Stop();
		OnDocsChanged();
		ShowDoc(_ws.Docs.FirstOrDefault());
		foreach (var e in _ws.LoadErrors) _status.Text = "Couldn't load " + e;
	}

	async Task PickFolder()
	{
		if (!await ConfirmDiscard("open another folder")) return;
		var res = await StorageProvider.OpenFolderPickerAsync(new FolderPickerOpenOptions { Title = "Open dialogue folder", AllowMultiple = false });
		var path = res.FirstOrDefault()?.TryGetLocalPath();
		if (path != null) OpenFolder(path);
	}

	void OnDocsChanged()
	{
		RefreshDocList();
		RefreshPlayCast();
		UpdateChrome();
		_validateTimer.Stop();
		_validateTimer.Start();
		foreach (var ((doc, id), w) in _editors.ToList())
			if (_ws?.Docs.Contains(doc) != true) w.Close();
		if (_current != null && _ws?.Docs.Contains(_current) != true) ShowDoc(_ws?.Docs.FirstOrDefault());
	}

	void RefreshDocList()
	{
		var items = new List<ListBoxItem>();
		ListBoxItem? selected = null;
		foreach (var d in Docs())
		{
			int errs = _issues.Count(i => i.DocId == d.Id && i.IsError), warns = _issues.Count(i => i.DocId == d.Id && !i.IsError);
			var badge = errs > 0 ? Ui.Chip($"{errs}", Palette.Error) : warns > 0 ? Ui.Chip($"{warns}", Palette.Warn) : null;
			var nameRow = Ui.Row(6, Ui.Label(d.Name + (d.Dirty ? "  •" : ""), 14, Palette.Text, FontWeight.SemiBold));
			if (badge != null) nameRow.Children.Add(badge);
			var item = new ListBoxItem
			{
				Tag = d,
				Padding = new Thickness(12, 6),
				Content = Ui.Col(1, nameRow,
					Ui.Label($"{d.FileName} · {d.Nodes.Count} nodes", 11, Palette.Muted),
					Ui.Label(Dialogue.Str(d.Root["malady"]) ?? "", 11, Palette.Faint)),
			};
			items.Add(item);
			if (d == _current) selected = item;
		}
		_docList.ItemsSource = items;
		_docList.SelectedItem = selected;
	}

	void ShowDoc(DialogueDocument? d)
	{
		if (_current != null) _current.Changed -= OnCurrentChanged;
		_current = d;
		if (_current != null) _current.Changed += OnCurrentChanged;
		_graph.Document = d;
		_graph.EvaluateCondition = null;
		if (_graphPreview.HunkId == d?.Id && _graphPreview.IsPlaying)
		{
			_graph.EvaluateCondition = c => _graphState.IsTrue(d!.Id, c);
			_graph.SetPreviewNode(_graphPreview.Runner.ActiveNodeId);
		}
		_graph.NodeIssues = IssuesFor(d);
		_docTitle.Text = d?.Name ?? "";
		_graphStatePanel.Rebuild();
		RefreshDocList();
		UpdateChrome();
	}

	void OnCurrentChanged()
	{
		UpdateChrome();
		_validateTimer.Stop();
		_validateTimer.Start();
	}

	void UpdateChrome()
	{
		_undo.IsEnabled = _current?.CanUndo == true;
		_redo.IsEnabled = _current?.CanRedo == true;
		ToolTip.SetTip(_undo, _current?.UndoLabel is { } l ? $"Undo {l} (⌘/Ctrl+Z)" : "Undo");
		_save.IsEnabled = _current?.Dirty == true;
		Title = _current == null ? "Story Writer" : $"Story Writer — {_current.FileName}{(_current.Dirty ? " •" : "")}";
		_zoomLabel.Text = $"{_graph.Zoom * 100:0}%";
		var dirty = Docs().Count(d => d.Dirty);
		_status.Text = _current == null ? "" :
			$"{_current.FilePath}   ·   {(_current.Dirty ? "unsaved changes" : "saved")}{(dirty > 1 ? $" ({dirty} files unsaved)" : "")}   ·   layout: .storywriter/{System.IO.Path.GetFileNameWithoutExtension(_current.FileName)}.layout.json";
	}

	Dictionary<string, (int, int)> IssuesFor(DialogueDocument? d) =>
		d == null ? new() : _issues.Where(i => i.DocId == d.Id && i.NodeId != null).GroupBy(i => i.NodeId!)
			.ToDictionary(g => g.Key, g => (g.Count(i => i.IsError), g.Count(i => !i.IsError)));

	void Revalidate()
	{
		if (_ws == null) return;
		var ids = _ws.HunkIds;
		_issues = _ws.Docs.SelectMany(d => Validator.Validate(d, ids)).ToList();
		_graph.NodeIssues = IssuesFor(_current);
		_graph.InvalidateVisual();
		int errs = _issues.Count(i => i.IsError), warns = _issues.Count - errs;
		_issuePanel.Header = errs + warns == 0 ? "Problems: none ✓" : $"Problems: {errs} error(s), {warns} warning(s)";
		_issueList.ItemsSource = _issues.Select(i => new ListBoxItem
		{
			Tag = i,
			Padding = new Thickness(10, 3),
			Content = Ui.Label(i.ToString(), 12, i.IsError ? Palette.Error : Palette.Warn),
		}).ToList();
		RefreshDocList();
	}

	void JumpTo(string docId, string? nodeId)
	{
		var d = _ws?.Find(docId);
		if (d == null) return;
		_modeTabs.SelectedIndex = 0;
		if (d != _current) ShowDoc(d);
		if (nodeId != null)
		{
			_graph.Select(nodeId);
			_graph.Reveal(nodeId, force: true);
		}
	}

	// ------------------------------------------------------------------ Graph wiring

	void WireGraph()
	{
		_graph.EditNodeRequested += OpenEditor;
		_graph.EditConversationRequested += EditConversation;
		_graph.PreviewRequested += PreviewFrom;
		_graph.ZoomChanged += _ => UpdateChrome();

		_graphPreview.NodeEntered += (h, n) =>
		{
			if (h == _current?.Id) _graph.SetPreviewNode(n);
		};
		_graphPreview.NodeLinkClicked += (h, n) => JumpTo(h, n);
		_graphPreview.ConversationEnded += (h, ending) =>
		{
			_graph.SetPreviewNode(null);
			var name = Find(h)?.Name ?? h;
			_graphPreview.SetEndActions(
				Ui.Btn("↻ Restart", () => _graphPreview.Restart(), "Restore the state from before this run and play it again"),
				Ui.Btn($"Next visit ►", () => StartGraphPreview(h, null), $"Talk to {name} again: entries are re-checked with the updated state", accent: true));
		};
	}

	void PreviewFrom(string? nodeId)
	{
		if (_current == null) return;
		StartGraphPreview(_current.Id, nodeId);
	}

	void StartGraphPreview(string hunk, string? nodeId)
	{
		_graphPreview.SetEndActions(Ui.Btn("■ Stop", () => { _graphPreview.Stop(); _graph.ClearPreview(); }), Ui.Btn("↻ Restart", () => _graphPreview.Restart()));
		_graph.ClearPreview();
		if (hunk == _current?.Id) _graph.EvaluateCondition = c => _graphState.IsTrue(hunk, c);
		_sideTabs.SelectedIndex = 0;
		_graphPreview.Start(hunk, nodeId);
		_graphStatePanel.Rebuild();
	}

	void OpenEditor(string nodeId)
	{
		if (_current == null || _current.Node(nodeId) == null) return;
		var key = (_current, nodeId);
		if (_editors.TryGetValue(key, out var existing))
		{
			existing.Activate();
			return;
		}
		var w = new NodeEditorWindow(_current, nodeId);
		var doc = _current;
		_editors[key] = w;
		w.PreviewRequested += id =>
		{
			if (doc != _current) ShowDoc(doc);
			_graph.Select(id);
			StartGraphPreview(doc.Id, id);
			Activate();
		};
		w.SaveRequested += () => Save(doc);
		w.Closed += (_, _) =>
		{
			foreach (var k in _editors.Where(kv => kv.Value == w).Select(kv => kv.Key).ToList()) _editors.Remove(k);
		};
		// Track renames so double-clicking the renamed node finds this window.
		doc.Changed += () =>
		{
			if (_editors.ContainsValue(w) && !_editors.ContainsKey((doc, w.NodeId)))
			{
				foreach (var k in _editors.Where(kv => kv.Value == w).Select(kv => kv.Key).ToList()) _editors.Remove(k);
				_editors[(doc, w.NodeId)] = w;
			}
		};
		w.Show(this);
	}

	void EditConversation()
	{
		if (_current == null) return;
		var w = new ConversationWindow(_current);
		w.ShowDialog(this);
	}

	// ------------------------------------------------------------------ Play-through

	void WirePlay()
	{
		_playState.Changed += RefreshPlayCast;
		_playPanel.ConversationStarted += RefreshPlayCast;
		_playPanel.NodeLinkClicked += (h, n) => JumpTo(h, n);
		_playPanel.ConversationEnded += (h, ending) =>
		{
			RefreshPlayCast();
			var doc = Find(h);
			var name = doc?.Name ?? h;
			var p = _playState.Hunk(h);
			var next = NextUnfixed(h);
			var actions = new List<Control>();
			if (!p.Fixed)
			{
				actions.Add(Ui.Btn($"Next visit with {name} ► (visit {p.Visits + 1})", () => _playPanel.Start(h), accent: true));
			}
			else
			{
				if (next != null) actions.Add(Ui.Btn($"Continue to {next.Name} ►", () => _playPanel.Start(next.Id), accent: true));
				else actions.Add(Ui.Label("Every arc is complete. ♥\uFE0E", 13, Palette.Ending, FontWeight.Bold));
				actions.Add(Ui.Btn($"Chat with {name} again", () => _playPanel.Start(h), "Post-ending conversation"));
			}
			_playPanel.SetEndActions(actions.ToArray());
		};
		_playPanel.SetEndActions();
	}

	DialogueDocument? NextUnfixed(string after)
	{
		var docs = Docs().ToList();
		int i = docs.FindIndex(d => d.Id == after);
		for (int k = 1; k <= docs.Count; k++)
		{
			var d = docs[(i + k) % docs.Count];
			if (!_playState.Hunk(d.Id).Fixed) return d;
		}
		return null;
	}

	void PlayEverything()
	{
		_playState.Reset();
		var first = Docs().FirstOrDefault();
		if (first != null)
		{
			_playPanel.SetEndActions();
			_playPanel.Start(first.Id);
		}
	}

	void RefreshPlayCast()
	{
		_playCast.Children.Clear();
		foreach (var d in Docs())
		{
			var p = _playState.Hunks.GetValueOrDefault(d.Id);
			string status = p == null || (!p.Met && p.Visits == 0) ? "not met yet"
				: p.Fixed ? $"fixed · {p.Ending.Replace('_', ' ')}"
				: $"visit {p.Visits + 1} next";
			bool active = _playPanel.HunkId == d.Id && _playPanel.IsPlaying;
			var doc = d;
			var talk = Ui.Btn(p?.Fixed == true ? "Chat ►" : "Talk ►", () => { _playPanel.SetEndActions(); _playPanel.Start(doc.Id); }, accent: !active && p?.Fixed != true);
			var head = new DockPanel();
			DockPanel.SetDock(talk, Dock.Right);
			head.Children.Add(talk);
			head.Children.Add(Ui.Label(d.Name, 15, Palette.Text, FontWeight.Bold));
			Control stats = p == null ? Ui.Label("", 1) : Ui.Row(4,
				Ui.Chip($"♥\uFE0E {p.Romance}", Palette.Romance), Ui.Chip($"☺ {p.Friendship}", Palette.Friendship), Ui.Chip($"ϟ {p.Friction}", Palette.Friction));
			_playCast.Children.Add(new Border
			{
				Background = active ? Palette.CardBorder : Palette.Card,
				BorderBrush = p?.Fixed == true ? Palette.Ending : active ? Palette.PreviewHere : Palette.CardBorder,
				BorderThickness = new Thickness(active || p?.Fixed == true ? 2 : 1),
				CornerRadius = new CornerRadius(8),
				Padding = new Thickness(10, 8),
				Child = Ui.Col(4, head,
					Ui.Label($"{Dialogue.Str(d.Root["malady"])} · {Dialogue.Str(d.Root["room"])}", 11, Palette.Muted),
					Ui.Label(status, 12, p?.Fixed == true ? Palette.Ending : Palette.Text),
					stats),
			});
		}
	}

	// ------------------------------------------------------------------ Commands

	void Save(DialogueDocument? d)
	{
		if (d == null) return;
		try
		{
			d.Save();
			_status.Text = $"Saved {d.FileName}";
		}
		catch (Exception e)
		{
			_ = Ui.Ask(this, "Save failed", $"{d.FileName}: {e.Message}", "OK");
		}
		RefreshDocList();
		UpdateChrome();
	}

	void SaveAll()
	{
		foreach (var d in Docs().Where(d => d.Dirty).ToList()) Save(d);
	}

	void Undo()
	{
		_current?.Undo();
		UpdateChrome();
	}

	void Redo()
	{
		_current?.Redo();
		UpdateChrome();
	}

	async Task ReloadCurrent()
	{
		if (_current == null) return;
		if (_current.Dirty && await Ui.Ask(this, "Reload", $"Discard unsaved changes to {_current.FileName}?", "Discard & reload", "Cancel") != 0) return;
		_current.Reload();
	}

	async Task NewConversation()
	{
		if (_ws == null) return;
		var id = await Ui.Prompt(this, "New conversation", "Character id (also the file name, and AFixHimMalady.HunkId in the level):", "", v =>
			!System.Text.RegularExpressions.Regex.IsMatch(v, "^[a-z0-9_]+$") ? "Lowercase letters, digits and _ only"
			: File.Exists(System.IO.Path.Combine(_ws.Folder, v + ".json")) ? "A file with that name exists" : null);
		if (id == null) return;
		var doc = _ws.CreateConversation(id, char.ToUpperInvariant(id[0]) + id[1..]);
		ShowDoc(doc);
		EditConversation();
	}

	async Task OnConflict(DialogueDocument d)
	{
		var r = await Ui.Ask(this, "Changed on disk", $"{d.FileName} was changed outside Story Writer, but you have unsaved edits.", "Reload from disk (lose my edits)", "Keep mine");
		if (r == 0) d.Reload();
	}

	async Task<bool> ConfirmDiscard(string action)
	{
		var dirty = Docs().Where(d => d.Dirty).ToList();
		if (dirty.Count == 0) return true;
		var r = await Ui.Ask(this, "Unsaved changes", $"Save changes to {string.Join(", ", dirty.Select(d => d.FileName))} before you {action}?", "Save", "Don't save", "Cancel");
		if (r == 0) SaveAll();
		return r is 0 or 1;
	}

	bool _closing;

	protected override void OnClosing(WindowClosingEventArgs e)
	{
		base.OnClosing(e);
		if (_closing || !Docs().Any(d => d.Dirty)) return;
		e.Cancel = true;
		Dispatcher.UIThread.Post(async () =>
		{
			if (await ConfirmDiscard("quit"))
			{
				_closing = true;
				Close();
			}
		});
	}

	protected override void OnClosed(EventArgs e)
	{
		base.OnClosed(e);
		_ws?.Dispose();
	}

	void OnWindowKey(object? sender, KeyEventArgs e)
	{
		if (!Ui.IsCommand(e.KeyModifiers)) return;
		bool inText = e.Source is TextBox || (e.Source as Visual)?.FindAncestorOfType<TextEditor>() != null;
		bool shift = e.KeyModifiers.HasFlag(KeyModifiers.Shift);
		switch (e.Key)
		{
			case Key.S:
				if (shift) SaveAll();
				else Save(_current);
				e.Handled = true;
				break;
			case Key.O:
				_ = PickFolder();
				e.Handled = true;
				break;
			case Key.Z when !inText:
				if (shift) Redo();
				else Undo();
				e.Handled = true;
				break;
			case Key.Y when !inText:
				Redo();
				e.Handled = true;
				break;
		}
	}
}

static class VisualExtensions
{
	public static T? FindAncestorOfType<T>(this Visual v) where T : class
	{
		for (var p = v.GetVisualParent(); p != null; p = p.GetVisualParent())
			if (p is T t) return t;
		return null;
	}

	static Visual? GetVisualParent(this Visual v) => Avalonia.VisualTree.VisualExtensions.GetVisualParent(v);
}
