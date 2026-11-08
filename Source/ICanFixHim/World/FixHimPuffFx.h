// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FixHimPuffFx.generated.h"

class UMaterialBillboardComponent;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;
class UPointLightComponent;

/** Which little burst to play. */
enum class EFixHimPuffStyle : uint8
{
	/** A hunk popping like a soap bubble: a ring of sparkles flying out and a handful of bubbles that drift up and pop. */
	BubblePop,
	/** A hunk arriving: sparkles spiral gently up out of the fixture, a few slow bubbles. Soft, never a jump scare. */
	Appear,
	/** Sparkles only (no bubbles): a thicker spiral of glitter up out of the fixture. */
	SparkleIn,
	/** Sparkles only: the body dissolves in a burst of glitter. */
	SparkleOut,
	/** A cloud of black spores billowing out of the fixture. */
	SporesIn,
	/** The body vanishing in a puff of black spores. */
	SporesOut,
	/** An electrical surge around the body: crackling bolts and a flickering flash. */
	SurgeIn,
	SurgeOut
};

/**
 * Short-lived, self-destroying cosmetic burst built from engine primitives: additive sparkle sprites (M_Sparkle) and
 * translucent spheres (M_Translucent) as bubbles. No Niagara asset needed, so it stays code-only like the rest of the
 * game. Spawn with AFixHimPuffFx::Spawn; it ticks itself and is gone after a second or two.
 */
UCLASS(NotPlaceable, Transient)
class ICANFIXHIM_API AFixHimPuffFx : public AActor
{
	GENERATED_BODY()

public:
	AFixHimPuffFx();

	static AFixHimPuffFx* Spawn(UWorld* World, const FVector& Location, const FLinearColor& Color, EFixHimPuffStyle Style, float Size = 1.f);

	virtual void Tick(float DeltaSeconds) override;

private:
	void Build(const FLinearColor& Color, EFixHimPuffStyle InStyle, float Size);
	/** Black spore cloud: dark matte specks plus a few soft smoky blobs. */
	void BuildSpores(bool bIn, float Size);
	/** Electric bolts that re-strike at random places up and down his body, plus a flickering light. */
	void BuildSurge(const FLinearColor& Color, float Size);

	struct FParticle
	{
		TObjectPtr<USceneComponent> Comp;
		FVector Velocity = FVector::ZeroVector;
		float Delay = 0.f;
		float Life = 1.f;
		float BaseSize = 1.f;
		float Spin = 0.f;
		bool bBubble = false;
		/** Bubbles: a quick swell then gone. */
		float PopAt = 1.f;
		float Phase = 0.f;
		/** Spores: drift upward by this much per second squared; blobs swell as they age. */
		float Rise = 0.f;
		bool bSpore = false;
		bool bBlob = false;
		/** Surge bolts: next time to jump to a new spot. */
		bool bSurge = false;
		float NextStrike = 0.f;
	};

	UPROPERTY(Transient) TArray<TObjectPtr<USceneComponent>> Parts;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> SparkleMID;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> BubbleMID;
	UPROPERTY(Transient) TObjectPtr<UPointLightComponent> SurgeLight;
	float SurgeSize = 1.f;

	TArray<FParticle> Particles;
	EFixHimPuffStyle Style = EFixHimPuffStyle::BubblePop;
	float Age = 0.f;
	float Lifetime = 1.5f;
};
