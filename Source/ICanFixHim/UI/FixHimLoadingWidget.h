// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "FixHimLoadingWidget.generated.h"

class UProgressBar;

/**
 * Opaque screen shown before the title while UFixHimWarmupSubsystem prepares shaders and effects. Fades out once
 * everything is ready, then tells the player controller (AFixHimPlayerController::FinishLoading).
 */
UCLASS()
class ICANFIXHIM_API UFixHimLoadingWidget : public UFixHimWidget
{
	GENERATED_BODY()

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	UPROPERTY() TObjectPtr<UProgressBar> Bar;
	UPROPERTY() TObjectPtr<UTextBlock> Caption;
	float Age = 0.f;
	float ShownProgress = 0.f;
	/** Seconds into the fade-out; negative until the warmup reports ready. */
	float FadeTime = -1.f;
	bool bFinished = false;
};
