// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimHUDWidget.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Core/FixHimSettings.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

using namespace FixHimUI;

void UFixHimHUDWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	WidgetTree->RootWidget = Root;

	// ---- Reticle (centre) ----
	UVerticalBox* Ret = WidgetTree->ConstructWidget<UVerticalBox>();
	ReticleRoot = Ret;
	UOverlaySlot* RetSlot = Root->AddChildToOverlay(Ret);
	RetSlot->SetHorizontalAlignment(HAlign_Center);
	RetSlot->SetVerticalAlignment(VAlign_Center);

	// Layers rasterized from the selected SVGs (Tools/Art/Reticles), all on one shared viewBox so they stack
	// centered: ink background (actionable only), shared ring, then the center dot/icon. Size is in UMG units,
	// so DPI scaling keeps it the same share of the screen at every resolution.
	const UFixHimSettings* Settings = UFixHimSettings::Get();
	ReticleTransitionSeconds = Settings->ReticleTransitionSeconds;
	ReticleIdleRingScale = Settings->ReticleIdleRingScale;
	ReticleBackgroundOpacity = Settings->ReticleBackgroundOpacity;
	ReticleCenterTextures.Add(EFixHimInteractionAction::None, Settings->ReticleDotTexture.LoadSynchronous());
	ReticleCenterTextures.Add(EFixHimInteractionAction::Inspect, Settings->ReticleInspectIcon.LoadSynchronous());
	ReticleCenterTextures.Add(EFixHimInteractionAction::Talk, Settings->ReticleTalkIcon.LoadSynchronous());
	ReticleCenterTextures.Add(EFixHimInteractionAction::Use, Settings->ReticleUseIcon.LoadSynchronous());
	ReticleCenterTextures.Add(EFixHimInteractionAction::EndDay, Settings->ReticleEndDayIcon.LoadSynchronous());
	UOverlay* Layers = WidgetTree->ConstructWidget<UOverlay>();
	auto AddLayer = [this, Layers](UTexture2D* Texture)
	{
		UImage* Image = WidgetTree->ConstructWidget<UImage>();
		Image->SetBrushFromTexture(Texture);
		UOverlaySlot* LayerSlot = Layers->AddChildToOverlay(Image);
		LayerSlot->SetHorizontalAlignment(HAlign_Fill);
		LayerSlot->SetVerticalAlignment(VAlign_Fill);
		return Image;
	};
	ReticleBackground = AddLayer(Settings->ReticleBackgroundTexture.LoadSynchronous());
	ReticleRing = AddLayer(Settings->ReticleRingTexture.LoadSynchronous());
	{
		// Drawn at its own size (centered) rather than scaled down, so its texels map ~2:1 like the full ring.
		ReticleRingIdle = WidgetTree->ConstructWidget<UImage>();
		ReticleRingIdle->SetBrushFromTexture(Settings->ReticleIdleRingTexture.LoadSynchronous());
		USizeBox* IdleBox = WidgetTree->ConstructWidget<USizeBox>();
		IdleBox->SetWidthOverride(Settings->ReticleSize * ReticleIdleRingScale);
		IdleBox->SetHeightOverride(Settings->ReticleSize * ReticleIdleRingScale);
		IdleBox->AddChild(ReticleRingIdle);
		UOverlaySlot* IdleSlot = Layers->AddChildToOverlay(IdleBox);
		IdleSlot->SetHorizontalAlignment(HAlign_Center);
		IdleSlot->SetVerticalAlignment(VAlign_Center);
	}
	ReticleCenterOut = AddLayer(nullptr);
	ReticleCenter = AddLayer(ReticleCenterTextures.FindRef(EFixHimInteractionAction::None));
	ApplyReticleLayers();
	USizeBox* ReticleBox = WidgetTree->ConstructWidget<USizeBox>();
	ReticleBox->SetWidthOverride(Settings->ReticleSize);
	ReticleBox->SetHeightOverride(Settings->ReticleSize);
	ReticleBox->AddChild(Layers);
	Ret->AddChildToVerticalBox(ReticleBox)->SetHorizontalAlignment(HAlign_Center);

	PromptPill = WidgetTree->ConstructWidget<UFixHimSurface>();
	PromptPill->SetBrush(Rounded(Plum, 14.f));
	PromptPill->SetPadding(FMargin(28,6,36,20));
	PromptText = MakeText(WidgetTree, TEXT(""), 18, Cream, TEXT("Bold"));
	PromptPill->SetContent(PromptText);
	PromptPill->SetVisibility(ESlateVisibility::Collapsed);
	// Its own slot, shifted below the reticle, so the reticle stays exactly at screen centre whether or not a prompt shows.
	PromptPill->SetRenderTranslation(FVector2D(0.f, Settings->ReticleSize * 0.5f + 56.f));
	UOverlaySlot* PromptSlot = Root->AddChildToOverlay(PromptPill);
	PromptSlot->SetHorizontalAlignment(HAlign_Center);
	PromptSlot->SetVerticalAlignment(VAlign_Center);

	// ---- Room name (top left) ----
	RoomPill = WidgetTree->ConstructWidget<UFixHimSurface>();
	RoomPill->SetBrush(Rounded(FixHimDesign::Teal, 18.f));
	RoomPill->SetPadding(FMargin(32,8,40,22));
	RoomText = MakeText(WidgetTree, TEXT(""), 26, Cream, TEXT("Display"));
	RoomPill->SetContent(RoomText);
	UOverlaySlot* RoomSlot = Root->AddChildToOverlay(RoomPill);
	RoomSlot->SetHorizontalAlignment(HAlign_Left);
	RoomSlot->SetVerticalAlignment(VAlign_Top);
	RoomSlot->SetPadding(FMargin(28.f, 24.f));
	RoomPill->SetVisibility(ESlateVisibility::Collapsed);

	// ---- Repairs (top right) ----
	UBorder* RepPill = WidgetTree->ConstructWidget<UFixHimSurface>();
	RepPill->SetBrush(Rounded(FixHimDesign::Teal, 18.f));
	RepPill->SetPadding(FMargin(32,8,40,22));
	RepairsText = MakeText(WidgetTree, TEXT("Repairs 0/0"), 18, Cream, TEXT("Bold"));
	RepPill->SetContent(RepairsText);
	UOverlaySlot* RepSlot = Root->AddChildToOverlay(RepPill);
	RepSlot->SetHorizontalAlignment(HAlign_Right);
	RepSlot->SetVerticalAlignment(VAlign_Top);
	RepSlot->SetPadding(FMargin(28.f, 24.f));

	// ---- Controls hint (bottom left) ----
	UTextBlock* Hint = MakeText(WidgetTree, TEXT("WASD move   Mouse look   Click interact   M floor plan   Esc pause   Bed or door = end the day"), 15, FLinearColor(1.f, 1.f, 1.f, 0.75f));
	ControlHint=Hint;
	Hint->SetShadowOffset(FVector2D(1.f, 1.f));
	Hint->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.7f));
	UOverlaySlot* HintSlot = Root->AddChildToOverlay(Hint);
	HintSlot->SetHorizontalAlignment(HAlign_Left);
	HintSlot->SetVerticalAlignment(VAlign_Bottom);
	HintSlot->SetPadding(FMargin(28.f, 20.f));

	// ---- Toast (top centre) ----
	ToastPill = WidgetTree->ConstructWidget<UFixHimSurface>();
	ToastPill->SetBrush(Rounded(Pink, 16.f));
	ToastPill->SetPadding(FMargin(32,8,40,22));
	ToastText = MakeText(WidgetTree, TEXT(""), 18, FLinearColor::White, TEXT("Bold"));
	ToastPill->SetContent(ToastText);
	UOverlaySlot* ToastSlot = Root->AddChildToOverlay(ToastPill);
	ToastSlot->SetHorizontalAlignment(HAlign_Center);
	ToastSlot->SetVerticalAlignment(VAlign_Top);
	ToastSlot->SetPadding(FMargin(0.f, 26.f));
	ToastPill->SetVisibility(ESlateVisibility::Collapsed);
}

void UFixHimHUDWidget::SetReticle(bool bVisible, EFixHimInteractionAction Action, const FText& Prompt)
{
	if (!ReticleRoot)
	{
		return;
	}
	const bool bWasVisible = ReticleRoot->GetVisibility() != ESlateVisibility::Collapsed;
	ReticleRoot->SetVisibility(bVisible ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	if (CurrentAction != Action)
	{
		// The current center cross-fades out from wherever it is while the new one fades in.
		CurrentAction = Action;
		ReticleCenterOut->SetBrush(ReticleCenter->GetBrush());
		CenterOutT = CenterInT;
		ReticleCenter->SetBrushFromTexture(ReticleCenterTextures.FindRef(Action));
		CenterInT = 0.f;
		ApplyReticleLayers();
	}
	// Only animate changes the player can see; hiding or reappearing shows the settled state.
	TickReticle(bVisible && bWasVisible ? 0.f : -1.f);
	PromptPill->SetVisibility(bVisible && Action != EFixHimInteractionAction::None && !Prompt.IsEmpty() ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	PromptText->SetText(Prompt);
	if(ControlHint) ControlHint->SetVisibility(bVisible ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
}

void UFixHimHUDWidget::TickReticle(float DeltaSeconds)
{
	if (!ReticleCenter)
	{
		return;
	}
	const float Step = DeltaSeconds < 0.f || ReticleTransitionSeconds <= 0.f ? 1.f : DeltaSeconds / ReticleTransitionSeconds;
	const float BackgroundTarget = CurrentAction == EFixHimInteractionAction::None ? 0.f : 1.f;
	if (BackgroundT == BackgroundTarget && CenterInT == 1.f && CenterOutT == 0.f)
	{
		return; // settled: leave the widgets untouched
	}
	BackgroundT = FMath::Clamp(BackgroundT + FMath::Sign(BackgroundTarget - BackgroundT) * Step,
		FMath::Min(BackgroundT, BackgroundTarget), FMath::Max(BackgroundT, BackgroundTarget));
	CenterInT = FMath::Min(1.f, CenterInT + Step);
	CenterOutT = FMath::Max(0.f, CenterOutT - Step);
	ApplyReticleLayers();
}

void UFixHimHUDWidget::ApplyReticleLayers()
{
	// The idle ring expands into the full ring as the ink fill grows out from the center at partial opacity;
	// icons pop in from 60% scale as they fade, and shrink as they leave.
	const auto Show = [](UImage* Image, float Amount, float MinScale, float MaxOpacity = 1.f)
	{
		const float Eased = FMath::InterpEaseOut(0.f, 1.f, Amount, 2.f);
		Image->SetRenderOpacity(Eased * MaxOpacity);
		Image->SetRenderScale(FVector2D(FMath::Lerp(MinScale, 1.f, Eased)));
		return Eased;
	};
	const float Actionable = Show(ReticleBackground, BackgroundT, 0.5f, ReticleBackgroundOpacity);
	// Ring swap: both rings scale so their radii always match; the full ring sits underneath at full opacity
	// (hidden by the wider-stroked idle ring at first) and only the idle ring on top fades, so nothing dims.
	ReticleRing->SetRenderOpacity(Actionable > 0.f ? 1.f : 0.f);
	ReticleRing->SetRenderScale(FVector2D(FMath::Lerp(ReticleIdleRingScale, 1.f, Actionable)));
	ReticleRingIdle->SetRenderOpacity(1.f - Actionable);
	ReticleRingIdle->SetRenderScale(FVector2D(FMath::Lerp(1.f, 1.f / ReticleIdleRingScale, Actionable)));
	Show(ReticleCenter, CenterInT, 0.6f);
	Show(ReticleCenterOut, CenterOutT, 0.6f);
}

void UFixHimHUDWidget::SetRoomName(const FText& Name)
{
	if (!RoomText)
	{
		return;
	}
	if (!RoomText->GetText().EqualTo(Name))
	{
		RoomFlash = 1.f;
	}
	RoomText->SetText(Name);
	RoomPill->SetVisibility(Name.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
}

void UFixHimHUDWidget::SetRepairs(int32 Fixed, int32 Total, int32 Week, int32 NumWeeks)
{
	if (RepairsText)
	{
		const FString WeekText = Week > 0 && Week <= NumWeeks ? FString::Printf(TEXT("Week %d of %d   "), Week, NumWeeks) : FString();
		RepairsText->SetText(FText::FromString(FString::Printf(TEXT("%sRepairs  %d / %d"), *WeekText, Fixed, Total)));
	}
}

void UFixHimHUDWidget::ShowToast(const FString& Message, float Seconds, bool bChime)
{
	if (!ToastPill)
	{
		return;
	}
	ToastText->SetText(FText::FromString(Message));
	ToastPill->SetVisibility(ESlateVisibility::HitTestInvisible);
	ToastTime = Seconds;
	if (bChime)
	{
		FixHim::Sfx(this, "Toast");
	}
}

void UFixHimHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	if (ToastTime > 0.f)
	{
		ToastTime -= InDeltaTime;
		ToastPill->SetRenderOpacity(FMath::Clamp(ToastTime / 0.4f, 0.f, 1.f));
		if (ToastTime <= 0.f)
		{
			ToastPill->SetVisibility(ESlateVisibility::Collapsed);
		}
	}

	TickReticle(InDeltaTime);

	if (RoomFlash > 0.f && RoomPill)
	{
		RoomFlash = FMath::Max(0.f, RoomFlash - InDeltaTime * 1.5f);
		RoomPill->SetRenderScale(FVector2D(FixHimDesign::ReducedMotion() ? 1.f : 1.f + .12f*RoomFlash));
	}
}
