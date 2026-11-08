// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimHUDWidget.h"
#include "Audio/FixHimSfxSubsystem.h"
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

	// A plain white dot that never changes during gameplay; the prompt pill below says what you're hovering.
	Dot = WidgetTree->ConstructWidget<UBorder>();
	Dot->SetBrush(Rounded(FLinearColor(1.f, 1.f, 1.f, 0.9f), 5.f, FLinearColor(0.2f, 0.f, 0.15f, 0.8f), 1.5f));
	USizeBox* DotBox = WidgetTree->ConstructWidget<USizeBox>();
	DotBox->SetWidthOverride(10.f);
	DotBox->SetHeightOverride(10.f);
	DotBox->AddChild(Dot);
	Ret->AddChildToVerticalBox(DotBox)->SetHorizontalAlignment(HAlign_Center);

	PromptPill = WidgetTree->ConstructWidget<UBorder>();
	PromptPill->SetBrush(Rounded(FLinearColor(Plum.R, Plum.G, Plum.B, 0.8f), 14.f));
	PromptPill->SetPadding(FMargin(14.f, 5.f));
	PromptText = MakeText(WidgetTree, TEXT(""), 18, Cream, TEXT("Bold"));
	PromptPill->SetContent(PromptText);
	PromptPill->SetVisibility(ESlateVisibility::Collapsed);
	// Its own slot, shifted below the dot, so the dot stays exactly at screen centre whether or not a prompt shows.
	PromptPill->SetRenderTranslation(FVector2D(0.f, 36.f));
	UOverlaySlot* PromptSlot = Root->AddChildToOverlay(PromptPill);
	PromptSlot->SetHorizontalAlignment(HAlign_Center);
	PromptSlot->SetVerticalAlignment(VAlign_Center);

	// ---- Room name (top left) ----
	RoomPill = WidgetTree->ConstructWidget<UBorder>();
	RoomPill->SetBrush(Rounded(FLinearColor(Plum.R, Plum.G, Plum.B, 0.72f), 18.f, Pink, 2.f));
	RoomPill->SetPadding(FMargin(20.f, 8.f));
	RoomText = MakeText(WidgetTree, TEXT(""), 22, Cream, TEXT("Bold"));
	RoomPill->SetContent(RoomText);
	UOverlaySlot* RoomSlot = Root->AddChildToOverlay(RoomPill);
	RoomSlot->SetHorizontalAlignment(HAlign_Left);
	RoomSlot->SetVerticalAlignment(VAlign_Top);
	RoomSlot->SetPadding(FMargin(28.f, 24.f));
	RoomPill->SetVisibility(ESlateVisibility::Collapsed);

	// ---- Repairs (top right) ----
	UBorder* RepPill = WidgetTree->ConstructWidget<UBorder>();
	RepPill->SetBrush(Rounded(FLinearColor(Plum.R, Plum.G, Plum.B, 0.72f), 18.f));
	RepPill->SetPadding(FMargin(18.f, 8.f));
	RepairsText = MakeText(WidgetTree, TEXT("Repairs 0/0"), 18, Blush, TEXT("Bold"));
	RepPill->SetContent(RepairsText);
	UOverlaySlot* RepSlot = Root->AddChildToOverlay(RepPill);
	RepSlot->SetHorizontalAlignment(HAlign_Right);
	RepSlot->SetVerticalAlignment(VAlign_Top);
	RepSlot->SetPadding(FMargin(28.f, 24.f));

	// ---- Controls hint (bottom left) ----
	UTextBlock* Hint = MakeText(WidgetTree, TEXT("WASD move   Mouse look   Click interact   M floor plan   Esc pause   Bed or door = end the day"), 15, FLinearColor(1.f, 1.f, 1.f, 0.75f));
	Hint->SetShadowOffset(FVector2D(1.f, 1.f));
	Hint->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.7f));
	UOverlaySlot* HintSlot = Root->AddChildToOverlay(Hint);
	HintSlot->SetHorizontalAlignment(HAlign_Left);
	HintSlot->SetVerticalAlignment(VAlign_Bottom);
	HintSlot->SetPadding(FMargin(28.f, 20.f));

	// ---- Toast (top centre) ----
	ToastPill = WidgetTree->ConstructWidget<UBorder>();
	ToastPill->SetBrush(Rounded(Pink, 16.f));
	ToastPill->SetPadding(FMargin(18.f, 7.f));
	ToastText = MakeText(WidgetTree, TEXT(""), 18, FLinearColor::White, TEXT("Bold"));
	ToastPill->SetContent(ToastText);
	UOverlaySlot* ToastSlot = Root->AddChildToOverlay(ToastPill);
	ToastSlot->SetHorizontalAlignment(HAlign_Center);
	ToastSlot->SetVerticalAlignment(VAlign_Top);
	ToastSlot->SetPadding(FMargin(0.f, 26.f));
	ToastPill->SetVisibility(ESlateVisibility::Collapsed);
}

void UFixHimHUDWidget::SetReticle(bool bVisible, bool bPointer, const FText& Prompt)
{
	if (!ReticleRoot)
	{
		return;
	}
	ReticleRoot->SetVisibility(bVisible ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	PromptPill->SetVisibility(bVisible && bPointer && !Prompt.IsEmpty() ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	PromptText->SetText(Prompt);
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

	if (RoomFlash > 0.f && RoomPill)
	{
		RoomFlash = FMath::Max(0.f, RoomFlash - InDeltaTime * 1.5f);
		RoomPill->SetRenderScale(FVector2D(1.f + 0.12f * RoomFlash));
	}
}
