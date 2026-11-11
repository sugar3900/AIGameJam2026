// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FixHimInteractable.generated.h"

class AFixHimPlayerController;
class UStaticMesh;
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

	/**
	 * Build the hover outline shell. Default on. Turn off only for an invisible inspect proxy whose inflated shell
	 * would read as a stray shape (e.g. a thin box behind authored damage art); trace, click, prompt and any glow
	 * are unaffected.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	bool bHoverOutline = true;

	/**
	 * Optional mesh for Body's inverted-hull outline shell, in Body's mesh space. The hull trick only works on
	 * near-convex shapes; a body with folded soft goods (the bed's throw) shows broad shell faces through its folds.
	 * Set this to the rigid part (e.g. the bed frame) to outline only that. Null keeps the Body mesh.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	TObjectPtr<UStaticMesh> OutlineMeshOverride;

	/** Emissive applied to Body while On (Light toggles). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor OnEmissive = FLinearColor(4.f, 3.2f, 2.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	FLinearColor RevealColor = FLinearColor(0.45f, 0.75f, 1.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Look")
	float RevealOpacity = 0.55f;

	/** Preserve authored water/flame materials instead of applying the generic reveal material. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Reveal")
	bool bUseAuthoredRevealMaterial = false;

	/** Optional splash/other reveal art; visibility follows RevealPart, collision is authored separately. */
	UPROPERTY(EditAnywhere, Category = "Reveal")
	TArray<TObjectPtr<AActor>> RevealActors;

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

	/**
	 * Opt-in (Light toggles): authored art whose materials expose the scalar GlowParam (e.g. a bulb's glass and
	 * filament). Each such slot gets a dynamic instance whose GlowParam is its authored value (the "on" strength)
	 * times the toggle alpha, so the glow fades with the light. Empty leaves the existing behaviour untouched.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Glow")
	TArray<TSoftObjectPtr<AActor>> GlowActors;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Glow")
	FName GlowParam = TEXT("GlowStrength");

	/**
	 * Opt-in (Light toggles): extra light actors switched with this one (e.g. a supplemental fill). Each light
	 * component's authored intensity is its "on" value and fades with the toggle alpha. Empty = unchanged behaviour.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Glow")
	TArray<TSoftObjectPtr<AActor>> ToggleLightActors;

	/** Opt-in click animation (Light/None toggles): Pivot dips by PullOffset and returns over PullSeconds (a pull chain). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Pull")
	bool bPullOnClick = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Pull")
	FVector PullOffset = FVector(0.f, 0.f, -1.5f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interactable|Pull")
	float PullSeconds = 0.25f;

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
	void ApplyRevealAlpha(float Alpha);
	bool IsRevealMesh(const UStaticMeshComponent* Mesh) const;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UMaterialInstanceDynamic>> RevealMIDs;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> OutlineShells;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> BodyMID;

	/** Overlay material instance shared by every mesh of this actor; the maladies drive its Glow. */
	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> ShineMID;

	void BuildGlow();

	UPROPERTY(Transient)
	TArray<TObjectPtr<UMaterialInstanceDynamic>> GlowMIDs;
	TArray<float> GlowOnValues;
	UPROPERTY(Transient)
	TArray<TObjectPtr<class ULightComponent>> ExtraLights;
	TArray<float> ExtraLightOnValues;
	float PullAge = -1.f;

	bool bHovered = false;
	bool bInteractionShineEnabled = false;
	float ToggleAlpha = 0.f;
	float Age = 0.f;
	float NextShineAt = 0.f;
	float ClosestOpenDistance = TNumericLimits<float>::Max();
};
