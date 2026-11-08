// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FixHimPuffFx.generated.h"

class UMaterialBillboardComponent;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;

/** Which little burst to play. */
enum class EFixHimPuffStyle : uint8
{
	/** A hunk popping like a soap bubble: a ring of sparkles flying out and a handful of bubbles that drift up and pop. */
	BubblePop,
	/** A hunk arriving: sparkles spiral gently up out of the fixture, a few slow bubbles. Soft, never a jump scare. */
	Appear
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
	};

	UPROPERTY(Transient) TArray<TObjectPtr<USceneComponent>> Parts;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> SparkleMID;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> BubbleMID;

	TArray<FParticle> Particles;
	EFixHimPuffStyle Style = EFixHimPuffStyle::BubblePop;
	float Age = 0.f;
	float Lifetime = 1.5f;
};
