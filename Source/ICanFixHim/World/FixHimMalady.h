// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "World/FixHimInteractable.h"
#include "FixHimMalady.generated.h"

class UArrowComponent;
class UCameraComponent;
class UPointLightComponent;
class UMaterialInterface;
class AFixHimHunk;

/** Procedural "this is broken" dressing played until the malady is repaired. */
UENUM(BlueprintType)
enum class EMaladyStyle : uint8
{
	Glow,
	Leak,
	Mold,
	Wiring,
	Tile
};

/**
 * The glowing fixture that holds a hunk: the leaky sink, the moldy wall, the sparking outlet...
 * Clicking it summons the man (AFixHimHunk). Leaving the room sends him back.
 */
UCLASS()
class ICANFIXHIM_API AFixHimMalady : public AFixHimInteractable
{
	GENERATED_BODY()

public:
	AFixHimMalady();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void Interact(AFixHimPlayerController* Player) override;
	virtual FText GetPrompt() const override;
	virtual EFixHimInteractionAction GetInteractionAction() const override;
	virtual FName DefaultInteractSfx(bool bNowOn) const override;

	/** Matches the "id" in Content/ICanFixHim/Data/Dialogue/<id>.json */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady")
	FString HunkId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady")
	EMaladyStyle Style = EMaladyStyle::Glow;

	/** Where the broken-fx emanate from, relative to the actor. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady", meta = (MakeEditWidget))
	FVector FxOffset = FVector::ZeroVector;

	/**
	 * Leak only, opt-in: when an attached actor carries the AuthoredLeakDamage tag (level-authored spill art), the
	 * procedural sphere drop and floor cylinder are not built. Instead a small drop forms at LeakDripStart, falls
	 * under gravity to LeakDripLanding and leaves a restrained ripple there (both actor-local, cm).
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady|Authored Leak", meta = (MakeEditWidget))
	FVector LeakDripStart = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady|Authored Leak", meta = (MakeEditWidget))
	FVector LeakDripLanding = FVector::ZeroVector;

	/** Lit translucent drop material; the unlit translucent fallback is used when unset. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady|Authored Leak")
	TObjectPtr<UMaterialInterface> LeakDropMaterial;

	/** Ripple material on a unit plane, driven by the scalar parameter "Phase" (0..1, one expanding ring). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady|Authored Leak")
	TObjectPtr<UMaterialInterface> LeakRippleMaterial;

	/** Ripple plane diameter at LeakDripLanding, cm. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady|Authored Leak")
	float LeakRippleDiameter = 14.f;

	/**
	 * The breathing-glow overlay drawn on Body. Default on. Turn off only for an invisible inspect proxy whose glowing
	 * faces would read as a stray pale shape (e.g. a box over authored mold art); the glow light, prompt, inspect and
	 * repair are unaffected.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Malady")
	bool bBodyGlowOverlay = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UArrowComponent> HunkSpawn;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UArrowComponent> TalkSpot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> DialogueCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UPointLightComponent> GlowLight;

	/** Place the dialogue camera at Rosie's eye line at the talk spot at BeginPlay. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady")
	bool bAutoFrameCamera = true;

	AFixHimHunk* GetHunk() const { return Hunk; }
	/** Not clickable while his goodbye plays (and for a moment after), so he can't be re-summoned mid-dissolve. */
	virtual bool CanInteract() const override;
	void LockInteraction(float Seconds);
	FLinearColor GetGlowColor() const { return GlowColor; }

	/** He grows gently out of the fixture (see AFixHimHunk::Appear). */
	void SummonHunk();
	/** bBubblePop: he pops like a bubble (end of a conversation, leaving the room); false hides him silently. */
	void DismissHunk(bool bBubblePop = true);
	bool IsHunkPresent() const;

	/** Where Rosie should stand (capsule centre) to talk. */
	FVector GetTalkLocation(float CapsuleHalfHeight) const;

	/** Refresh the broken/fixed dressing from save data. */
	void RefreshRepairState();
	bool IsRepaired() const { return bRepaired; }

private:
	void BuildBrokenFx();
	void FrameCamera();
	void TickBrokenFx(float DeltaSeconds);
	FVector FindStandLocation(const FVector& Around, float Scale) const;

	FVector HunkStandLocation = FVector::ZeroVector;
	float HunkScale = 1.f;
	float InteractLockedUntil = 0.f;

	UPROPERTY(Transient)
	TObjectPtr<AFixHimHunk> Hunk;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> BrokenFx;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMeshComponent> Drop;

	UPROPERTY(Transient)
	TObjectPtr<UPointLightComponent> FxLight;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMeshComponent> Ripple;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> RippleMID;

	bool bAuthoredLeak = false;
	float LeakCycleStart = 0.f;
	float LeakCyclePeriod = 1.6f;
	FRandomStream LeakRng;

	FLinearColor GlowColor = FLinearColor(1.f, 0.4f, 0.7f);
	FText HunkName;
	bool bRepaired = false;
	bool bRepairKnown = false;
	float FxTime = 0.f;
};
