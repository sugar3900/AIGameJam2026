// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "FixHimHUDWidget.generated.h"

class UBorder;
class UTextBlock;
class USizeBox;
class UWidget;

/** In-world HUD: centre reticle (fixed white dot), interact prompt, room name, hints, toasts. */
UCLASS()
class ICANFIXHIM_API UFixHimHUDWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void SetReticle(bool bVisible, bool bPointer, const FText& Prompt);
	void SetRoomName(const FText& Name);
	void SetRepairs(int32 Fixed, int32 Total, int32 Week = 0, int32 NumWeeks = 0);
	void ShowToast(const FString& Message, float Seconds = 2.f, bool bChime = true);

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	UPROPERTY() TObjectPtr<UWidget> ReticleRoot;
	UPROPERTY() TObjectPtr<UBorder> Dot;
	UPROPERTY() TObjectPtr<UTextBlock> PromptText;
	UPROPERTY() TObjectPtr<UBorder> PromptPill;
	UPROPERTY() TObjectPtr<UTextBlock> RoomText;
	UPROPERTY() TObjectPtr<UBorder> RoomPill;
	UPROPERTY() TObjectPtr<UTextBlock> RepairsText;
	UPROPERTY() TObjectPtr<UBorder> ToastPill;
	UPROPERTY() TObjectPtr<UTextBlock> ToastText;

	float ToastTime = 0.f;
	float RoomFlash = 0.f;
};
