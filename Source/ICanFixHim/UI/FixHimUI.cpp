// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimUI.h"
#include "Player/FixHimPlayerController.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "Components/Border.h"
#include "Components/BorderSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Styling/CoreStyle.h"
#include "Framework/Application/SlateApplication.h"

namespace FixHimUI
{
	FSlateFontInfo Font(int32 Size, const TCHAR* Typeface)
	{
		return FCoreStyle::GetDefaultFontStyle(Typeface, Size);
	}

	FSlateBrush Rounded(const FLinearColor& Fill, float Radius, const FLinearColor& Outline, float OutlineWidth)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::RoundedBox;
		Brush.TintColor = FSlateColor(Fill);
		Brush.OutlineSettings = FSlateBrushOutlineSettings(FVector4(Radius, Radius, Radius, Radius), FSlateColor(Outline), OutlineWidth);
		Brush.OutlineSettings.RoundingType = ESlateBrushRoundingType::FixedRadius;
		return Brush;
	}

	FButtonStyle ButtonStyle(const FLinearColor& Normal, const FLinearColor& Hovered, const FLinearColor& Pressed, float Radius, const FLinearColor& Outline)
	{
		FButtonStyle Style;
		Style.SetNormal(Rounded(Normal, Radius, Outline, Outline.A > 0.f ? 2.f : 0.f));
		Style.SetHovered(Rounded(Hovered, Radius, Outline, Outline.A > 0.f ? 2.f : 0.f));
		Style.SetPressed(Rounded(Pressed, Radius, Outline, Outline.A > 0.f ? 2.f : 0.f));
		Style.SetDisabled(Rounded(Normal.CopyWithNewOpacity(0.35f), Radius));
		Style.SetNormalPadding(FMargin(18.f, 10.f));
		Style.SetPressedPadding(FMargin(18.f, 11.f, 18.f, 9.f));
		return Style;
	}

	UTextBlock* MakeText(UWidgetTree* Tree, const FString& Text, int32 Size, const FLinearColor& Color, const TCHAR* Typeface)
	{
		UTextBlock* T = Tree->ConstructWidget<UTextBlock>();
		T->SetText(FText::FromString(Text));
		T->SetFont(Font(Size, Typeface));
		T->SetColorAndOpacity(FSlateColor(Color));
		return T;
	}
}

// ---------------------------------------------------------------------------

void UFixHimButton::Init(TFunction<void()> InOnClick)
{
	OnClick = MoveTemp(InOnClick);
	OnClicked.AddUniqueDynamic(this, &UFixHimButton::HandleClicked);
	OnHovered.AddUniqueDynamic(this, &UFixHimButton::HandleHovered);
}

void UFixHimButton::HandleHovered()
{
	FixHim::Sfx(this, "ButtonHover", 1.f, 0.03f);
}

void UFixHimButton::HandleClicked()
{
	FixHim::Sfx(this, ClickSfx);
	if (OnClick)
	{
		OnClick();
	}
}

UFixHimButton* UFixHimButton::Make(UWidgetTree* Tree, const FString& LabelText, TFunction<void()> InOnClick, int32 FontSize, bool bPrimary)
{
	using namespace FixHimUI;
	UFixHimButton* B = Tree->ConstructWidget<UFixHimButton>();
	B->SetStyle(bPrimary
		? ButtonStyle(Pink, HotPink, Plum, 22.f)
		: ButtonStyle(Cream, Blush, Pink, 22.f, Pink));
	B->Label = MakeText(Tree, LabelText, FontSize, bPrimary ? FLinearColor::White : Plum, TEXT("Bold"));
	B->Label->SetJustification(ETextJustify::Center);
	B->AddChild(B->Label);
	B->Init(MoveTemp(InOnClick));
	static const TCHAR* const BackLabels[] = { TEXT("Back"), TEXT("Cancel"), TEXT("Close"), TEXT("Not yet"), TEXT("Never mind") };
	for (const TCHAR* BackLabel : BackLabels)
	{
		if (LabelText.StartsWith(BackLabel, ESearchCase::IgnoreCase))
		{
			B->ClickSfx = TEXT("ButtonBack");
		}
	}
	return B;
}

void UFixHimSlider::Init(TFunction<void(float)> InOnChanged)
{
	OnChanged = MoveTemp(InOnChanged);
	OnValueChanged.AddUniqueDynamic(this, &UFixHimSlider::HandleChanged);
}

void UFixHimSlider::ApplyBigStyle(const FLinearColor& Track, const FLinearColor& Handle)
{
	using namespace FixHimUI;
	constexpr float Thumb = 30.f;
	constexpr float ThumbHovered = 34.f;
	constexpr float Bar = 12.f;

	FSliderStyle Style = GetWidgetStyle();
	// White images, tinted by the bar / handle colours below.
	FSlateBrush BarBrush = Rounded(FLinearColor::White, Bar * 0.5f);
	BarBrush.ImageSize = FVector2D(Bar, Bar);
	Style.SetNormalBarImage(BarBrush);
	Style.SetHoveredBarImage(BarBrush);
	Style.SetDisabledBarImage(BarBrush);
	FSlateBrush ThumbBrush = Rounded(FLinearColor::White, Thumb * 0.5f, FLinearColor(1.f, 1.f, 1.f, 0.9f), 3.f);
	ThumbBrush.ImageSize = FVector2D(Thumb, Thumb);
	Style.SetNormalThumbImage(ThumbBrush);
	Style.SetDisabledThumbImage(ThumbBrush);
	FSlateBrush HoverBrush = Rounded(FLinearColor::White, ThumbHovered * 0.5f, FLinearColor::White, 4.f);
	HoverBrush.ImageSize = FVector2D(ThumbHovered, ThumbHovered);
	Style.SetHoveredThumbImage(HoverBrush);
	Style.SetBarThickness(Bar);
	SetWidgetStyle(Style);
	SetIndentHandle(true);
	SetSliderBarColor(Track);
	SetSliderHandleColor(Handle);
	// Grab the cursor's hand so it reads as draggable.
	SetCursor(EMouseCursor::GrabHand);
}

void UFixHimSlider::HandleChanged(float NewValue)
{
	// A soft tick every 5% of travel rather than on every pixel of the drag.
	const int32 Step = FMath::FloorToInt(GetNormalizedValue() * 20.f);
	if (Step != LastTickStep)
	{
		LastTickStep = Step;
		FixHim::Sfx(this, "SliderTick", 1.f, 0.f);
	}
	if (OnChanged)
	{
		OnChanged(NewValue);
	}
}

void UFixHimCheckBox::Init(TFunction<void(bool)> InOnChanged)
{
	OnChanged = MoveTemp(InOnChanged);
	OnCheckStateChanged.AddUniqueDynamic(this, &UFixHimCheckBox::HandleChanged);
}

void UFixHimCheckBox::HandleChanged(bool bChecked)
{
	FixHim::Sfx(this, bChecked ? "ToggleOn" : "ToggleOff");
	if (OnChanged)
	{
		OnChanged(bChecked);
	}
}

// ---------------------------------------------------------------------------

AFixHimPlayerController* UFixHimWidget::GetFixHimPC() const
{
	return Cast<AFixHimPlayerController>(GetOwningPlayer());
}

TSharedRef<SWidget> UFixHimWidget::RebuildWidget()
{
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		BuildUI();
	}
	return Super::RebuildWidget();
}

void UFixHimWidget::NativeConstruct()
{
	Super::NativeConstruct();
	PopAge = 0.f;
	ShownAge = 0.f;
	if (PopCard)
	{
		PopCard->SetRenderScale(FVector2D(0.01f, 0.01f));
		FixHim::Sfx(this, OpenSfx, 1.f, 0.03f);
	}
}

void UFixHimWidget::NativeDestruct()
{
	if (PopCard)
	{
		FixHim::Sfx(this, CloseSfx, 1.f, 0.03f);
	}
	Super::NativeDestruct();
}

FString UFixHimWidget::SimulateClickAt(const FVector2D& ScreenPos)
{
	// Deepest interactive control under the point (ForEachWidget visits parents before children).
	UWidget* Hit = nullptr;
	WidgetTree->ForEachWidget([&Hit, &ScreenPos](UWidget* W)
	{
		if ((W->IsA<USlider>() || W->IsA<UButton>() || W->IsA<UCheckBox>()) && W->IsVisible() && W->GetIsEnabled()
			&& W->GetCachedWidget().IsValid() && W->GetCachedGeometry().IsUnderLocation(ScreenPos))
		{
			Hit = W;
		}
	});
	TSet<FKey> Pressed;
	Pressed.Add(EKeys::LeftMouseButton);
	const FPointerEvent Down(0, 0, ScreenPos, ScreenPos, Pressed, EKeys::LeftMouseButton, 0.f, FModifierKeysState());
	const FPointerEvent Up(0, 0, ScreenPos, ScreenPos, TSet<FKey>(), EKeys::LeftMouseButton, 0.f, FModifierKeysState());
	if (Hit)
	{
		const TSharedPtr<SWidget> Slate = Hit->GetCachedWidget();
		const FGeometry Geo = Hit->GetCachedGeometry();
		if (UButton* Button = Cast<UButton>(Hit))
		{
			// SButton only clicks when Slate itself marked it hovered, which a simulated event can't do.
			Button->OnClicked.Broadcast();
		}
		else
		{
			Slate->OnMouseButtonDown(Geo, Down);
			Slate->OnMouseButtonUp(Geo, Up);
		}
		if (FSlateApplication::IsInitialized())
		{
			FSlateApplication::Get().ReleaseAllPointerCapture();
		}
		return FString::Printf(TEXT("control %s (%s, %.0fx%.0f)"), *Hit->GetName(), *Hit->GetClass()->GetName(), Geo.GetLocalSize().X, Geo.GetLocalSize().Y);
	}
	const UWidget* Card = GetOutsideClickCard();
	if (Card && Card->GetCachedGeometry().IsUnderLocation(ScreenPos))
	{
		return TEXT("inside the card, nothing clickable");
	}
	const FReply Reply = NativeOnMouseButtonDown(GetCachedGeometry(), Down);
	return Reply.IsEventHandled() ? TEXT("screen handled the click (outside the card)") : TEXT("screen ignored the click");
}

FReply UFixHimWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	if (InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton && ShownAge >= OutsideClickMinAge)
	{
		const UWidget* Card = GetOutsideClickCard();
		if (Card && Card->IsVisible() && !Card->GetCachedGeometry().IsUnderLocation(InMouseEvent.GetScreenSpacePosition()))
		{
			if (HandleClickOutside())
			{
				FixHim::Sfx(this, "ButtonBack");
				return FReply::Handled();
			}
		}
	}
	return Super::NativeOnMouseButtonDown(InGeometry, InMouseEvent);
}

void UFixHimWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	ShownAge += InDeltaTime;
	constexpr float PopSeconds = 0.22f;
	if (PopCard && PopAge < PopSeconds)
	{
		PopAge += InDeltaTime;
		const float S = FMath::Max(0.01f, FixHimUI::EaseOutBack(PopAge / PopSeconds));
		PopCard->SetRenderScale(FVector2D(S, S));
	}
}

UVerticalBox* UFixHimWidget::MakeCardScreen(const FString& Title, float Width)
{
	using namespace FixHimUI;

	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	UBorder* Dim = WidgetTree->ConstructWidget<UBorder>();
	Dim->SetBrushColor(FLinearColor(0.05f, 0.0f, 0.04f, 0.55f));
	UOverlaySlot* DimSlot = Root->AddChildToOverlay(Dim);
	DimSlot->SetHorizontalAlignment(HAlign_Fill);
	DimSlot->SetVerticalAlignment(VAlign_Fill);

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(Width);
	UOverlaySlot* SizeSlot = Root->AddChildToOverlay(Size);
	SizeSlot->SetHorizontalAlignment(HAlign_Center);
	SizeSlot->SetVerticalAlignment(VAlign_Center);

	UBorder* Card = WidgetTree->ConstructWidget<UBorder>();
	Card->SetBrush(Rounded(Cream, 28.f, Pink, 4.f));
	Card->SetPadding(FMargin(36.f, 28.f));
	Size->AddChild(Card);
	Size->SetRenderTransformPivot(FVector2D(0.5f, 0.5f));
	PopCard = Size;

	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	Card->SetContent(Col);

	UTextBlock* Heading = MakeText(WidgetTree, Title, 34, HotPink, TEXT("Bold"));
	Heading->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(Heading)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));
	return Col;
}
