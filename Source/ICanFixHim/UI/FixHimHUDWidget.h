// I Can Fix Him - AI Game Jam 2026

#pragma once

#include "CoreMinimal.h"
#include "UI/FixHimUI.h"
#include "World/FixHimInteractable.h"
#include "FixHimHUDWidget.generated.h"

class UImage;
class UTexture2D;
class UBorder;
class UTextBlock;
class USizeBox;
class UWidget;

/** In-world HUD: contextual world reticle, interact prompt, room name, hints, toasts. */
UCLASS()
class ICANFIXHIM_API UFixHimHUDWidget : public UFixHimWidget
{
	GENERATED_BODY()

public:
	void SetReticle(bool bVisible, EFixHimInteractionAction Action, const FText& Prompt);
	void SetRoomName(const FText& Name);
	void SetRepairs(int32 Fixed, int32 Total, int32 Week = 0, int32 NumWeeks = 0);
	void ShowToast(const FString& Message, float Seconds = 2.f, bool bChime = true);

protected:
	virtual void BuildUI() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	friend class FFixHimReticlesTest;
	UPROPERTY() TObjectPtr<UWidget> ReticleRoot;
	UPROPERTY() TObjectPtr<UImage> ReticleImage;
	UPROPERTY() TMap<EFixHimInteractionAction, TObjectPtr<UTexture2D>> ReticleTextures;
	EFixHimInteractionAction CurrentAction = EFixHimInteractionAction::None;
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
