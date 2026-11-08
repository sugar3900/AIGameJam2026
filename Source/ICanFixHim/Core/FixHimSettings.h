// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "FixHimSettings.generated.h"

class USkeletalMesh;
class UAnimInstance;
class UMaterialInterface;
class UTexture2D;
class UStaticMesh;

/**
 * Project-wide asset references and tuning for I Can Fix Him.
 * Edit in Project Settings > Game > I Can Fix Him (saved to Config/DefaultGame.ini).
 * Everything is a soft reference so C++ never hard-codes content paths.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "I Can Fix Him"))
class ICANFIXHIM_API UFixHimSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UFixHimSettings();

	static const UFixHimSettings* Get() { return GetDefault<UFixHimSettings>(); }

	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	// ---- Characters -------------------------------------------------------

	/** The hunks (every house malady shares this base body; looks come from dialogue JSON). */
	UPROPERTY(Config, EditAnywhere, Category = "Characters")
	TSoftObjectPtr<USkeletalMesh> HunkMesh;

	UPROPERTY(Config, EditAnywhere, Category = "Characters")
	TSoftClassPtr<UAnimInstance> LocomotionAnimClass;

	/** Material used to tint the hunks. Needs a "BaseColor" vector parameter. */
	UPROPERTY(Config, EditAnywhere, Category = "Characters")
	TSoftObjectPtr<UMaterialInterface> CharacterMaterial;

	// ---- World ------------------------------------------------------------

	/** Simple stylized lit material. Vector params: BaseColor, Emissive. Scalar: Roughness. */
	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UMaterialInterface> FlatMaterial;

	/** Unlit translucent material for water / effects. Vector param: BaseColor. Scalar: Opacity. */
	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UMaterialInterface> TranslucentMaterial;

	/** Camera facing twinkle sprite used by the hunks' appear / pop effects (World/FixHimPuffFx). Param: Color. */
	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UMaterialInterface> SparkleMaterial;

	/** Overlay material that sweeps an occasional shine across interactables and softly glows the maladies' hosts. Params: Color, Bounds, Sweep, ShineStrength, Glow. */
	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UMaterialInterface> ShineMaterial;

	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UStaticMesh> CubeMesh;

	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UStaticMesh> SphereMesh;

	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UStaticMesh> CylinderMesh;

	UPROPERTY(Config, EditAnywhere, Category = "World")
	TSoftObjectPtr<UStaticMesh> PlaneMesh;

	/** Custom depth stencil value used for the hover outline post process. */
	UPROPERTY(Config, EditAnywhere, Category = "World")
	int32 OutlineStencilValue = 1;

	// ---- UI ---------------------------------------------------------------

	/** UI material for dialogue portraits rendered from a scene capture. Params: Portrait (texture), Silhouette (scalar). */
	UPROPERTY(Config, EditAnywhere, Category = "UI")
	TSoftObjectPtr<UMaterialInterface> PortraitMaterial;

	/** Big heart icon used for romance meters and ending cards. */
	UPROPERTY(Config, EditAnywhere, Category = "UI")
	TSoftObjectPtr<UTexture2D> HeartTexture;

	/** The heroine's dialogue portrait for "You:" lines (a bust silhouette, Tools/Art/player_silhouette.svg). */
	UPROPERTY(Config, EditAnywhere, Category = "UI")
	TSoftObjectPtr<UTexture2D> PlayerPortraitTexture;

	// ---- Data -------------------------------------------------------------

	/** Folder (relative to the project Content dir) holding one dialogue JSON per hunk. Staged as non-UFS when packaging. */
	UPROPERTY(Config, EditAnywhere, Category = "Data")
	FString DialogueDirectory = TEXT("ICanFixHim/Data/Dialogue");

	/** Player character's name, substituted for {player} in dialogue. */
	UPROPERTY(Config, EditAnywhere, Category = "Data")
	FString PlayerName = TEXT("Rosie");

	// ---- Tuning -----------------------------------------------------------

	UPROPERTY(Config, EditAnywhere, Category = "Tuning")
	float InteractRange = 450.f;

	/** Characters per second for the dialogue typewriter at text speed 1.0. */
	UPROPERTY(Config, EditAnywhere, Category = "Tuning")
	float TypewriterSpeed = 55.f;

	/** Real seconds for daylight to fade into night (then it stays dark). */
	UPROPERTY(Config, EditAnywhere, Category = "Tuning")
	float DayLengthSeconds = 900.f;

	/** Fraction of the day after which the "it's getting late" tooltip appears. */
	UPROPERTY(Config, EditAnywhere, Category = "Tuning")
	float LateWarningFraction = 0.75f;

	/** Number of playable days (one per week). Going to bed on the last one triggers the final inspection. */
	UPROPERTY(Config, EditAnywhere, Category = "Tuning")
	int32 NumWeeks = 4;

	/** Stat threshold used by the default ending resolver. */
	UPROPERTY(Config, EditAnywhere, Category = "Tuning")
	int32 EndingThreshold = 5;
};
