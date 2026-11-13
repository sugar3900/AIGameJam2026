// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimLoadingWidget.h"
#include "Core/FixHimWarmupSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"
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

	// Fully opaque: the level behind is still preparing and must not be seen. Teal, like the title backdrop.
	UBorder* Backdrop = WidgetTree->ConstructWidget<UBorder>();
	Backdrop->SetBrushColor(FixHimDesign::Teal);
	Backdrop->SetVisibility(ESlateVisibility::Visible); // swallow clicks meant for the title underneath
	UOverlaySlot* BackdropSlot = Root->AddChildToOverlay(Backdrop);
	BackdropSlot->SetHorizontalAlignment(HAlign_Fill);
	BackdropSlot->SetVerticalAlignment(VAlign_Fill);

	// Logo, progress bar and caption on the shared 12-degree placement grid.
	UVerticalBox* Col = WidgetTree->ConstructWidget<UFixHimStack>();
	UOverlaySlot* ColSlot = Root->AddChildToOverlay(Col);
	ColSlot->SetHorizontalAlignment(HAlign_Center);
	ColSlot->SetVerticalAlignment(VAlign_Center);

	USizeBox* LogoBox = WidgetTree->ConstructWidget<USizeBox>();
	LogoBox->SetWidthOverride(420.f);
	LogoBox->SetHeightOverride(336.f);
	UImage* Logo = WidgetTree->ConstructWidget<UImage>();
	Logo->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr, TEXT("/Game/ICanFixHim/UI/Design/Brand/T_Logo.T_Logo")));
	LogoBox->AddChild(Logo);
	UVerticalBoxSlot* LogoSlot = Col->AddChildToVerticalBox(LogoBox);
	LogoSlot->SetHorizontalAlignment(HAlign_Center);
	LogoSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 36.f));

	// Same construction as the dialogue meters: thick cream track with a white rim, pink fill.
	USizeBox* BarBox = WidgetTree->ConstructWidget<USizeBox>();
	BarBox->SetWidthOverride(440.f);
	BarBox->SetHeightOverride(22.f);
	Bar = WidgetTree->ConstructWidget<UProgressBar>();
	FProgressBarStyle Style;
	Style.SetBackgroundImage(Rounded(Cream.CopyWithNewOpacity(.9f), 11.f, FLinearColor::White, 2.f));
	Style.SetFillImage(Rounded(FLinearColor::White, 11.f));
	Style.SetMarqueeImage(Rounded(FLinearColor::White, 11.f));
	Bar->SetWidgetStyle(Style);
	Bar->SetFillColorAndOpacity(FixHimDesign::Pink);
	Bar->SetPercent(0.f);
	BarBox->AddChild(Bar);
	Col->AddChildToVerticalBox(BarBox)->SetHorizontalAlignment(HAlign_Center);

	Caption = MakeText(WidgetTree, TEXT("Getting the place ready"), 22, Cream);
	UVerticalBoxSlot* CaptionSlot = Col->AddChildToVerticalBox(Caption);
	CaptionSlot->SetHorizontalAlignment(HAlign_Center);
	CaptionSlot->SetPadding(FMargin(0.f, 18.f, 0.f, 0.f));
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
