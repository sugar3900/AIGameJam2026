// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimUI.h"
#include "Player/FixHimPlayerController.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "Components/Border.h"
#include "Components/BorderSlot.h"
#include "Components/ButtonSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Styling/CoreStyle.h"
#include "Framework/Application/SlateApplication.h"
#include "Engine/Font.h"
#include "Engine/FontFace.h"
#include "Engine/Texture2D.h"
#include "Fonts/CompositeFont.h"
#include "UObject/StrongObjectPtr.h"
#include "Components/ScrollBox.h"
#include "Components/EditableTextBox.h"
#include "Components/ScrollBoxSlot.h"
#include "InputCoreTypes.h"

namespace FixHimUI
{
// Weak keys preserve authored point sizes without retaining screens after dismissal.
static TMap<TWeakObjectPtr<UTextBlock>, int32> AuthoredTextSizes;

FSlateFontInfo Font(int32 Size, const TCHAR *Typeface)
{
	// Strong references keep imported runtime fonts alive and package paths are explicitly cooked.
	static auto BuildFont = [](bool DisplayFont) {
		UFont *F = NewObject<UFont>();
		F->FontCacheType = EFontCacheType::Runtime;
		const TArray<FString> Names = DisplayFont ? TArray<FString>{TEXT("BarlowCondensed-ExtraBoldItalic")}
		                                          : TArray<FString>{TEXT("Barlow-Regular"), TEXT("Barlow-SemiBold")};
		for (int I = 0; I < Names.Num(); ++I)
		{
			const FString Path = FString::Printf(TEXT("/Game/ICanFixHim/UI/Design/Fonts/%s.%s"), *Names[I], *Names[I]);
			if (auto *Face = LoadObject<UFontFace>(nullptr, *Path))
			{
				FTypefaceEntry Entry(I == 0 ? FName("Regular") : FName("Semibold"));
				Entry.Font = FFontData(Face);
				F->GetMutableInternalCompositeFont().DefaultTypeface.Fonts.Add(Entry);
			}
		}
		return TStrongObjectPtr<UFont>(F);
	};
	static TStrongObjectPtr<UFont> Body = BuildFont(false);
	static TStrongObjectPtr<UFont> Display = BuildFont(true);
	const bool IsDisplay = FCString::Strcmp(Typeface, TEXT("Display")) == 0;
	UFont *Asset = IsDisplay ? Display.Get() : Body.Get();
	const int32 ScaledSize = FMath::RoundToInt(Size * FixHimDesign::TextScale());
	return Asset && !Asset->GetCompositeFont()->DefaultTypeface.Fonts.IsEmpty()
	           ? FSlateFontInfo(Asset, ScaledSize,
			                    IsDisplay ? FName("Regular")
			                    : FCString::Strstr(Typeface, TEXT("Bold")) || FCString::Strstr(Typeface, TEXT("Semi"))
	                                ? FName("Semibold")
									: FName("Regular"))
			   : FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), ScaledSize);
}

FSlateBrush Rounded(const FLinearColor &Fill, float Radius, const FLinearColor &Outline, float OutlineWidth)
{
	FSlateBrush Brush;
	Brush.DrawAs = ESlateBrushDrawType::RoundedBox;
	Brush.TintColor = FSlateColor(Fill);
	Brush.OutlineSettings =
	    FSlateBrushOutlineSettings(FVector4(Radius, Radius, Radius, Radius), FSlateColor(Outline), OutlineWidth);
	Brush.OutlineSettings.RoundingType = ESlateBrushRoundingType::FixedRadius;
	return Brush;
}

FButtonStyle ButtonStyle(const FLinearColor &Normal, const FLinearColor &Hovered, const FLinearColor &Pressed,
                         float Radius, const FLinearColor &Outline)
{
	FButtonStyle Style;
	Style.SetNormal(Rounded(Normal, Radius, Outline, Outline.A > 0.f ? 2.f : 0.f));
	Style.SetHovered(Rounded(Hovered, Radius, Outline, Outline.A > 0.f ? 2.f : 0.f));
	Style.SetPressed(Rounded(Pressed, Radius, Outline, Outline.A > 0.f ? 2.f : 0.f));
	Style.SetDisabled(Rounded(FixHimDesign::Disabled, Radius, FixHimDesign::DisabledInk, 2));
	Style.SetDisabledForeground(FSlateColor(FixHimDesign::DisabledInk));
	Style.SetNormalPadding(FMargin(0));
	Style.SetPressedPadding(FMargin(2, 3, -2, -3));
	return Style;
}

UTextBlock *MakeText(UWidgetTree *Tree, const FString &Text, int32 Size, const FLinearColor &Color,
                     const TCHAR *Typeface)
{
	UTextBlock *T = Tree->ConstructWidget<UTextBlock>();
	T->SetText(FText::FromString(Text));
	T->SetFont(Font(Size, Typeface));
	AuthoredTextSizes.Add(T, Size);
	T->SetColorAndOpacity(FSlateColor(Color));
	if (FCString::Strcmp(Typeface, TEXT("Display")) == 0)
	{
		FWidgetTransform Transform;
		Transform.Shear = FVector2D(-FMath::RadiansToDegrees(FMath::Atan(FixHimDesign::DisplayShear)), 0);
		T->SetRenderTransform(Transform);
	}
	return T;
}
// Cached screens are reused by the controller. Apply the current option whenever one reopens,
// using authored sizes so repeated openings never accumulate rounding or scaling errors.
void RefreshTextScale(UWidgetTree *Tree)
{
	Tree->ForEachWidget([](UWidget *W) {
		if (auto *Text = Cast<UTextBlock>(W))
			if (const int32 *Size = AuthoredTextSizes.Find(Text))
			{
				auto Info = Text->GetFont();
				Info.Size = FMath::RoundToInt(*Size * FixHimDesign::TextScale());
				Text->SetFont(Info);
			}
	});
	for (auto It = AuthoredTextSizes.CreateIterator(); It; ++It)
		if (!It.Key().IsValid())
			It.RemoveCurrent();
}
} // namespace FixHimUI

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

UFixHimButton *UFixHimButton::Make(UWidgetTree *Tree, const FString &LabelText, TFunction<void()> InOnClick,
                                   int32 FontSize, bool bPrimary)
{
	using namespace FixHimUI;
	UFixHimButton *B = Tree->ConstructWidget<UFixHimButton>();
	B->SetStyle(ButtonStyle(Cream, Pink, Pink, 12, Gold));
	B->LabelSize = FontSize;
	B->Label = MakeText(Tree, LabelText, FontSize, bPrimary ? FLinearColor::White : Plum, TEXT("Semibold"));
	B->Label->SetColorAndOpacity(FSlateColor::UseForeground());
	B->Label->SetAutoWrapText(true);
	B->SetCursor(EMouseCursor::Hand);
	B->Label->SetJustification(ETextJustify::Center);
	if (auto *Slot = Cast<UButtonSlot>(B->AddChild(B->Label)))
	{
		Slot->SetPadding(FMargin(32, 8, 38, 24));
		Slot->SetHorizontalAlignment(HAlign_Fill);
	}
	B->SetVariant(bPrimary);
	B->Init(MoveTemp(InOnClick));
	static const TCHAR *const BackLabels[] = {TEXT("Back"), TEXT("Cancel"), TEXT("Close"), TEXT("Not yet"),
	                                          TEXT("Never mind")};
	for (const TCHAR *BackLabel : BackLabels)
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

void UFixHimSlider::ApplyBigStyle(const FLinearColor &Track, const FLinearColor &Handle)
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
	FCheckBoxStyle Style = GetWidgetStyle();
	FSlateBrush Empty = FixHimUI::Rounded(FixHimDesign::Cream, 8, FixHimDesign::Teal, 3);
	Empty.ImageSize = FVector2D(32, 32);
	FSlateBrush Hover = FixHimUI::Rounded(FixHimDesign::Cream, 8, FixHimDesign::Pink, 4);
	Hover.ImageSize = FVector2D(32, 32);
	FSlateBrush Check;
	Check.SetResourceObject(
	    LoadObject<UTexture2D>(nullptr, TEXT("/Game/ICanFixHim/UI/Design/Icons/T_Icon_check.T_Icon_check")));
	Check.ImageSize = FVector2D(32, 32);
	Check.TintColor = FSlateColor(FixHimDesign::Teal);
	Style.SetUncheckedImage(Empty).SetUncheckedHoveredImage(Hover).SetUncheckedPressedImage(Hover);
	Style.SetCheckedImage(Check).SetCheckedHoveredImage(Check).SetCheckedPressedImage(Check);
	Style.SetPadding(FMargin(8));
	SetWidgetStyle(Style);
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

AFixHimPlayerController *UFixHimWidget::GetFixHimPC() const
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
	FixHimUI::RefreshTextScale(WidgetTree);
	SetIsFocusable(true);
	PopAge = 0.f;
	bInitialFocus = false;
	ShownAge = 0.f;
	WidgetTree->ForEachWidget([](UWidget *W) {
		if (auto *B = Cast<UFixHimButton>(W))
		{
			if (B->Label && B->bDesignSurface)
				B->Label->SetColorAndOpacity(FSlateColor::UseForeground());
		}
	});
	if (PopCard)
	{
		PopCard->SetRenderScale(FVector2D(FixHimDesign::ReducedMotion() ? 1.f : .96f));
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

FString UFixHimWidget::SimulateClickAt(const FVector2D &ScreenPos)
{
	// Deepest interactive control under the point (ForEachWidget visits parents before children).
	UWidget *Hit = nullptr;
	WidgetTree->ForEachWidget([&Hit, &ScreenPos](UWidget *W) {
		if ((W->IsA<USlider>() || W->IsA<UButton>() || W->IsA<UCheckBox>()) && W->IsVisible() && W->GetIsEnabled() &&
		    W->GetCachedWidget().IsValid() && W->GetCachedGeometry().IsUnderLocation(ScreenPos))
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
		if (UButton *Button = Cast<UButton>(Hit))
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
		return FString::Printf(TEXT("control %s (%s, %.0fx%.0f)"), *Hit->GetName(), *Hit->GetClass()->GetName(),
		                       Geo.GetLocalSize().X, Geo.GetLocalSize().Y);
	}
	const UWidget *Card = GetOutsideClickCard();
	if (Card && Card->GetCachedGeometry().IsUnderLocation(ScreenPos))
	{
		return TEXT("inside the card, nothing clickable");
	}
	const FReply Reply = NativeOnMouseButtonDown(GetCachedGeometry(), Down);
	return Reply.IsEventHandled() ? TEXT("screen handled the click (outside the card)")
	                              : TEXT("screen ignored the click");
}

FReply UFixHimWidget::NativeOnMouseButtonDown(const FGeometry &InGeometry, const FPointerEvent &InMouseEvent)
{
	if (InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton && ShownAge >= OutsideClickMinAge)
	{
		const UWidget *Card = GetOutsideClickCard();
		if (Card && Card->IsVisible() &&
		    !Card->GetCachedGeometry().IsUnderLocation(InMouseEvent.GetScreenSpacePosition()))
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

void UFixHimWidget::NativeTick(const FGeometry &MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	ShownAge += InDeltaTime;
	if (!bInitialFocus && ShownAge > .12f)
	{
		bInitialFocus = true;
		bool Focused = false;
		WidgetTree->ForEachWidget([&](UWidget *W) { Focused |= W->HasKeyboardFocus(); });
		if (!Focused && InitialFocusTarget && InitialFocusTarget->IsVisible() && InitialFocusTarget->GetIsEnabled())
		{
			InitialFocusTarget->SetKeyboardFocus();
			Focused = true;
		}
		if (!Focused)
			WidgetTree->ForEachWidget([&](UWidget *W) {
				if (!Focused &&
				    (W->IsA<UButton>() || W->IsA<USlider>() || W->IsA<UCheckBox>() || W->IsA<UEditableTextBox>()) &&
				    W->IsVisible() && W->GetIsEnabled())
				{
					W->SetKeyboardFocus();
					Focused = true;
				}
			});
	}
	constexpr float PopSeconds = 0.22f;
	if (PopCard && PopAge < PopSeconds)
	{
		PopAge += InDeltaTime;
		const float S =
		    FixHimDesign::ReducedMotion() ? 1.f : FMath::Lerp(.96f, 1.f, FMath::Clamp(PopAge / PopSeconds, 0.f, 1.f));
		PopCard->SetRenderScale(FVector2D(S, S));
	}
}

UVerticalBox *UFixHimWidget::MakeCardScreen(const FString &Title, float Width)
{
	using namespace FixHimUI;

	UOverlay *Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	UBorder *Dim = WidgetTree->ConstructWidget<UBorder>();
	Dim->SetBrushColor(FixHimDesign::Scrim);
	UOverlaySlot *DimSlot = Root->AddChildToOverlay(Dim);
	DimSlot->SetHorizontalAlignment(HAlign_Fill);
	DimSlot->SetVerticalAlignment(VAlign_Fill);

	USizeBox *Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(Width);
	Size->SetMaxDesiredHeight(960);
	UOverlaySlot *SizeSlot = Root->AddChildToOverlay(Size);
	SizeSlot->SetHorizontalAlignment(HAlign_Center);
	SizeSlot->SetVerticalAlignment(VAlign_Center);

	UBorder *Card = WidgetTree->ConstructWidget<UFixHimSurface>();
	Card->SetBrush(Rounded(Cream, 28.f, Pink, 4.f));
	Card->SetPadding(FMargin(32, 32, 40, 40));
	UScrollBox *Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Scroll->SetConsumeMouseWheel(EConsumeMouseWheel::WhenScrollingPossible);
	Scroll->SetAnimateWheelScrolling(false);
	Size->AddChild(Card);
	Card->SetContent(Scroll);
	Size->SetRenderTransformPivot(FVector2D(0.5f, 0.5f));
	PopCard = Size;

	UVerticalBox *Col = WidgetTree->ConstructWidget<UFixHimStack>();
	Scroll->AddChild(Col);

	UTextBlock *Heading = MakeText(WidgetTree, Title.ToUpper(), FixHimDesign::Heading, Cream, TEXT("Display"));
	Heading->SetJustification(ETextJustify::Center);
	UFixHimSurface *Header = WidgetTree->ConstructWidget<UFixHimSurface>();
	Header->SetBrush(Rounded(FixHimDesign::Teal, 12));
	Header->SetPadding(FMargin(32, 8, 40, 20));
	Header->SetContent(Heading);
	Col->AddChildToVerticalBox(Header)->SetPadding(FMargin(0, 0, 0, 24));
	return Col;
}

void UFixHimButton::SetVariant(bool Primary, bool Selected)
{
	SetVariant(Primary ? EFixHimButtonVariant::Primary : EFixHimButtonVariant::Secondary);
	bSelected = Selected;
	if (MyButton)
		MyButton->Invalidate(EInvalidateWidgetReason::Paint);
}

FReply UFixHimWidget::NativeOnKeyDown(const FGeometry &Geometry, const FKeyEvent &Event)
{
	const FKey Key = Event.GetKey();
	if ((Key == EKeys::Escape || Key == EKeys::Gamepad_FaceButton_Right) && HandleClickOutside())
	{
		FixHim::Sfx(this, "ButtonBack");
		return FReply::Handled();
	}
	const bool Forward = Key == EKeys::Down || Key == EKeys::Gamepad_DPad_Down || Key == EKeys::Tab;
	const bool Back = Key == EKeys::Up || Key == EKeys::Gamepad_DPad_Up;
	if (Forward || Back)
	{
		TArray<UWidget *> Controls;
		WidgetTree->ForEachWidget([&](UWidget *W) {
			bool Visible = W->IsVisible() && W->GetIsEnabled();
			for (UWidget *P = W->GetParent(); P; P = P->GetParent())
				Visible &= P->IsVisible() && P->GetIsEnabled();
			if (Visible &&
			    (W->IsA<UButton>() || W->IsA<USlider>() || W->IsA<UCheckBox>() || W->IsA<UEditableTextBox>()))
				Controls.Add(W);
		});
		if (!Controls.IsEmpty())
		{
			int32 Current = Controls.IndexOfByPredicate([](UWidget *W) { return W->HasKeyboardFocus(); });
			const int32 Step = Back || (Key == EKeys::Tab && Event.IsShiftDown()) ? -1 : 1;
			const int32 Next = Current == INDEX_NONE ? 0 : (Current + Step + Controls.Num()) % Controls.Num();
			Controls[Next]->SetKeyboardFocus();
			for (UWidget *Parent = Controls[Next]->GetParent(); Parent; Parent = Parent->GetParent())
				if (auto *Scroll = Cast<UScrollBox>(Parent))
					Scroll->ScrollWidgetIntoView(Controls[Next], false, EDescendantScrollDestination::IntoView, 16);
			return FReply::Handled();
		}
	}
	return Super::NativeOnKeyDown(Geometry, Event);
}

void UFixHimButton::SetVariant(EFixHimButtonVariant InVariant)
{
	Variant = InVariant;
	bInlineTopic = InVariant == EFixHimButtonVariant::Topic;
	bDesignSurface = InVariant != EFixHimButtonVariant::Topic && InVariant != EFixHimButtonVariant::Spatial;
	bPrimary = InVariant == EFixHimButtonVariant::Primary;
	if (Label && bDesignSurface)
	{
		const bool Display = InVariant != EFixHimButtonVariant::Reply;
		Label->SetFont(FixHimUI::Font(LabelSize, Display ? TEXT("Display") : TEXT("Semibold")));
		FWidgetTransform Transform;
		Transform.Shear = Display ? FVector2D(-FMath::RadiansToDegrees(FMath::Atan(FixHimDesign::DisplayShear)), 0)
		                          : FVector2D::ZeroVector;
		Label->SetRenderTransform(Transform);
	}
	if (MyButton)
		MyButton->Invalidate(EInvalidateWidgetReason::Paint);
}
