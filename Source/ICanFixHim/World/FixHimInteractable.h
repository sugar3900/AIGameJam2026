// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FixHimInteractable.generated.h"

class AFixHimPlayerController;
class UStaticMeshComponent;
class UPointLightComponent;
class UMaterialInstanceDynamic;
class ALight;

UENUM(BlueprintType)
enum class EInteractToggle : uint8
{
	/** Nothing toggles; subclasses implement Interact. */
	None,
	/** Light component + emissive turn on/off (lamp, TV, stove). */
	Light,
	/** Pivot slides by ToggleOffset (drawer). */
	Slide,
	/** Pivot rotates by ToggleRotation (door, cabinet, toilet lid). */
	Rotate,
	/** RevealPart becomes visible (running faucet, shower). */
	Reveal
};

/**
 * Anything in the apartment you can point at and click.
 * Occasionally shimmers with a shine that wipes across it, gets an outline on hover,
 * and toggles between two states when clicked.
 *
 * Hierarchy: Root -> Pivot -> Body (+ outline shells), Root -> RevealPart, Root -> Light
 */
UCLASS()
class ICANFIXHIM_API AFixHimInteractable : public AActor
{
	GENERATED_BODY()

public:
	AFixHimInteractable();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintPure, Category = "Interactable")
	virtual bool CanInteract() const { return bEnabled; }
	UFUNCTION(BlueprintCallable, Category = "Interactable")
	virtual void Interact(AFixHimPlayerController* Player);
	virtual FText GetPrompt() const;

	void SetHovered(bool bInHovered);
	bool IsHovered() const { return bHovered; }
	/** Suppress the attention sweep immediately, even when the world is about to pause. */
	void SetInteractionShineEnabled(bool bAllow);

	UFUNCTION(BlueprintCallable, Category = "Interactable")
	void SetOn(bool bInOn, bool bInstant = false);
	bool IsOn() const { return bIsOn; }

	/** Room this belongs to (matches AFixHimRoom::RoomId). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Interactable")
	FString RoomId;

	/** How close the player must be to click this; 0 uses the global InteractRange. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
	float InteractRangeOverride = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> Pivot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> RevealPart;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UPointLightComponent> Light;

	// ---- Look -------------------------------------------------------------

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor BodyColor = FLinearColor(0.8f, 0.8f, 0.8f);

	/** Keep material slots on authored moving meshes instead of applying the flat color. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	bool bUseAuthoredBodyMaterials = false;

	/** Emissive applied to Body while On (Light toggles). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor OnEmissive = FLinearColor(4.f, 3.2f, 2.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor RevealColor = FLinearColor(0.45f, 0.75f, 1.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	float RevealOpacity = 0.55f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor OutlineColor = FLinearColor(1.f, 0.35f, 0.75f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	float OutlineThickness = 2.2f;

	/** An occasional shine wipes across the object (ShineMaterial overlay on its meshes). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	bool bShine = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor ShineColor = FLinearColor(1.f, 0.9f, 0.95f);

	/** Seconds between shines (a random value in this range is drawn each time). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FVector2D ShineInterval = FVector2D(2.f, 4.5f);

	/** Brightness of the shine band (additive, over the object's own colours). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	float ShineStrength = 0.65f;

	// ---- Behaviour --------------------------------------------------------

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	EInteractToggle Toggle = EInteractToggle::Light;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	bool bEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	bool bIsOn = false;

	/** Close this drawer or appliance after the player retreats from it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	bool bAutoCloseOnWalkAway = false;

	/** Members of the same non-empty group share state (paired doors or a room's light circuit). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	FName ToggleGroup;

	/** Authored standalone lights controlled by this toggle. Soft references allow different sublevels. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	TArray<TSoftObjectPtr<ALight>> ControlledLights;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	FVector ToggleOffset = FVector(40.f, 0.f, 0.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	FRotator ToggleRotation = FRotator(0.f, 100.f, 0.f);

	/** Shown under the reticle, e.g. "Turn on lamp". */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	FText PromptOn = NSLOCTEXT("FixHim", "DefaultPromptOn", "Turn off");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	FText PromptOff = NSLOCTEXT("FixHim", "DefaultPromptOff", "Turn on");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable")
	float LightIntensityOn = 2500.f;

	/** Sound (SFX_<Name>) played when switched on/opened; empty picks a default from the toggle type and name. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Sound")
	FName InteractSfx;

	/** Sound played when switched off/closed; empty falls back to InteractSfx or the default. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Sound")
	FName InteractSfxOff;

	/** The sound for a toggle that just ended up `bNowOn`: the explicit fields above, else DefaultInteractSfx. */
	FName GetInteractSfx(bool bNowOn) const;
	/** Inferred from the toggle type and prompt, so actors already placed in the level need no rebuild. */
	virtual FName DefaultInteractSfx(bool bNowOn) const;

protected:
	void SetOnLocal(bool bInOn, bool bInstant);
	void PlayInteractSfx();
	void ApplyLook();
	void BuildOutline();
	void BuildShine();
	void ApplyToggleAlpha(float Alpha);

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> OutlineShells;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> BodyMID;

	/** Overlay material instance shared by every mesh of this actor; the maladies drive its Glow. */
	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> ShineMID;

	bool bHovered = false;
	bool bInteractionShineEnabled = false;
	float ToggleAlpha = 0.f;
	float Age = 0.f;
	float NextShineAt = 0.f;
	float ClosestOpenDistance = TNumericLimits<float>::Max();
};
