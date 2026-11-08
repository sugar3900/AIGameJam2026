// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "FixHimHunk.generated.h"

class USceneCaptureComponent2D;
class UTextureRenderTarget2D;
struct FHunkDefinition;

/**
 * The man trapped inside a house malady. Spawned hidden by AFixHimMalady and
 * popped into existence when the player clicks the glowing fixture.
 * Owns a scene capture used for the dialogue portrait and the intro silhouette.
 */
UCLASS()
class ICANFIXHIM_API AFixHimHunk : public ACharacter
{
	GENERATED_BODY()

public:
	AFixHimHunk();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/** Apply body tint, scale and props from the dialogue JSON. */
	void ApplyDefinition(const FHunkDefinition& Def);

	void Appear();
	void Disappear();
	bool IsPresent() const { return bPresent; }

	/** The dialogue portrait is a still taken when the hunk first appears; this makes sure one exists (capturing now if not). */
	void SetPortraitLive(bool bLive);
	UTextureRenderTarget2D* GetPortrait() const { return PortraitTarget; }
	/** Re-render the portrait target. bAsStill marks the result as the dialogue still (taken once, on first appearance). */
	void CapturePortraitNow(bool bAsStill = false);

	/** One-off head-to-waist capture into Target (used for the end-of-game keepsake). */
	void CaptureKeepsake(UTextureRenderTarget2D* Target);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hunk")
	FString HunkId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneCaptureComponent2D> PortraitCapture;

private:
	void SetPresentImmediate(bool bVisible);

	UPROPERTY(Transient)
	TObjectPtr<UTextureRenderTarget2D> PortraitTarget;

	float BaseScale = 1.f;
	float PopAlpha = 0.f;
	float PopTarget = 0.f;
	bool bPresent = false;
	bool bHasStill = false;
	FTimerHandle StillTimer;
	float Age = 0.f;
};
