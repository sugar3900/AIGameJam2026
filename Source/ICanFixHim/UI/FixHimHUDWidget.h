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
	/** Advance reticle layer transitions; Seconds <= 0 or a hidden reticle snaps to the end state. */
	void TickReticle(float DeltaSeconds);
	void ApplyReticleLayers();

	UPROPERTY() TObjectPtr<UWidget> ReticleRoot;
	UPROPERTY() TObjectPtr<UImage> ReticleBackground;
	UPROPERTY() TObjectPtr<UImage> ReticleRing;
	/** Idle-size ring with full-size line widths; swapped with ReticleRing as both scale to a shared radius. */
	UPROPERTY() TObjectPtr<UImage> ReticleRingIdle;
	/** The current center (dot or contextual icon) and the one cross-fading out. */
	UPROPERTY() TObjectPtr<UImage> ReticleCenter;
	UPROPERTY() TObjectPtr<UImage> ReticleCenterOut;
	/** Center layer per action; None is the idle dot. */
	UPROPERTY() TMap<EFixHimInteractionAction, TObjectPtr<UTexture2D>> ReticleCenterTextures;
	EFixHimInteractionAction CurrentAction = EFixHimInteractionAction::None;
	float ReticleTransitionSeconds = 0.f;
	float ReticleIdleRingScale = 1.f;
	float ReticleBackgroundOpacity = 1.f;
	/** Transition progress, 0..1: ink background shown, incoming center shown, outgoing center remaining. */
	float BackgroundT = 0.f;
	float CenterInT = 1.f;
	float CenterOutT = 0.f;
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
