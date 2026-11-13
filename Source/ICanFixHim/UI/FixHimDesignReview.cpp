#include "UI/FixHimDesignReview.h"
#include "Player/FixHimPlayerController.h"
#include "Blueprint/WidgetTree.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/SizeBox.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "Framework/Application/SlateApplication.h"
using namespace FixHimUI;
void UFixHimDesignReviewWidget::BuildUI()
{
	auto *Col = MakeCardScreen(TEXT("THE COMPONENT WORKSHOP"), 1400);
	auto Section = [&](const FString &Title) {
		auto *T = MakeText(WidgetTree, Title, 16, PlumSoft, TEXT("Semibold"));
		Col->AddChildToVerticalBox(T)->SetPadding(FMargin(0, 12, 0, 8));
	};
	auto Row = [&]() {
		auto *R = WidgetTree->ConstructWidget<UHorizontalBox>();
		Col->AddChildToVerticalBox(R)->SetPadding(FMargin(0, 0, 0, 12));
		return R;
	};
	auto Sample = [&](UHorizontalBox *R, const FString &Label, bool Primary, bool Focused, bool Pressed, bool Enabled) {
		auto *B = UFixHimButton::Make(WidgetTree, Label, [] {}, 22, Primary);
		B->bSelected = Focused;
		B->bPreviewPressed = Pressed;
		B->SetIsEnabled(Enabled);
		R->AddChildToHorizontalBox(B)->SetPadding(FMargin(0, 0, 16, 0));
	};
	Section(TEXT("BUTTONS / SAME CONSTRUCTION IN EVERY STATE"));
	auto *R = Row();
	Sample(R, TEXT("Primary"), true, false, false, true);
	Sample(R, TEXT("Focus"), true, true, false, true);
	Sample(R, TEXT("Pressed"), true, false, true, true);
	Sample(R, TEXT("Disabled"), true, false, false, false);
	R = Row();
	Sample(R, TEXT("Secondary"), false, false, false, true);
	Sample(R, TEXT("Selected"), false, true, false, true);
	Sample(R, TEXT("Disabled"), false, false, false, false);
	Section(TEXT("READING & REPLIES / FULL AUTHORED COPY"));
	auto *Body = MakeText(
	    WidgetTree, TEXT("Barlow Regular for reading. Semibold for emphasis. Body text stays upright."), 22, Plum);
	Body->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Body)->SetPadding(FMargin(0, 0, 0, 16));
	auto *Reply = UFixHimButton::Make(
	    WidgetTree,
	    TEXT("1.  Because somebody loved it. And because I love it. All of it. Including the part that argues."), [] {},
	    22, false);
	Reply->SetVariant(EFixHimButtonVariant::Reply);
	Reply->Label->SetJustification(ETextJustify::Left);
	Col->AddChildToVerticalBox(Reply);
	Section(TEXT("CONTROLS / KEYBOARD, MOUSE & GAMEPAD"));
	R = Row();
	auto *Slider = WidgetTree->ConstructWidget<UFixHimSlider>();
	Slider->SetValue(.65f);
	Slider->ApplyBigStyle(Blush, PlumSoft);
	Slider->Init([](float) {});
	auto *Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetWidthOverride(300);
	Box->SetHeightOverride(48);
	Box->AddChild(Slider);
	R->AddChildToHorizontalBox(Box);
	auto *Check = WidgetTree->ConstructWidget<UFixHimCheckBox>();
	Check->SetIsChecked(true);
	Check->Init([](bool) {});
	R->AddChildToHorizontalBox(Check);
	R->AddChildToHorizontalBox(MakeText(WidgetTree, TEXT("Checked"), 22, Plum))->SetVerticalAlignment(VAlign_Center);
	Section(TEXT("PHOSPHOR BOLD / ONE WEIGHT, UPRIGHT GEOMETRY"));
	R = Row();
	for (const TCHAR *Name : {TEXT("heart"), TEXT("users"), TEXT("lightning"), TEXT("wrench"), TEXT("house"),
	                          TEXT("gear"), TEXT("eye"), TEXT("chat_circle_text")})
	{
		auto *I = FixHimDesign::Icon(WidgetTree, Name, PlumSoft);
		auto *B = WidgetTree->ConstructWidget<USizeBox>();
		B->SetWidthOverride(36);
		B->SetHeightOverride(36);
		B->AddChild(I);
		R->AddChildToHorizontalBox(B)->SetPadding(FMargin(0, 0, 20, 0));
	}
	auto *Hint = MakeText(WidgetTree,
	                      TEXT("12° shared contours and placement grid · Upright reading text · Tab / arrows to "
	                           "navigate · Enter / A to activate"),
	                      16, PlumSoft);
	Hint->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Hint)->SetPadding(FMargin(0, 16));
	TWeakObjectPtr<UFixHimDesignReviewWidget> Self(this);
	CardActions->AddChildToVerticalBox(UFixHimButton::Make(
	    WidgetTree, TEXT("Close workshop"),
	    [Self]() {
		    if (Self.IsValid())
			    Self->HandleClickOutside();
	    },
	    22, false));
}
bool UFixHimDesignReviewWidget::HandleClickOutside()
{
	RemoveFromParent();
	if (OnClose)
		OnClose();
	return true;
}
#if !UE_BUILD_SHIPPING
namespace
{
FAutoConsoleCommandWithWorld Workshop(
    TEXT("FixHim.DesignSystem"), TEXT("Open the reusable UI component workshop."),
    FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld *World) {
	    auto *PC = World ? Cast<AFixHimPlayerController>(World->GetFirstPlayerController()) : nullptr;
	    if (!PC)
		    return;
	    const TWeakPtr<SWidget> PreviousFocus = FSlateApplication::Get().GetKeyboardFocusedWidget();
	    const bool WasPlaying = PC->GetState() == EFixHimState::Playing;
	    if (WasPlaying)
		    PC->SetPaused(true);
	    auto *W = CreateWidget<UFixHimDesignReviewWidget>(PC);
	    W->OnClose = [Weak = TWeakObjectPtr<AFixHimPlayerController>(PC), WasPlaying, PreviousFocus]() {
		    if (Weak.IsValid() && WasPlaying)
			    Weak->SetPaused(false);
		    else if (auto Focus = PreviousFocus.Pin())
			    FSlateApplication::Get().SetKeyboardFocus(Focus, EFocusCause::SetDirectly);
	    };
	    W->AddToViewport(1000);
	    PC->bShowMouseCursor = true;
	    FInputModeGameAndUI Mode;
	    Mode.SetWidgetToFocus(W->TakeWidget());
	    Mode.SetHideCursorDuringCapture(false);
	    PC->SetInputMode(Mode);
    }));
} // namespace
#endif
