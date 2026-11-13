// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "World/FixHimInteractable.h"
#include "FixHimMorphInteractable.generated.h"

class USkeletalMeshComponent;

/**
 * A toggle whose authored shape changes instead of moving rigidly: a skeletal mesh's morph target (a curtain's
 * "Closed") follows the toggle alpha, 0 while off. Body becomes an invisible click proxy whose box blends from ProxyOff
 * to ProxyOn with the same alpha, so the clickable (and click-blocking) area follows the visible shape. The attention
 * shine is applied to the morph mesh. The inverted-hull hover outline (static meshes only) is not built for it.
 *
 * Hierarchy: Root -> Pivot -> Body (hidden proxy) + MorphMesh
 */
UCLASS()
class ICANFIXHIM_API AFixHimMorphInteractable : public AFixHimInteractable
{
	GENERATED_BODY()

public:
	AFixHimMorphInteractable();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USkeletalMeshComponent> MorphMesh;

	/** Morph target driven 0 (off) .. 1 (on). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Morph")
	FName MorphTarget = TEXT("Closed");

	/**
	 * Optional corrective for the halfway pose (a linear blend between two very different shapes loses volume, e.g. a
	 * curtain's cloth length). Driven additively at 4·a·(1−a): 0 at both ends, 1 at a = 0.5. Ignored if the mesh lacks it.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Morph")
	FName MidMorphTarget = TEXT("Closed_Mid");

	/** Click proxy box in actor space (cm) while off. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Morph")
	FBox ProxyOff = FBox(FVector(-10.f), FVector(10.f));

	/** Click proxy box in actor space (cm) while on. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Morph")
	FBox ProxyOn = FBox(FVector(-10.f), FVector(10.f));

protected:
	virtual void ApplyToggleAlpha(float Alpha) override;
	void BuildMorphShine();
};
