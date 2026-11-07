// I Can Fix Him - AI Game Jam 2026

#include "Dialogue/DialogueCondition.h"

namespace FixHim::Condition
{
	namespace
	{
		struct FParser
		{
			const FString& Src;
			FResolver Resolve;
			int32 Pos = 0;
			FString Error;

			FParser(const FString& InSrc, FResolver InResolve) : Src(InSrc), Resolve(InResolve) {}

			void SkipWs()
			{
				while (Pos < Src.Len() && FChar::IsWhitespace(Src[Pos]))
				{
					++Pos;
				}
			}

			bool Match(const TCHAR* Token)
			{
				SkipWs();
				const int32 Len = FCString::Strlen(Token);
				if (Src.Mid(Pos, Len) == Token)
				{
					Pos += Len;
					return true;
				}
				return false;
			}

			bool Peek(const TCHAR* Token)
			{
				SkipWs();
				return Src.Mid(Pos, FCString::Strlen(Token)) == Token;
			}

			int32 ParseOr()
			{
				int32 L = ParseAnd();
				while (Match(TEXT("||")))
				{
					const int32 R = ParseAnd();
					L = (L != 0 || R != 0) ? 1 : 0;
				}
				return L;
			}

			int32 ParseAnd()
			{
				int32 L = ParseNot();
				while (Match(TEXT("&&")))
				{
					const int32 R = ParseNot();
					L = (L != 0 && R != 0) ? 1 : 0;
				}
				return L;
			}

			int32 ParseNot()
			{
				SkipWs();
				if (Pos < Src.Len() && Src[Pos] == TEXT('!') && !Peek(TEXT("!=")))
				{
					++Pos;
					return ParseNot() == 0 ? 1 : 0;
				}
				return ParseCompare();
			}

			int32 ParseCompare()
			{
				const int32 L = ParseSum();
				if (Match(TEXT("=="))) { return L == ParseSum() ? 1 : 0; }
				if (Match(TEXT("!="))) { return L != ParseSum() ? 1 : 0; }
				if (Match(TEXT(">="))) { return L >= ParseSum() ? 1 : 0; }
				if (Match(TEXT("<="))) { return L <= ParseSum() ? 1 : 0; }
				if (Match(TEXT(">"))) { return L > ParseSum() ? 1 : 0; }
				if (Match(TEXT("<"))) { return L < ParseSum() ? 1 : 0; }
				return L;
			}

			int32 ParseSum()
			{
				int32 L = ParsePrimary();
				for (;;)
				{
					if (Match(TEXT("+"))) { L += ParsePrimary(); }
					else if (Match(TEXT("-"))) { L -= ParsePrimary(); }
					else { break; }
				}
				return L;
			}

			int32 ParsePrimary()
			{
				SkipWs();
				if (Pos >= Src.Len())
				{
					Error = TEXT("Unexpected end of expression");
					return 0;
				}
				const TCHAR C = Src[Pos];
				if (C == TEXT('('))
				{
					++Pos;
					const int32 V = ParseOr();
					if (!Match(TEXT(")")))
					{
						Error = TEXT("Missing )");
					}
					return V;
				}
				if (C == TEXT('-'))
				{
					++Pos;
					return -ParsePrimary();
				}
				if (FChar::IsDigit(C))
				{
					int32 Start = Pos;
					while (Pos < Src.Len() && FChar::IsDigit(Src[Pos]))
					{
						++Pos;
					}
					return FCString::Atoi(*Src.Mid(Start, Pos - Start));
				}
				if (FChar::IsAlpha(C) || C == TEXT('_'))
				{
					int32 Start = Pos;
					while (Pos < Src.Len() && (FChar::IsAlnum(Src[Pos]) || Src[Pos] == TEXT('_') || Src[Pos] == TEXT('.')))
					{
						++Pos;
					}
					const FString Ident = Src.Mid(Start, Pos - Start).ToLower();
					if (Ident == TEXT("true")) { return 1; }
					if (Ident == TEXT("false")) { return 0; }
					return Resolve(Ident);
				}
				Error = FString::Printf(TEXT("Unexpected '%c' at %d"), C, Pos);
				++Pos;
				return 0;
			}
		};
	}

	int32 Evaluate(const FString& Expression, FResolver Resolve, FString* OutError)
	{
		if (Expression.TrimStartAndEnd().IsEmpty())
		{
			return 1;
		}
		FParser P(Expression, Resolve);
		const int32 Result = P.ParseOr();
		P.SkipWs();
		if (P.Error.IsEmpty() && P.Pos < Expression.Len())
		{
			P.Error = FString::Printf(TEXT("Trailing characters at %d"), P.Pos);
		}
		if (OutError)
		{
			*OutError = P.Error;
		}
		return Result;
	}
}
