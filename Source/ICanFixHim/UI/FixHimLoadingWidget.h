// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "FixHimLoadingWidget.generated.h"

class UProgressBar;

/**
 * Opaque screen shown before the title while UFixHimWarmupSubsystem prepares shaders and effects. Only shows
 * progress: AFixHimPlayerController decides when loading is over and fades it out.
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
	/** Just the animated dots after "Getting the place ready". */
	UPROPERTY() TObjectPtr<UTextBlock> Caption;
	static constexpr float DotsWidth = 24.f;
	float Age = 0.f;
	float ShownProgress = 0.f;
};
