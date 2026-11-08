// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "FixHimSfxSubsystem.generated.h"

class USoundBase;

/**
 * One-shot sound effects. A sound "Foo" is any sound wave named SFX_Foo (or SFX_Foo_1, SFX_Foo_2, ... as random
 * variants) under /Game/ICanFixHim/Audio/SFX (made by Tools/Audio/generate_sfx.py + Tools/Editor/import_sfx.py).
 *
 * Variants are picked at random without repeating the last one, the same sound can't retrigger within a few
 * milliseconds, and a missing sound is a logged-once no-op, so call sites never need to check. Sounds play as UI
 * sounds, so they keep going while the game is paused. Master volume is applied to the audio device by the save
 * subsystem; there is no separate SFX bus yet.
 */
UCLASS()
class ICANFIXHIM_API UFixHimSfxSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimSfxSubsystem* Get(const UObject* WorldContext);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	/** Rescan the SFX folder (after importing new sounds while the game is running). */
	void RebuildIndex();
	bool Has(FName Name) const { return Index.Contains(Name); }

	/** Non-spatial; returns false if the sound is missing or was rate limited. */
	bool Play2D(FName Name, float Volume = 1.f, float PitchJitter = 0.05f);
	bool PlayAt(FName Name, const FVector& Location, float Volume = 1.f, float PitchJitter = 0.05f);

private:
	struct FEntry
	{
		TArray<FSoftObjectPath> Variants;
		int32 LastVariant = INDEX_NONE;
		double LastPlayTime = -1.0;
	};

	USoundBase* Pick(FName Name);

	TMap<FName, FEntry> Index;
	TSet<FName> Warned;
	/** Loaded waves (they're tiny); keeps them from being garbage collected between plays. */
	UPROPERTY(Transient) TArray<TObjectPtr<USoundBase>> Loaded;
};

namespace FixHim
{
	/** Fire-and-forget helpers for call sites: FixHim::Sfx(this, "ButtonClick"). Safe with a null context. */
	ICANFIXHIM_API void Sfx(const UObject* WorldContext, FName Name, float Volume = 1.f, float PitchJitter = 0.05f);
	ICANFIXHIM_API void SfxAt(const UObject* WorldContext, FName Name, const FVector& Location, float Volume = 1.f, float PitchJitter = 0.05f);
}
