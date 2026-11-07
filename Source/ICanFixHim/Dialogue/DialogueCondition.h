// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"

/**
 * Tiny expression evaluator for dialogue conditions.
 *
 *   romance >= 3 && !seen.v2_pipes
 *   (friendship + romance) > 4 || flag.knows_secret
 *   lukey.fixed && visits >= 2
 *
 * Integer-only. Operators: ! && || == != < <= > >= + - and parentheses.
 * Identifiers are resolved through the supplied callback (unknown -> 0).
 * An empty expression is true.
 */
namespace FixHim::Condition
{
	using FResolver = TFunctionRef<int32(const FString& /*Identifier*/)>;

	ICANFIXHIM_API int32 Evaluate(const FString& Expression, FResolver Resolve, FString* OutError = nullptr);

	inline bool IsTrue(const FString& Expression, FResolver Resolve)
	{
		return Expression.IsEmpty() || Evaluate(Expression, Resolve) != 0;
	}
}
