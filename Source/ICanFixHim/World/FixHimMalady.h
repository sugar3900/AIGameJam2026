// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "World/FixHimInteractable.h"
#include "FixHimMalady.generated.h"

class UArrowComponent;
class UCameraComponent;
class UPointLightComponent;
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

	/** Matches the "id" in Content/ICanFixHim/Data/Dialogue/<id>.json */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady")
	FString HunkId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady")
	EMaladyStyle Style = EMaladyStyle::Glow;

	/** Where the broken-fx emanate from, relative to the actor. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Malady", meta = (MakeEditWidget))
	FVector FxOffset = FVector::ZeroVector;

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
	FLinearColor GetGlowColor() const { return GlowColor; }

	void SummonHunk();
	void DismissHunk();
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

	UPROPERTY(Transient)
	TObjectPtr<AFixHimHunk> Hunk;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> BrokenFx;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMeshComponent> Drop;

	UPROPERTY(Transient)
	TObjectPtr<UPointLightComponent> FxLight;

	FLinearColor GlowColor = FLinearColor(1.f, 0.4f, 0.7f);
	FText HunkName;
	bool bRepaired = false;
	float FxTime = 0.f;
};
