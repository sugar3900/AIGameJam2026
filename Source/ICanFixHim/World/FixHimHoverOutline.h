// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "FixHimHoverOutline.generated.h"

class AFixHimInteractable;
class APostProcessVolume;
class UMaterialInstanceDynamic;

/**
 * Screen-space hover outline. The hovered interactable writes its meshes to custom depth with
 * UFixHimSettings::OutlineStencilValue; this subsystem enables an unbound post-process volume running
 * HoverOutlineMaterial, which draws a fixed-pixel rim around the pixels of those meshes that are actually
 * visible (custom depth matches scene depth). The pass is disabled while nothing is hovered.
 */
UCLASS()
class ICANFIXHIM_API UFixHimHoverOutlineSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	static UFixHimHoverOutlineSubsystem* Get(const UObject* WorldContext);

	/** Outline `Target` (its meshes must already write the outline stencil) in `Color`. */
	void Show(const AFixHimInteractable* Target, const FLinearColor& Color);
	/** Turn the outline off if `Target` is the one shown. */
	void Hide(const AFixHimInteractable* Target);

protected:
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

private:
	bool EnsureVolume();

	TWeakObjectPtr<const AFixHimInteractable> Current;

	UPROPERTY(Transient)
	TObjectPtr<APostProcessVolume> Volume;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> MID;

	bool bMissingMaterial = false;
};
