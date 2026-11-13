// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimMenus.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Player/FixHimPlayerController.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/EditableTextBox.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/SizeBoxSlot.h"
#include "Components/Spacer.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

using namespace FixHimUI;

// ---------------------------------------------------------------------------
// Title

void UFixHimTitleWidget::BuildUI()
{
	UOverlay *Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	// No panel: the logo and large standalone buttons sit straight on the scene, stacked straight down the left
	// like the title concept (each face still slants; the column doesn't drift). Their shadows lift them off the room.
	UVerticalBox *Col = WidgetTree->ConstructWidget<UVerticalBox>();
	UOverlaySlot *ColSlot = Root->AddChildToOverlay(Col);
	ColSlot->SetHorizontalAlignment(HAlign_Left);
	ColSlot->SetVerticalAlignment(VAlign_Center);
	ColSlot->SetPadding(FMargin(110.f, 40.f, 0.f, 40.f));

	UVerticalBox *TitleCol = WidgetTree->ConstructWidget<UVerticalBox>();
	TitleBlock = TitleCol;
	UVerticalBoxSlot *TitleSlot = Col->AddChildToVerticalBox(TitleCol);
	TitleSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
	TitleSlot->SetHorizontalAlignment(HAlign_Center);

	USizeBox *LogoBox = WidgetTree->ConstructWidget<USizeBox>();
	// Sized so the logo plus five standalone buttons still fit 1080p at 135% text.
	LogoBox->SetWidthOverride(440);
	LogoBox->SetHeightOverride(352);
	UImage *Logo = WidgetTree->ConstructWidget<UImage>();
	Logo->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr, TEXT("/Game/ICanFixHim/UI/Design/Brand/T_Logo.T_Logo")));
	LogoBox->AddChild(Logo);
	TitleCol->AddChildToVerticalBox(LogoBox);

	TWeakObjectPtr<UFixHimTitleWidget> Self(this);
	auto AddButton = [&](const FString &Label, TFunction<void()> Fn, bool bPrimary) -> UFixHimButton * {
		USizeBox *Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetWidthOverride(460.f);
		UFixHimButton *B = UFixHimButton::MakeStandalone(WidgetTree, Label, MoveTemp(Fn), bPrimary,
		                                       Label == TEXT("Options")    ? TEXT("gear")
		                                       : Label == TEXT("Continue") ? TEXT("play")
		                                       : Label == TEXT("New Game") ? TEXT("house")
		                                       : Label == TEXT("Credits")  ? TEXT("info")
		                                                                   : TEXT("door_open"));
		Box->AddChild(B);
		Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 6.f));
		return B;
	};

	const auto *Saved = UFixHimSaveSubsystem::Get(this);
	const bool HasSave = Saved && Saved->HasSaveFile();
	auto NewGame = [&]() {
		NewGameButton = AddButton(
		    TEXT("New Game"),
		    [Self]() {
			    if (Self.IsValid() && Self->GetFixHimPC())
				    Self->GetFixHimPC()->StartNewGame();
		    },
		    !HasSave);
	};
	auto Continue = [&]() {
		ContinueButton = AddButton(
		    TEXT("Continue"),
		    [Self]() {
			    if (Self.IsValid() && Self->GetFixHimPC())
				    Self->GetFixHimPC()->ContinueGame();
		    },
		    HasSave);
	};
	if (HasSave)
	{
		Continue();
		NewGame();
	}
	else
	{
		NewGame();
		Continue();
	}
	AddButton(
	    TEXT("Options"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->OpenOptions();
		    }
	    },
	    false);
	AddButton(
	    TEXT("Credits"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->OpenCredits();
		    }
	    },
	    false);
	AddButton(
	    TEXT("Exit"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->QuitToDesktop();
		    }
	    },
	    false);


	RefreshContinue();
}

void UFixHimTitleWidget::RefreshContinue()
{
	if (ContinueButton)
	{
		const UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this);
		const bool HasSave = Save && Save->HasSaveFile();
		ContinueButton->SetIsEnabled(HasSave);
		ContinueButton->SetVariant(HasSave);
		if (NewGameButton)
			NewGameButton->SetVariant(!HasSave);
		InitialFocusTarget = HasSave ? ContinueButton.Get() : NewGameButton.Get();
	}
}

void UFixHimTitleWidget::NativeTick(const FGeometry &MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
}

// ---------------------------------------------------------------------------
// Name entry

void UFixHimNameEntryWidget::BuildUI()
{
	UVerticalBox *Col = MakeCardScreen(TEXT("Welcome home"), 720.f);
	TWeakObjectPtr<UFixHimNameEntryWidget> Self(this);

	UTextBlock *Prompt =
	    MakeText(WidgetTree, TEXT("You just bought a condemned house on Heartbreak Lane. What's your name, homeowner?"),
		         20, Plum);
	Prompt->SetJustification(ETextJustify::Center);
	Prompt->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Prompt)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));

	NameBox = WidgetTree->ConstructWidget<UEditableTextBox>();
	NameBox->SetHintText(FText::FromString(TEXT("Your name")));
	FEditableTextBoxStyle Style = NameBox->WidgetStyle;
	Style.SetBackgroundImageNormal(Rounded(Cream, 12, PlumSoft, 2));
	Style.SetBackgroundImageHovered(Rounded(FLinearColor::White, 14.f, HotPink, 2.f));
	Style.SetBackgroundImageFocused(Rounded(FLinearColor::White, 14.f, HotPink, 3.f));
	Style.SetPadding(FMargin(16.f, 12.f));
	Style.SetFont(Font(24, TEXT("Bold")));
	Style.SetForegroundColor(FSlateColor(Plum));
	NameBox->WidgetStyle = Style;
	NameBox->SetJustification(ETextJustify::Center);
	NameBox->OnTextChanged.AddUniqueDynamic(this, &UFixHimNameEntryWidget::HandleTextChanged);
	NameBox->OnTextCommitted.AddUniqueDynamic(this, &UFixHimNameEntryWidget::HandleTextCommitted);
	Col->AddChildToVerticalBox(NameBox)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));

	USizeBox *Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetMinDesiredHeight(72.f);
	MoveInButton = UFixHimButton::Make(
	    WidgetTree, TEXT("Move in"),
	    [Self]() {
		    if (Self.IsValid())
		    {
			    Self->Submit();
		    }
	    },
	    24, true);
	// Greyed out (not just faded pink) while the name is empty.
	FButtonStyle BStyle = MoveInButton->GetStyle();
	BStyle.SetDisabled(Rounded(FixHimDesign::DisabledMid, 12, FixHimDesign::DisabledLight, 2));
	MoveInButton->SetStyle(BStyle);
	MoveInButton->SetIsEnabled(false);
	Box->AddChild(MoveInButton);
	CardActions->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 10.f));

	USizeBox *BackBox = WidgetTree->ConstructWidget<USizeBox>();
	BackBox->SetMinDesiredHeight(72.f);
	BackBox->AddChild(UFixHimButton::Make(
	    WidgetTree, TEXT("Back"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->CancelNameEntry();
		    }
	    },
	    24, false));
	CardActions->AddChildToVerticalBox(BackBox);
}

void UFixHimNameEntryWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (NameBox)
	{
		// UE 5.8 retains the passed style address; pass the widget-owned member.
		NameBox->WidgetStyle.SetFont(Font(24, TEXT("Bold")));
		NameBox->SetWidgetStyle(NameBox->WidgetStyle);
		NameBox->SetKeyboardFocus();
	}
}

bool UFixHimNameEntryWidget::HandleClickOutside()
{
	AFixHimPlayerController *PC = GetFixHimPC();
	if (PC && CurrentName().IsEmpty())
	{
		PC->CancelNameEntry();
		return true;
	}
	return false;
}

FString UFixHimNameEntryWidget::CurrentName() const
{
	return NameBox ? NameBox->GetText().ToString().TrimStartAndEnd() : FString();
}

void UFixHimNameEntryWidget::HandleTextChanged(const FText &Text)
{
	// Keep it to a name that fits in the name plate.
	FString S = Text.ToString();
	if (S.Len() > 16)
	{
		S.LeftInline(16);
		NameBox->SetText(FText::FromString(S));
	}
	MoveInButton->SetIsEnabled(!CurrentName().IsEmpty());
}

void UFixHimNameEntryWidget::HandleTextCommitted(const FText &Text, ETextCommit::Type CommitMethod)
{
	if (CommitMethod == ETextCommit::OnEnter)
	{
		Submit();
	}
}

void UFixHimNameEntryWidget::Submit()
{
	const FString Name = CurrentName();
	if (!Name.IsEmpty() && GetFixHimPC())
	{
		GetFixHimPC()->BeginNewGame(Name);
	}
}

// ---------------------------------------------------------------------------
// Pause

void UFixHimPauseWidget::BuildUI()
{
	UVerticalBox *Col = MakeCardScreen(TEXT("Paused"), 620.f);
	OpenSfx = TEXT("PauseOn");
	CloseSfx = TEXT("PauseOff");
	TWeakObjectPtr<UFixHimPauseWidget> Self(this);
	auto Add = [&](const FString &Label, TFunction<void()> Fn, bool bPrimary) {
		USizeBox *Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetMinDesiredHeight(72.f);
		Box->AddChild(UFixHimButton::Make(WidgetTree, Label, MoveTemp(Fn), 22, bPrimary));
		CardActions->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
	};
	Add(
	    TEXT("Resume"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->SetPaused(false);
		    }
	    },
	    true);
	Add(
	    TEXT("Options"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->OpenOptions();
		    }
	    },
	    false);
	Add(
	    TEXT("Save & Exit"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->ReturnToMainMenu();
		    }
	    },
	    false);

	UTextBlock *Hint =
	    MakeText(WidgetTree, TEXT("Progress saves when you leave through the front door or Save & Exit."), 14, PlumSoft,
		         TEXT("Italic"));
	Hint->SetJustification(ETextJustify::Center);
	Hint->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Hint)->SetPadding(FMargin(0.f, 6.f, 0.f, 0.f));
}

bool UFixHimPauseWidget::HandleClickOutside()
{
	if (AFixHimPlayerController *PC = GetFixHimPC())
	{
		PC->SetPaused(false);
		return true;
	}
	return false;
}

// ---------------------------------------------------------------------------
// Door prompt

bool UFixHimDoorPromptWidget::HandleClickOutside()
{
	if (AFixHimPlayerController *PC = GetFixHimPC())
	{
		PC->CloseDoorPrompt();
		return true;
	}
	return false;
}

void UFixHimDoorPromptWidget::BuildUI()
{
	UVerticalBox *Col = MakeCardScreen(TEXT("End the day?"), 720.f);
	TWeakObjectPtr<UFixHimDoorPromptWidget> Self(this);

	BodyText = MakeText(WidgetTree, TEXT("The day ends and a week will pass."), 18, PlumSoft);
	BodyText->SetJustification(ETextJustify::Center);
	BodyText->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(BodyText)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));

	auto Add = [&](const FString &Label, TFunction<void()> Fn, bool bPrimary) {
		USizeBox *Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetMinDesiredHeight(72.f);
		UFixHimButton *Button = UFixHimButton::Make(WidgetTree, Label, MoveTemp(Fn), 22, bPrimary);
		if (bPrimary)
		{
			EndDayButton = Button;
		}
		Box->AddChild(Button);
		CardActions->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
	};
	Add(
	    TEXT("End Day"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->ConfirmEndDay();
		    }
	    },
	    true);
	Add(
	    TEXT("Cancel"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->CloseDoorPrompt();
		    }
	    },
	    false);
}

void UFixHimDoorPromptWidget::Refresh()
{
	const AFixHimPlayerController *PC = GetFixHimPC();
	const bool bAllowed = !PC || PC->CanEndDay();
	if (EndDayButton)
	{
		EndDayButton->SetIsEnabled(bAllowed);
	}
	if (BodyText)
	{
		BodyText->SetText(
		    FText::FromString(bAllowed ? TEXT("The day ends and a week will pass.")
			                           : TEXT("You feel a presence in the house... someone you still need to meet.")));
	}
}

// ---------------------------------------------------------------------------
// Options

bool UFixHimOptionsWidget::HandleClickOutside()
{
	if (UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this))
	{
		Save->SaveOptions();
	}
	if (AFixHimPlayerController *PC = GetFixHimPC())
	{
		PC->CloseSubMenu();
		return true;
	}
	return false;
}

void UFixHimOptionsWidget::BuildUI()
{
	UVerticalBox *Col = MakeCardScreen(TEXT("Options"), 1260.f);
	UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this);
	if (!Save)
	{
		return;
	}
	TWeakObjectPtr<UFixHimSaveSubsystem> WeakSave(Save);

	auto AddRow = [&](const FString &Label, UWidget *Control, UTextBlock *ValueText) {
		UHorizontalBox *Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		UTextBlock *L = MakeText(WidgetTree, Label, 20, Plum, TEXT("Semibold"));
		L->SetAutoWrapText(true);
		USizeBox *LabelBox = WidgetTree->ConstructWidget<USizeBox>();
		LabelBox->SetWidthOverride(280.f * FixHimDesign::TextScale());
		LabelBox->AddChild(L);
		Row->AddChildToHorizontalBox(LabelBox)->SetVerticalAlignment(VAlign_Center);
		UHorizontalBoxSlot *CSlot = Row->AddChildToHorizontalBox(Control);
		CSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		CSlot->SetVerticalAlignment(VAlign_Center);
		if (ValueText)
		{
			USizeBox *VB = WidgetTree->ConstructWidget<USizeBox>();
			VB->SetWidthOverride(100.f * FixHimDesign::TextScale());
			VB->AddChild(ValueText);
			ValueText->SetJustification(ETextJustify::Right);
			ValueText->SetColorAndOpacity(FSlateColor(Plum));
			ValueText->SetFont(Font(18, TEXT("Semibold")));
			Row->AddChildToHorizontalBox(VB)->SetVerticalAlignment(VAlign_Center);
		}
		auto *Pitch = WidgetTree->ConstructWidget<USizeBox>();
		Pitch->SetMinDesiredHeight(64);
		Pitch->AddChild(Row);
		Col->AddChildToVerticalBox(Pitch);
	};

	auto AddSlider = [&](const FString &Label, float Min, float Max, float Value, TFunction<void(float)> Apply,
	                     TFunction<FString(float)> Format) {
		UFixHimSlider *S = WidgetTree->ConstructWidget<UFixHimSlider>();
		S->SetMinValue(Min);
		S->SetMaxValue(Max);
		S->SetValue(Value);
		S->ApplyBigStyle(Blush, PlumSoft);
		UTextBlock *V = MakeText(WidgetTree, Format(Value), 18, PlumSoft);
		TWeakObjectPtr<UTextBlock> WeakV(V);
		S->Init([Apply, Format, WeakV](float NewValue) {
			Apply(NewValue);
			if (WeakV.IsValid())
			{
				WeakV->SetText(FText::FromString(Format(NewValue)));
			}
		});
		// The whole row height is the hit area, not just the thin bar.
		USizeBox *Hit = WidgetTree->ConstructWidget<USizeBox>();
		Hit->SetHeightOverride(UFixHimSlider::BigHitHeight);
		Hit->AddChild(S);
		if (USizeBoxSlot *HitSlot = Cast<USizeBoxSlot>(S->Slot))
		{
			HitSlot->SetVerticalAlignment(VAlign_Fill);
			HitSlot->SetHorizontalAlignment(HAlign_Fill);
		}
		AddRow(Label, Hit, V);
	};

	auto AddCheck = [&](const FString &Label, bool bValue, TFunction<void(bool)> Apply) {
		UFixHimCheckBox *C = WidgetTree->ConstructWidget<UFixHimCheckBox>();
		C->SetIsChecked(bValue);
		C->Init(MoveTemp(Apply));
		auto *Hit = WidgetTree->ConstructWidget<USizeBox>();
		Hit->SetHeightOverride(48);
		Hit->AddChild(C);
		CastChecked<USizeBoxSlot>(C->Slot)->SetHorizontalAlignment(HAlign_Left);
		AddRow(Label, Hit, nullptr);
	};

	auto Percent = [](float V) { return FString::Printf(TEXT("%d%%"), FMath::RoundToInt(V * 100.f)); };
	auto Times = [](float V) { return FString::Printf(TEXT("%.1fx"), V); };

	AddSlider(
	    TEXT("Master volume"), 0.f, 1.f, Save->Options().MasterVolume,
	    [WeakSave](float V) {
		    if (WeakSave.IsValid())
		    {
			    WeakSave->Options().MasterVolume = V;
			    WeakSave->ApplyOptions();
		    }
	    },
	    Percent);
	AddSlider(
	    TEXT("Music volume"), 0.f, 1.f, Save->Options().MusicVolume,
	    [WeakSave](float V) {
		    if (WeakSave.IsValid())
		    {
			    WeakSave->Options().MusicVolume = V;
			    WeakSave->ApplyOptions();
		    }
	    },
	    Percent);
	AddSlider(
	    TEXT("Mouse sensitivity"), 0.25f, 6.f, Save->Options().MouseSensitivity,
	    [WeakSave](float V) {
		    if (WeakSave.IsValid())
		    {
			    WeakSave->Options().MouseSensitivity = V;
		    }
	    },
	    Times);
	AddSlider(
	    TEXT("Text speed"), 0.25f, 4.f, Save->Options().TextSpeed,
	    [WeakSave](float V) {
		    if (WeakSave.IsValid())
		    {
			    WeakSave->Options().TextSpeed = V;
		    }
	    },
	    [](float V) { return V >= 3.95f ? FString(TEXT("Instant")) : FString::Printf(TEXT("%.1fx"), V); });
	AddCheck(TEXT("Invert look Y"), Save->Options().bInvertY, [WeakSave](bool b) {
		if (WeakSave.IsValid())
		{
			WeakSave->Options().bInvertY = b;
		}
	});
	AddCheck(TEXT("Reduced motion"), Save->Options().bReducedMotion, [WeakSave](bool b) {
		if (WeakSave.IsValid())
			WeakSave->Options().bReducedMotion = b;
	});
	AddSlider(
	    TEXT("UI text size"), 1.f, 1.35f, Save->Options().UITextScale,
	    [WeakSave](float V) {
		    if (WeakSave.IsValid())
			    WeakSave->Options().UITextScale = V;
	    },
	    Percent);
	UTextBlock *ScaleHint = MakeText(WidgetTree, TEXT("Text size applies when a screen is next opened."), 16, PlumSoft);
	Col->AddChildToVerticalBox(ScaleHint)->SetPadding(FMargin(0, 8));
	AddCheck(TEXT("Fullscreen"), Save->Options().bFullscreen, [WeakSave](bool b) {
		if (WeakSave.IsValid())
		{
			WeakSave->Options().bFullscreen = b;
			WeakSave->ApplyOptions();
		}
	});

	TWeakObjectPtr<UFixHimOptionsWidget> Self(this);
	USizeBox *Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetMinDesiredHeight(72.f);
	Box->AddChild(UFixHimButton::Make(
	    WidgetTree, TEXT("Back"),
	    [Self, WeakSave]() {
		    if (WeakSave.IsValid())
		    {
			    WeakSave->SaveOptions();
		    }
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->CloseSubMenu();
		    }
	    },
	    24, false));
	CardActions->AddChildToVerticalBox(Box);
}

// ---------------------------------------------------------------------------
// Credits

bool UFixHimCreditsWidget::HandleClickOutside()
{
	if (AFixHimPlayerController *PC = GetFixHimPC())
	{
		PC->CloseSubMenu();
		return true;
	}
	return false;
}

void UFixHimCreditsWidget::BuildUI()
{
	UVerticalBox *Col = MakeCardScreen(TEXT("Credits"), 880.f);
	auto Line = [&](const FString &Text, int32 Size, const FLinearColor &Color, const TCHAR *Face, float Bottom) {
		UTextBlock *T = MakeText(WidgetTree, Text, Size, Color, Face);
		T->SetJustification(ETextJustify::Center);
		T->SetAutoWrapText(true);
		Col->AddChildToVerticalBox(T)->SetPadding(FMargin(0.f, 0.f, 0.f, Bottom));
	};
	Line(TEXT("I CAN FIX HIM"), 26, Plum, TEXT("Bold"), 4.f);
	Line(TEXT("Made for AI Game Jam 2026"), 18, PlumSoft, TEXT("Italic"), 18.f);
	Line(TEXT("Created by"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("Kirsten Sugar, David Wallin and Michael Consoli"), 22, Plum, TEXT("Bold"), 12.f);
	Line(TEXT("Code, dialogue & puns (sorry)"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("Made with Claude by Anthropic"), 20, Plum, TEXT("Regular"), 12.f);
	Line(TEXT("Built with"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("Unreal Engine 5.8  -  Mannequins from the UE templates"), 18, Plum, TEXT("Regular"), 22.f);
	Line(TEXT("No houses were harmed. Several were flirted with."), 14, PlumSoft, TEXT("Italic"), 0.f);

	TWeakObjectPtr<UFixHimCreditsWidget> Self(this);
	USizeBox *Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetMinDesiredHeight(72.f);
	Box->AddChild(UFixHimButton::Make(
	    WidgetTree, TEXT("Back"),
	    [Self]() {
		    if (Self.IsValid() && Self->GetFixHimPC())
		    {
			    Self->GetFixHimPC()->CloseSubMenu();
		    }
	    },
	    24, false));
	CardActions->AddChildToVerticalBox(Box);
}
