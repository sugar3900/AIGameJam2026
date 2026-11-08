namespace StoryWriter.Runtime;

/// <summary>Port of Source/ICanFixHim/Dialogue/DialogueCondition.cpp. Keep the two in sync.</summary>
public static class Condition
{
	public static int Evaluate(string? expression, Func<string, int> resolve, out string? error)
	{
		error = null;
		if (string.IsNullOrWhiteSpace(expression)) return 1;
		var p = new Parser(expression, resolve);
		int result = p.ParseOr();
		p.SkipWs();
		if (p.Error == null && p.Pos < expression.Length) p.Error = $"Trailing characters at {p.Pos}";
		error = p.Error;
		return result;
	}

	public static bool IsTrue(string? expression, Func<string, int> resolve) => Evaluate(expression, resolve, out _) != 0;

	/// <summary>Syntax check only (every identifier resolves to 0). Returns the error or null.</summary>
	public static string? Check(string? expression)
	{
		Evaluate(expression, _ => 0, out var e);
		return e;
	}

	/// <summary>Identifiers referenced by an expression (lower-cased), for the condition boxes and state panel.</summary>
	public static List<string> Identifiers(string? expression)
	{
		var list = new List<string>();
		if (string.IsNullOrEmpty(expression)) return list;
		Evaluate(expression, id => { if (!list.Contains(id)) list.Add(id); return 0; }, out _);
		return list;
	}

	sealed class Parser
	{
		readonly string _src;
		readonly Func<string, int> _resolve;
		public int Pos;
		public string? Error;

		public Parser(string src, Func<string, int> resolve)
		{
			_src = src;
			_resolve = resolve;
		}

		public void SkipWs()
		{
			while (Pos < _src.Length && char.IsWhiteSpace(_src[Pos])) Pos++;
		}

		bool Match(string token)
		{
			SkipWs();
			if (string.CompareOrdinal(_src, Pos, token, 0, token.Length) == 0 && Pos + token.Length <= _src.Length)
			{
				Pos += token.Length;
				return true;
			}
			return false;
		}

		bool Peek(string token)
		{
			SkipWs();
			return Pos + token.Length <= _src.Length && string.CompareOrdinal(_src, Pos, token, 0, token.Length) == 0;
		}

		public int ParseOr()
		{
			int l = ParseAnd();
			while (Match("||"))
			{
				int r = ParseAnd();
				l = (l != 0 || r != 0) ? 1 : 0;
			}
			return l;
		}

		int ParseAnd()
		{
			int l = ParseNot();
			while (Match("&&"))
			{
				int r = ParseNot();
				l = (l != 0 && r != 0) ? 1 : 0;
			}
			return l;
		}

		int ParseNot()
		{
			SkipWs();
			if (Pos < _src.Length && _src[Pos] == '!' && !Peek("!="))
			{
				Pos++;
				return ParseNot() == 0 ? 1 : 0;
			}
			return ParseCompare();
		}

		int ParseCompare()
		{
			int l = ParseSum();
			if (Match("==")) return l == ParseSum() ? 1 : 0;
			if (Match("!=")) return l != ParseSum() ? 1 : 0;
			if (Match(">=")) return l >= ParseSum() ? 1 : 0;
			if (Match("<=")) return l <= ParseSum() ? 1 : 0;
			if (Match(">")) return l > ParseSum() ? 1 : 0;
			if (Match("<")) return l < ParseSum() ? 1 : 0;
			return l;
		}

		int ParseSum()
		{
			int l = ParsePrimary();
			for (;;)
			{
				if (Match("+")) l += ParsePrimary();
				else if (Match("-")) l -= ParsePrimary();
				else break;
			}
			return l;
		}

		int ParsePrimary()
		{
			SkipWs();
			if (Pos >= _src.Length)
			{
				Error ??= "Unexpected end of expression";
				return 0;
			}
			char c = _src[Pos];
			if (c == '(')
			{
				Pos++;
				int v = ParseOr();
				if (!Match(")")) Error ??= "Missing )";
				return v;
			}
			if (c == '-')
			{
				Pos++;
				return -ParsePrimary();
			}
			if (char.IsDigit(c))
			{
				int start = Pos;
				while (Pos < _src.Length && char.IsDigit(_src[Pos])) Pos++;
				return int.TryParse(_src.AsSpan(start, Pos - start), out var n) ? n : 0;
			}
			if (char.IsLetter(c) || c == '_')
			{
				int start = Pos;
				while (Pos < _src.Length && (char.IsLetterOrDigit(_src[Pos]) || _src[Pos] == '_' || _src[Pos] == '.')) Pos++;
				var ident = _src[start..Pos].ToLowerInvariant();
				if (ident == "true") return 1;
				if (ident == "false") return 0;
				return _resolve(ident);
			}
			Error ??= $"Unexpected '{c}' at {Pos}";
			Pos++;
			return 0;
		}
	}
}
