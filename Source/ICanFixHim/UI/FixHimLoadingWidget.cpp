// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimLoadingWidget.h"
#include "Core/FixHimWarmupSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/ProgressBar.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

using namespace FixHimUI;

void UFixHimLoadingWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	// Fully opaque: the level behind is still preparing and must not be seen.
	UBorder* Backdrop = WidgetTree->ConstructWidget<UBorder>();
	Backdrop->SetBrushColor(Plum);
	Backdrop->SetVisibility(ESlateVisibility::Visible); // swallow clicks meant for the title underneath
	UOverlaySlot* BackdropSlot = Root->AddChildToOverlay(Backdrop);
	BackdropSlot->SetHorizontalAlignment(HAlign_Fill);
	BackdropSlot->SetVerticalAlignment(VAlign_Fill);

	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	UOverlaySlot* ColSlot = Root->AddChildToOverlay(Col);
	ColSlot->SetHorizontalAlignment(HAlign_Center);
	ColSlot->SetVerticalAlignment(VAlign_Center);

	UTextBlock* Small = MakeText(WidgetTree, TEXT("I CAN"), 32, Blush, TEXT("Bold"));
	Col->AddChildToVerticalBox(Small)->SetHorizontalAlignment(HAlign_Center);
	UTextBlock* Big = MakeText(WidgetTree, TEXT("FIX HIM"), 84, Pink, TEXT("Bold"));
	Big->SetShadowOffset(FVector2D(4.f, 4.f));
	Big->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.55f));
	UVerticalBoxSlot* BigSlot = Col->AddChildToVerticalBox(Big);
	BigSlot->SetHorizontalAlignment(HAlign_Center);
	BigSlot->SetPadding(FMargin(0.f, -18.f, 0.f, 36.f));

	USizeBox* BarBox = WidgetTree->ConstructWidget<USizeBox>();
	BarBox->SetWidthOverride(420.f);
	BarBox->SetHeightOverride(14.f);
	Bar = WidgetTree->ConstructWidget<UProgressBar>();
	FProgressBarStyle Style;
	Style.SetBackgroundImage(Rounded(PlumSoft, 7.f));
	Style.SetFillImage(Rounded(FLinearColor::White, 7.f));
	Style.SetMarqueeImage(Rounded(FLinearColor::White, 7.f));
	Bar->SetWidgetStyle(Style);
	Bar->SetFillColorAndOpacity(Pink);
	Bar->SetPercent(0.f);
	BarBox->AddChild(Bar);
	Col->AddChildToVerticalBox(BarBox)->SetHorizontalAlignment(HAlign_Center);

	Caption = MakeText(WidgetTree, TEXT("Getting the place ready"), 22, Cream);
	UVerticalBoxSlot* CaptionSlot = Col->AddChildToVerticalBox(Caption);
	CaptionSlot->SetHorizontalAlignment(HAlign_Center);
	CaptionSlot->SetPadding(FMargin(0.f, 16.f, 0.f, 0.f));
}

void UFixHimLoadingWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;

	// Visuals only: the player controller decides when loading is over and fades this screen out.
	const UFixHimWarmupSubsystem* Warmup = UFixHimWarmupSubsystem::Get(this);
	const bool bReady = !Warmup || Warmup->IsWarmed();
	const float Target = Warmup ? Warmup->GetProgress() : 1.f;

	// Ease the bar toward the real value so a jump in the count doesn't look jerky.
	ShownProgress = bReady ? 1.f : FMath::FInterpTo(ShownProgress, Target, InDeltaTime, 6.f);
	if (Bar)
	{
		Bar->SetPercent(ShownProgress);
	}
	if (Caption && !bReady)
	{
		static const TCHAR* Dots[] = { TEXT(""), TEXT("."), TEXT(".."), TEXT("...") };
		Caption->SetText(FText::FromString(FString(TEXT("Getting the place ready")) + Dots[int32(Age * 2.5f) % 4]));
	}
}
