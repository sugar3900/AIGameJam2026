// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"

ICANFIXHIM_API DECLARE_LOG_CATEGORY_EXTERN(LogFixHim, Log, All);

/** In-game debug tools (Debug/): compiled into the editor and development builds only, never shipping. */
#if WITH_EDITOR || !UE_BUILD_SHIPPING
#define FIXHIM_DEBUG 1
#else
#define FIXHIM_DEBUG 0
#endif
