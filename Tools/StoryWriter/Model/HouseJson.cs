using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace StoryWriter.Model;

/// <summary>
/// Writes dialogue JSON in the same hand-written style as the files in Content/ICanFixHim/Data/Dialogue,
/// so saving an untouched file produces no diff:
///  - 4-space indents, LF, final newline, raw UTF-8 (no \u escapes)
///  - objects inside arrays (choices, entries, props) and "do"/"topics" objects stay on one line
///  - arrays of numbers are inline ([1, 2, 3]); single-string arrays are inline ([ "x" ])
///  - a blank line between node groups in "nodes" (v1*, v2*, ..., after_*)
/// </summary>
public static class HouseJson
{
	static readonly HashSet<string> InlineObjectKeys = new() { "do", "topics" };

	/// <summary>
	/// Original layout of each container, keyed by path ("nodes/v1/lines" -> inline?). The files are hand-formatted
	/// and not perfectly consistent, so untouched containers keep whatever style they had.
	/// </summary>
	public sealed class StyleHints : Dictionary<string, (bool inline, int count)> { }

	public static string Serialize(JsonNode root, StyleHints? hints = null)
	{
		var sb = new StringBuilder();
		Write(sb, root, 0, null, false, "", hints);
		sb.Append('\n');
		return sb.ToString();
	}

	/// <summary>Records which objects/arrays were written on a single line in the source text.</summary>
	public static StyleHints ScanStyle(string text)
	{
		var hints = new StyleHints();
		var bytes = Encoding.UTF8.GetBytes(text);
		var reader = new Utf8JsonReader(bytes, new JsonReaderOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
		var stack = new Stack<(string path, long start, bool isArray, int index, string? prop)>();
		string ChildPath()
		{
			if (stack.Count == 0) return "";
			var top = stack.Peek();
			var seg = top.isArray ? top.index.ToString() : top.prop ?? "";
			return top.path.Length == 0 ? seg : top.path + "/" + seg;
		}
		void Bump()
		{
			if (stack.Count > 0 && stack.Peek().isArray)
			{
				var t = stack.Pop();
				t.index++;
				stack.Push(t);
			}
		}
		try
		{
			while (reader.Read())
			{
				switch (reader.TokenType)
				{
					case JsonTokenType.StartObject:
					case JsonTokenType.StartArray:
						stack.Push((ChildPath(), reader.TokenStartIndex, reader.TokenType == JsonTokenType.StartArray, 0, null));
						break;
					case JsonTokenType.EndObject:
					case JsonTokenType.EndArray:
						var f = stack.Pop();
						hints[f.path] = (Array.IndexOf(bytes, (byte)'\n', (int)f.start, (int)(reader.TokenStartIndex - f.start)) < 0, f.index);
						Bump();
						break;
					case JsonTokenType.PropertyName:
						var p = stack.Pop();
						p.prop = reader.GetString();
						stack.Push(p);
						break;
					default:
						Bump();
						break;
				}
			}
		}
		catch (JsonException)
		{
			// Invalid JSON is reported by the parser; hints are best effort.
		}
		return hints;
	}

	public static JsonNode Parse(string text) =>
		JsonNode.Parse(text, new JsonNodeOptions { PropertyNameCaseInsensitive = false },
			new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true })
		?? new JsonObject();

	/// <summary>Group used to separate nodes with blank lines: "v2_story" -> "v2", "after_rs" -> "after".</summary>
	public static string NodeGroup(string id)
	{
		int i = id.IndexOf('_');
		return i > 0 ? id[..i] : id;
	}

	static void Write(StringBuilder sb, JsonNode? node, int indent, string? key, bool parentIsArray, string path, StyleHints? hints)
	{
		// A container that was inline keeps that style only while it hasn't grown.
		bool? hinted = hints != null && hints.TryGetValue(path, out var h)
			? (h.inline ? (node is JsonArray ha && ha.Count > Math.Max(h.count, 1) ? null : true) : false)
			: null;
		static string Join(string path, string seg) => path.Length == 0 ? seg : path + "/" + seg;
		switch (node)
		{
			case null:
				sb.Append("null");
				return;
			case JsonValue v:
				WriteValue(sb, v);
				return;
			case JsonArray a:
				if (hinted ?? IsInlineArray(a)) { WriteInline(sb, a); return; }
				sb.Append("[\n");
				for (int i = 0; i < a.Count; i++)
				{
					Pad(sb, indent + 1);
					Write(sb, a[i], indent + 1, null, true, Join(path, i.ToString()), hints);
					if (i < a.Count - 1) sb.Append(',');
					sb.Append('\n');
				}
				Pad(sb, indent);
				sb.Append(']');
				return;
			case JsonObject o:
				if (o.Count == 0 || (hinted ?? (parentIsArray || (key != null && InlineObjectKeys.Contains(key)))))
				{
					WriteInline(sb, o);
					return;
				}
				sb.Append("{\n");
				int n = 0;
				string? prevGroup = null;
				foreach (var (k, v) in o)
				{
					if (key == "nodes")
					{
						var g = NodeGroup(k);
						if (prevGroup != null && g != prevGroup) sb.Append('\n');
						prevGroup = g;
					}
					Pad(sb, indent + 1);
					WriteString(sb, k);
					sb.Append(": ");
					Write(sb, v, indent + 1, k, false, Join(path, k), hints);
					if (++n < o.Count) sb.Append(',');
					sb.Append('\n');
				}
				Pad(sb, indent);
				sb.Append('}');
				return;
		}
	}

	static bool IsInlineArray(JsonArray a)
	{
		if (a.Count == 0) return true;
		if (a.All(x => x is JsonValue v && v.GetValueKind() is JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False)) return true;
		return a.Count == 1 && a[0] is JsonValue s && s.GetValueKind() == JsonValueKind.String;
	}

	static void WriteInline(StringBuilder sb, JsonNode? node)
	{
		switch (node)
		{
			case null: sb.Append("null"); break;
			case JsonValue v: WriteValue(sb, v); break;
			case JsonArray a:
				if (a.Count == 0) { sb.Append("[]"); break; }
				bool numeric = a.All(x => x is JsonValue v && v.GetValueKind() != JsonValueKind.String);
				sb.Append(numeric ? "[" : "[ ");
				for (int i = 0; i < a.Count; i++)
				{
					if (i > 0) sb.Append(", ");
					WriteInline(sb, a[i]);
				}
				sb.Append(numeric ? "]" : " ]");
				break;
			case JsonObject o:
				if (o.Count == 0) { sb.Append("{}"); break; }
				sb.Append("{ ");
				int n = 0;
				foreach (var (k, v) in o)
				{
					if (n++ > 0) sb.Append(", ");
					WriteString(sb, k);
					sb.Append(": ");
					WriteInline(sb, v);
				}
				sb.Append(" }");
				break;
		}
	}

	static void WriteValue(StringBuilder sb, JsonValue v)
	{
		switch (v.GetValueKind())
		{
			case JsonValueKind.String:
				WriteString(sb, v.GetValue<string>());
				break;
			case JsonValueKind.Number:
				// Parsed numbers keep their original text (1.08 stays 1.08).
				sb.Append(v.TryGetValue<JsonElement>(out var e) ? e.GetRawText() : v.ToJsonString());
				break;
			default:
				sb.Append(v.ToJsonString());
				break;
		}
	}

	public static void WriteString(StringBuilder sb, string s)
	{
		sb.Append('"');
		foreach (char c in s)
		{
			switch (c)
			{
				case '"': sb.Append("\\\""); break;
				case '\\': sb.Append("\\\\"); break;
				case '\n': sb.Append("\\n"); break;
				case '\r': sb.Append("\\r"); break;
				case '\t': sb.Append("\\t"); break;
				default:
					if (c < 0x20) sb.Append($"\\u{(int)c:x4}");
					else sb.Append(c);
					break;
			}
		}
		sb.Append('"');
	}

	static void Pad(StringBuilder sb, int indent) => sb.Append(' ', indent * 4);
}
