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
#include "Components/ScaleBox.h"
#include "Components/ScrollBox.h"
#include "Components/EditableTextBox.h"
#include "Components/ScrollBoxSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "InputCoreTypes.h"

namespace FixHimUI
{
// Weak keys preserve authored point sizes without retaining screens after dismissal.
static TMap<TWeakObjectPtr<UTextBlock>, int32> AuthoredTextSizes;

FSlateFontInfo Font(int32 Size, const TCHAR *Typeface)
{
	// Strong references keep imported runtime fonts alive and package paths are explicitly cooked.
	static auto BuildFont = [](const TArray<FString> &Names) {
		UFont *F = NewObject<UFont>();
		F->FontCacheType = EFontCacheType::Runtime;
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
	// Type rule: titles use Barlow Condensed ExtraBold; all other text is Barlow SemiBold. Both are upright cuts that
	// MakeText (or a parent block) shears the full 12 degrees, so glyphs and wrapped lines step along the same grid.
	// Legacy names (Regular/Semibold/Bold/Italic/Lean) all resolve to the body face.
	static TStrongObjectPtr<UFont> Display = BuildFont({TEXT("BarlowCondensed-ExtraBold")});
	static TStrongObjectPtr<UFont> Body = BuildFont({TEXT("Barlow-SemiBold")});
	const bool IsDisplay = FCString::Strncmp(Typeface, TEXT("Display"), 7) == 0;
	UFont *Asset = IsDisplay ? Display.Get() : Body.Get();
	const int32 ScaledSize = FMath::RoundToInt(Size * FixHimDesign::TextScale());
	return Asset && !Asset->GetCompositeFont()->DefaultTypeface.Fonts.IsEmpty()
	           ? FSlateFontInfo(Asset, ScaledSize, FName("Regular"))
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
	const FVector2f Press = FixHimDesign::DepthOffset(FixHimDesign::ButtonBorder);
	Style.SetPressedPadding(FMargin(Press.X, Press.Y, -Press.X, -Press.Y)); // follows the face's press offset
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
	// All text leans 12 degrees. "...Face" typefaces leave the shear to a parent block (e.g. the dialogue line).
	if (!FString(Typeface).EndsWith(TEXT("Face")))
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
                                   int32 FontSize, bool bPrimary, const FString &LeadingIcon)
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
	UWidget *Content = B->Label;
	if (!LeadingIcon.IsEmpty())
	{
		auto *Row = Tree->ConstructWidget<UHorizontalBox>();
		auto *Box = Tree->ConstructWidget<USizeBox>();
		Box->SetWidthOverride(28);
		Box->SetHeightOverride(28);
		auto *Icon = FixHimDesign::Icon(Tree, LeadingIcon, FLinearColor::White);
		// Bound rather than foreground-tinted: cream faces want an orange icon beside an ink label.
		Icon->ColorAndOpacityDelegate.BindUFunction(B, GET_FUNCTION_NAME_CHECKED(UFixHimButton, GetIconTint));
		B->LeadingIcon = Icon;
		Box->AddChild(Icon);
		Row->AddChildToHorizontalBox(Box)->SetVerticalAlignment(VAlign_Center);
		// Fill, not auto: a wrapping label in an auto slot can settle on a too-narrow wrap width.
		UHorizontalBoxSlot *LabelSlot = Row->AddChildToHorizontalBox(B->Label);
		LabelSlot->SetPadding(FMargin(16, 0, 0, 0));
		LabelSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		LabelSlot->SetVerticalAlignment(VAlign_Center);
		B->Label->SetJustification(ETextJustify::Left);
		Content = Row;
	}
	if (auto *Slot = Cast<UButtonSlot>(B->AddChild(Content)))
	{
		// Icons sit closer to the slanted edge than bare labels (no focus pointer on icon buttons).
		Slot->SetPadding(FMargin(LeadingIcon.IsEmpty() ? 52 : 36, 16, 38, 16 + FixHimDesign::Extrusion));
		Slot->SetHorizontalAlignment(HAlign_Fill);
		// Fill, not centre: Slate's centred alignment offsets by (top - bottom) padding, which pulls content up
		// by half the extrusion allowance. Filling the padded box keeps the label centred on the face.
		Slot->SetVerticalAlignment(VAlign_Fill);
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

UFixHimButton *UFixHimButton::MakeStandalone(UWidgetTree *Tree, const FString &LabelText, TFunction<void()> InOnClick,
                                             bool bPrimary, const FString &LeadingIcon)
{
	using namespace FixHimDesign;
	UFixHimButton *B = Make(Tree, LabelText, MoveTemp(InOnClick), StandaloneLabel, bPrimary, LeadingIcon);
	B->bStandalone = true;
	if (auto *Slot = Cast<UButtonSlot>(B->GetContentSlot()))
	{
		// Taller face; the right and bottom also make room for the shadow beyond the extrusion.
		constexpr float PadY = 22.f;
		Slot->SetPadding(FMargin(LeadingIcon.IsEmpty() ? 56 : 38, PadY, 38 + ShadowExtraX,
		                         PadY + DepthReserveY(ButtonBorder, true)));
	}
	if (B->LeadingIcon)
	{
		if (auto *Box = Cast<USizeBox>(B->LeadingIcon->GetParent()))
		{
			Box->SetWidthOverride(36);
			Box->SetHeightOverride(36);
		}
		if (auto *LabelSlot = Cast<UHorizontalBoxSlot>(B->Label->Slot))
			LabelSlot->SetPadding(FMargin(20, 0, 0, 0));
	}
	return B;
}

FLinearColor UFixHimButton::GetIconTint()
{
	using namespace FixHimDesign;
	if (!GetIsEnabled())
		return DisabledInk;
	const bool Active = HasKeyboardFocus() || bSelected || IsPressed() || bPreviewPressed || IsHovered();
	return bPrimary || Active ? FLinearColor::White : Orange;
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
	BarBrush.DrawAs = ESlateBrushDrawType::NoDrawType;
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
	FSlateBrush Empty;
	Empty.ImageSize = FVector2D(32, 32);
	Empty.DrawAs = ESlateBrushDrawType::NoDrawType;
	Style.SetUncheckedImage(Empty).SetUncheckedHoveredImage(Empty).SetUncheckedPressedImage(Empty);
	Style.SetCheckedImage(Empty).SetCheckedHoveredImage(Empty).SetCheckedPressedImage(Empty);
	Style.SetForegroundColor(FSlateColor(FLinearColor::White));
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
		PopCard->SetRenderOpacity(0.f);
		bPopSettled = false;
		PopStableFrames = 0;
		PopLastSize = FVector2D::ZeroVector;
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
	const bool bHeaderMoved = SyncHeaderLayouts();
	if (PopCard && !bPopSettled)
	{
		// Wrapped text settles its height a frame or two after the first paint, and the header re-fits to it.
		// Showing that reflow reads as the layout breaking, so hold the card hidden until two quiet frames pass.
		const FVector2D PopSize = PopCard->GetDesiredSize();
		const bool bQuiet = !bHeaderMoved && PopSize.X > 0 && PopSize.Equals(PopLastSize, .5);
		PopLastSize = PopSize;
		PopStableFrames = bQuiet ? PopStableFrames + 1 : 0;
		if (PopStableFrames >= 2 || ShownAge > .5f)
		{
			bPopSettled = true;
			PopAge = 0.f;
			PopCard->SetRenderOpacity(1.f);
		}
	}
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
	if (PopCard && bPopSettled && PopAge < PopSeconds)
	{
		PopAge += InDeltaTime;
		const float S =
		    FixHimDesign::ReducedMotion() ? 1.f : FMath::Lerp(.96f, 1.f, FMath::Clamp(PopAge / PopSeconds, 0.f, 1.f));
		PopCard->SetRenderScale(FVector2D(S, S));
	}
}

namespace
{
// Surface faces leave this much of their box for the extrusion and shadow (see FixHimDesign Surface()).
constexpr float PlateDepthX = FixHimDesign::DepthReserveX(FixHimDesign::ButtonBorder),
                PlateDepthY = FixHimDesign::DepthReserveY(FixHimDesign::ButtonBorder);

} // namespace

UWidget *UFixHimWidget::MakeHeaderedSurface(UBorder *Surface, const FString &Title, const FMargin &Padding)
{
	using namespace FixHimUI;
	Surface->SetPadding(Padding);
	if (Title.IsEmpty())
		return Surface;
	auto *Heading = MakeText(WidgetTree, Title.ToUpper(), FixHimDesign::Heading, Cream, TEXT("Display"));
	Heading->SetJustification(ETextJustify::Center);
	HeaderTitle = Heading;
	auto *Header = WidgetTree->ConstructWidget<UFixHimSurface>();
	Header->SetBrush(Rounded(FixHimDesign::Teal, 12));
	Header->SetPadding(FMargin(32, 10, 40, 10 + FixHimDesign::Extrusion));
	Heading->SetRenderTranslation(FVector2D(0, Heading->GetFont().Size * FixHimDesign::CapCentre));
	// Long titles (the ending categories) shrink to fit the plate rather than spill past it; short ones are untouched.
	auto *Fit = WidgetTree->ConstructWidget<UScaleBox>();
	Fit->SetStretch(EStretch::ScaleToFit);
	Fit->SetStretchDirection(EStretchDirection::DownOnly);
	Fit->SetContent(Heading);
	Header->SetContent(Fit);
	return MakeHeaderedSurface(Surface, Header, Padding);
}

UWidget *UFixHimWidget::MakeHeaderedSurface(UBorder *Surface, UWidget *Header, const FMargin &Padding, float Inset)
{
	Surface->SetPadding(Padding);
	auto *Stack = WidgetTree->ConstructWidget<UOverlay>();
	UOverlaySlot *SurfaceSlot = Stack->AddChildToOverlay(Surface);
	SurfaceSlot->SetHorizontalAlignment(HAlign_Fill);
	SurfaceSlot->SetVerticalAlignment(VAlign_Fill);
	UOverlaySlot *HeaderSlot = Stack->AddChildToOverlay(Header);
	HeaderSlot->SetHorizontalAlignment(HAlign_Fill);
	HeaderSlot->SetVerticalAlignment(VAlign_Top);
	FHeaderLayout &Layout = HeaderLayouts.AddDefaulted_GetRef();
	Layout.Header = Header;
	Layout.Surface = Surface;
	Layout.Padding = Padding;
	Layout.Inset = Inset;
	SyncHeaderLayouts();
	return Stack;
}

bool UFixHimWidget::SyncHeaderLayouts()
{
	const float K = FixHimDesign::Slant;
	bool bMoved = false;
	for (FHeaderLayout &L : HeaderLayouts)
	{
		UWidget *Header = L.Header.Get();
		UBorder *Surface = L.Surface.Get();
		if (!Header || !Surface)
			continue;
		// Before the first layout pass, estimate from the heading size so the first frame is already close.
		// A collapsed header (e.g. dialogue narration) reserves nothing.
		const bool bShown = Header->GetVisibility() != ESlateVisibility::Collapsed;
		float HeaderH = bShown ? Header->GetDesiredSize().Y : 0.f;
		if (bShown && HeaderH <= 0)
			HeaderH = 28.f + 1.25f * FixHimDesign::Heading * FixHimDesign::TextScale() + PlateDepthY;
		float SurfaceH = Surface->GetCachedGeometry().GetLocalSize().Y;
		if (SurfaceH <= 0)
			SurfaceH = Surface->GetDesiredSize().Y;
		const FVector2D Measured(HeaderH, SurfaceH);
		if (Measured.Equals(L.Measured, .5))
			continue;
		L.Measured = Measured;
		bMoved = true;
		const float PlateFace = FMath::Max(0.f, HeaderH - PlateDepthY), Drop = PlateFace * .5f;
		const auto *DesignSurface = Cast<UFixHimSurface>(Surface);
		const float SurfaceBorder = DesignSurface ? DesignSurface->BorderWidth : FixHimDesign::ButtonBorder;
		const float SurfaceDepthX = FixHimDesign::DepthReserveX(SurfaceBorder),
		            SurfaceDepthY = FixHimDesign::DepthReserveY(SurfaceBorder);
		if (auto *SurfaceSlot = Cast<UOverlaySlot>(Surface->Slot))
			SurfaceSlot->SetPadding(FMargin(0, Drop, 0, 0));
		FMargin P = L.Padding;
		if (bShown)
			P.Top += HeaderH - Drop;
		if (L.bCentreRows)
		{
			// A UFixHimStack centres each row against its own box; the face is that box minus the extrusion and
			// shadow reserve (right, bottom), leaning 12 degrees. Measured at any row, the row sits right of the
			// face's centre by this much; move the padding over so rows centre on the face.
				// Rows are mostly buttons, and a button's box also holds its extrusion on the right. Centre the button's
			// top layer (face and keyline, no extrusion) on the card's top layer: subtract half its reserve too.
			const float Shift = (P.Left - P.Right) * .5f + SurfaceDepthX * .5f +
			                    K * (P.Top - P.Bottom + SurfaceDepthY) * .5f - PlateDepthX * .5f;
			P.Left -= Shift;
			P.Right += Shift;
		}
		Surface->SetPadding(P);
		// Both faces lean 12 degrees. At the plate's mid-height (the surface's top edge) the surface face spans
		// [FaceH*K, BoxW-SurfaceDepthX] and the plate face spans [Left + Drop*K, Left + PlateW - PlateDepthX - Drop*K].
		const float SurfaceFace = FMath::Max(0.f, SurfaceH - SurfaceDepthY);
		const float Left = SurfaceFace * K + L.Inset - Drop * K;
		const float Right = L.Inset - Drop * K + (SurfaceDepthX - PlateDepthX);
		if (auto *HeaderSlot = Cast<UOverlaySlot>(Header->Slot))
			HeaderSlot->SetPadding(FMargin(Left, 0, Right, 0));
	}
	return bMoved;
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

	UFixHimSurface *Card = WidgetTree->ConstructWidget<UFixHimSurface>();
	Card->SetBrush(Rounded(Cream, 28.f, Pink, 4.f));
	Card->BorderWidth = FixHimDesign::PopupBorder;
	CardSurface = Card;
	const FMargin CardPadding(32, 32, 40, 40);
	Size->AddChild(MakeHeaderedSurface(Card, Title, CardPadding));
	if (!Title.IsEmpty())
	{
		HeaderLayouts.Last().bCentreRows = true;
		HeaderLayouts.Last().Measured = FVector2D(-1, -1);
		SyncHeaderLayouts();
	}
	else
	{
		// Titleless (ending) cards: same centring as SyncHeaderLayouts, with fixed padding.
		using namespace FixHimDesign;
		const float Shift = (CardPadding.Left - CardPadding.Right) * .5f + DepthReserveX(PopupBorder) * .5f +
		                    Slant * (CardPadding.Top - CardPadding.Bottom + DepthReserveY(PopupBorder)) * .5f -
		                    DepthReserveX(ButtonBorder) * .5f;
		Card->SetPadding(FMargin(CardPadding.Left - Shift, CardPadding.Top, CardPadding.Right + Shift,
		                         CardPadding.Bottom));
	}
	Size->SetRenderTransformPivot(FVector2D(.5f, .5f));
	PopCard = Size;
	auto *Layout = WidgetTree->ConstructWidget<UFixHimStack>();
	// Long content (ending text) must not lean past the card's reserve; see UFixHimStack::MaxLean.
	constexpr float CardMaxLean = 120.f;
	Layout->MaxLean = CardMaxLean;
	Card->SetContent(Layout);
	// A rectangular scroll clip must stay inside both slanted edges. The outer stack
	// positions its centre; reserve half the maximum body's lean on either side.
	auto *Bounds = WidgetTree->ConstructWidget<USizeBox>();
	Bounds->SetMaxDesiredHeight(720);
	auto *Inset = WidgetTree->ConstructWidget<UBorder>();
	Inset->SetBrushColor(FLinearColor::Transparent);
	Inset->SetPadding(FMargin(60, 0, 60, 0));
	Bounds->AddChild(Inset);
	auto *Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Scroll->SetAnimateWheelScrolling(false);
	Scroll->SetScrollbarThickness(FVector2D(7, 7));
	FScrollBarStyle BarStyle = Scroll->GetWidgetBarStyle();
	BarStyle.SetNormalThumbImage(Rounded(FixHimDesign::Teal, 3));
	BarStyle.SetHoveredThumbImage(Rounded(FixHimDesign::Pink, 3));
	BarStyle.SetDraggedThumbImage(Rounded(FixHimDesign::Ink, 3));
	Scroll->SetWidgetBarStyle(BarStyle);
	Inset->SetContent(Scroll);
	// A grid stack, so rows of card content step along the 12-degree columns.
	auto *Col = WidgetTree->ConstructWidget<UFixHimStack>();
	Col->MaxLean = CardMaxLean;
	Scroll->AddChild(Col);
	Layout->AddChildToVerticalBox(Bounds);
	CardActions = WidgetTree->ConstructWidget<UFixHimStack>();
	Layout->AddChildToVerticalBox(CardActions)->SetPadding(FMargin(0, 20, 0, 0));
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
		const bool Display = true; // Replies use the display face too, matching the show-graphics mock-up.
		Label->SetFont(FixHimUI::Font(LabelSize, TEXT("Display")));
		FWidgetTransform Transform;
		Transform.Shear = Display ? FVector2D(-FMath::RadiansToDegrees(FMath::Atan(FixHimDesign::DisplayShear)), 0)
		                          : FVector2D::ZeroVector;
		Transform.Translation.Y = Label->GetFont().Size * FixHimDesign::CapCentre;
		Label->SetRenderTransform(Transform);
	}
	if (MyButton)
		MyButton->Invalidate(EInvalidateWidgetReason::Paint);
}
