// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimLoadingWidget.h"
#include "Core/FixHimWarmupSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/HorizontalBox.h"
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

	// Logo, progress bar and caption on one centred axis. Not a UFixHimStack: its 12-degree stagger pushes the top
	// rows right of the bottom ones, which reads as off-centre on a bare backdrop.
	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	UOverlaySlot* ColSlot = Root->AddChildToOverlay(Col);
	ColSlot->SetHorizontalAlignment(HAlign_Center);
	ColSlot->SetVerticalAlignment(VAlign_Center);

	USizeBox* LogoBox = WidgetTree->ConstructWidget<USizeBox>();
	LogoBox->SetWidthOverride(420.f);
	LogoBox->SetHeightOverride(336.f);
	UImage* Logo = WidgetTree->ConstructWidget<UImage>();
	Logo->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr, TEXT("/Game/ICanFixHim/UI/Design/Brand/T_Logo.T_Logo")));
	LogoBox->AddChild(Logo);
	// The heart pokes out on the right, so the art's bounds sit ~4.5 px right of the texture's centre. Nudge it back
	// with a render offset (layout untouched) so the logo lines up with the bar and caption.
	LogoBox->SetRenderTranslation(FVector2D(-4.5f, 0.f));
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

	// The animated dots live in a fixed-width box beside the caption, mirrored by an empty box on the other side,
	// so the words stay centred under the bar instead of shuffling left as dots are added.
	UHorizontalBox* CaptionRow = WidgetTree->ConstructWidget<UHorizontalBox>();
	auto DotsBox = [this]()
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetWidthOverride(DotsWidth * FixHimDesign::TextScale()); // the caption font follows text size too
		return Box;
	};
	CaptionRow->AddChildToHorizontalBox(DotsBox());
	CaptionRow->AddChildToHorizontalBox(MakeText(WidgetTree, TEXT("Getting the place ready"), 22, Cream));
	USizeBox* DotsSlot = DotsBox();
	Caption = MakeText(WidgetTree, TEXT(""), 22, Cream);
	DotsSlot->AddChild(Caption);
	CaptionRow->AddChildToHorizontalBox(DotsSlot);
	UVerticalBoxSlot* CaptionSlot = Col->AddChildToVerticalBox(CaptionRow);
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
		Caption->SetText(FText::FromString(Dots[int32(Age * 2.5f) % 4]));
	}
}
