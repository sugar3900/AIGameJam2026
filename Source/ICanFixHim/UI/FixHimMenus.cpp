// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimMenus.h"
#include "Player/FixHimPlayerController.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/EditableTextBox.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/Spacer.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

using namespace FixHimUI;

// ---------------------------------------------------------------------------
// Title

void UFixHimTitleWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	// Soft plum panel down the left so the apartment stays visible behind the menu.
	USizeBox* PanelSize = WidgetTree->ConstructWidget<USizeBox>();
	PanelSize->SetWidthOverride(700.f);
	UOverlaySlot* PanelSlot = Root->AddChildToOverlay(PanelSize);
	PanelSlot->SetHorizontalAlignment(HAlign_Left);
	PanelSlot->SetVerticalAlignment(VAlign_Fill);

	UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
	Panel->SetBrushColor(FLinearColor(Plum.R, Plum.G, Plum.B, 0.78f));
	Panel->SetPadding(FMargin(80.f, 70.f, 60.f, 50.f));
	PanelSize->AddChild(Panel);

	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	Panel->SetContent(Col);

	UVerticalBox* TitleCol = WidgetTree->ConstructWidget<UVerticalBox>();
	TitleBlock = TitleCol;
	Col->AddChildToVerticalBox(TitleCol);

	UTextBlock* Small = MakeText(WidgetTree, TEXT("I CAN"), 40, Blush, TEXT("Bold"));
	TitleCol->AddChildToVerticalBox(Small);
	UTextBlock* Big = MakeText(WidgetTree, TEXT("FIX HIM"), 104, Pink, TEXT("Bold"));
	Big->SetShadowOffset(FVector2D(5.f, 5.f));
	Big->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.55f));
	TitleCol->AddChildToVerticalBox(Big)->SetPadding(FMargin(0.f, -22.f, 0.f, 0.f));
	UTextBlock* Tag = MakeText(WidgetTree, TEXT("a home renovation romance"), 24, Cream, TEXT("Italic"));
	TitleCol->AddChildToVerticalBox(Tag)->SetPadding(FMargin(4.f, 0.f, 0.f, 0.f));

	UVerticalBoxSlot* SpacerSlot = Col->AddChildToVerticalBox(WidgetTree->ConstructWidget<USpacer>());
	SpacerSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	TWeakObjectPtr<UFixHimTitleWidget> Self(this);
	auto AddButton = [&](const FString& Label, TFunction<void()> Fn, bool bPrimary) -> UFixHimButton*
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetWidthOverride(340.f);
		Box->SetHeightOverride(62.f);
		UFixHimButton* B = UFixHimButton::Make(WidgetTree, Label, MoveTemp(Fn), 24, bPrimary);
		Box->AddChild(B);
		Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 14.f));
		return B;
	};

	AddButton(TEXT("New Game"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->StartNewGame(); } }, true);
	ContinueButton = AddButton(TEXT("Continue"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->ContinueGame(); } }, true);
	AddButton(TEXT("Options"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->OpenOptions(); } }, false);
	AddButton(TEXT("Credits"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->OpenCredits(); } }, false);
	AddButton(TEXT("Exit"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->QuitToDesktop(); } }, false);

	UTextBlock* Footer = MakeText(WidgetTree, TEXT("AI Game Jam 2026  -  prototype build"), 14, Blush.CopyWithNewOpacity(0.7f));
	Col->AddChildToVerticalBox(Footer)->SetPadding(FMargin(0.f, 24.f, 0.f, 0.f));

	RefreshContinue();
}

void UFixHimTitleWidget::RefreshContinue()
{
	if (ContinueButton)
	{
		const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
		ContinueButton->SetIsEnabled(Save && Save->HasSaveFile());
	}
}

void UFixHimTitleWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;
	if (TitleBlock)
	{
		// A little lovesick wobble.
		FWidgetTransform T;
		T.Angle = FMath::Sin(Age * 1.3f) * 1.2f;
		T.Scale = FVector2D(1.f + 0.015f * FMath::Sin(Age * 2.1f));
		TitleBlock->SetRenderTransform(T);
	}
}

// ---------------------------------------------------------------------------
// Name entry

void UFixHimNameEntryWidget::BuildUI()
{
	UVerticalBox* Col = MakeCardScreen(TEXT("Welcome home"), 520.f);
	TWeakObjectPtr<UFixHimNameEntryWidget> Self(this);

	UTextBlock* Prompt = MakeText(WidgetTree, TEXT("You just bought a condemned house on Heartbreak Lane. What's your name, homeowner?"), 20, Plum);
	Prompt->SetJustification(ETextJustify::Center);
	Prompt->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(Prompt)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));

	NameBox = WidgetTree->ConstructWidget<UEditableTextBox>();
	NameBox->SetHintText(FText::FromString(TEXT("Your name")));
	FEditableTextBoxStyle Style = NameBox->WidgetStyle;
	Style.SetBackgroundImageNormal(Rounded(FLinearColor::White, 14.f, Pink, 2.f));
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

	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetHeightOverride(58.f);
	MoveInButton = UFixHimButton::Make(WidgetTree, TEXT("Move in"), [Self]() { if (Self.IsValid()) { Self->Submit(); } }, 22, true);
	// Greyed out (not just faded pink) while the name is empty.
	FButtonStyle BStyle = MoveInButton->GetStyle();
	BStyle.SetDisabled(Rounded(FLinearColor(0.72f, 0.7f, 0.72f), 22.f));
	MoveInButton->SetStyle(BStyle);
	MoveInButton->SetIsEnabled(false);
	Box->AddChild(MoveInButton);
	Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 10.f));

	USizeBox* BackBox = WidgetTree->ConstructWidget<USizeBox>();
	BackBox->SetHeightOverride(46.f);
	BackBox->AddChild(UFixHimButton::Make(WidgetTree, TEXT("Back"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->CancelNameEntry(); } }, 18, false));
	Col->AddChildToVerticalBox(BackBox);
}

void UFixHimNameEntryWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (NameBox)
	{
		NameBox->SetKeyboardFocus();
	}
}

FString UFixHimNameEntryWidget::CurrentName() const
{
	return NameBox ? NameBox->GetText().ToString().TrimStartAndEnd() : FString();
}

void UFixHimNameEntryWidget::HandleTextChanged(const FText& Text)
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

void UFixHimNameEntryWidget::HandleTextCommitted(const FText& Text, ETextCommit::Type CommitMethod)
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
	UVerticalBox* Col = MakeCardScreen(TEXT("Paused"), 420.f);
	TWeakObjectPtr<UFixHimPauseWidget> Self(this);
	auto Add = [&](const FString& Label, TFunction<void()> Fn, bool bPrimary)
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetHeightOverride(58.f);
		Box->AddChild(UFixHimButton::Make(WidgetTree, Label, MoveTemp(Fn), 22, bPrimary));
		Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
	};
	Add(TEXT("Resume"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->SetPaused(false); } }, true);
	Add(TEXT("Options"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->OpenOptions(); } }, false);
	Add(TEXT("Save & Exit"),[Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->ReturnToMainMenu(); } }, false);

	UTextBlock* Hint = MakeText(WidgetTree, TEXT("Progress saves when you leave through the front door or Save & Exit."), 14, PlumSoft, TEXT("Italic"));
	Hint->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(Hint)->SetPadding(FMargin(0.f, 6.f, 0.f, 0.f));
}

// ---------------------------------------------------------------------------
// Door prompt

void UFixHimDoorPromptWidget::BuildUI()
{
	UVerticalBox* Col = MakeCardScreen(TEXT("End the day?"), 460.f);
	TWeakObjectPtr<UFixHimDoorPromptWidget> Self(this);

	BodyText = MakeText(WidgetTree, TEXT("The day ends and a week will pass."), 18, PlumSoft);
	BodyText->SetJustification(ETextJustify::Center);
	BodyText->SetAutoWrapText(true);
	Col->AddChildToVerticalBox(BodyText)->SetPadding(FMargin(0.f, 0.f, 0.f, 18.f));

	auto Add = [&](const FString& Label, TFunction<void()> Fn, bool bPrimary)
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetHeightOverride(58.f);
		UFixHimButton* Button = UFixHimButton::Make(WidgetTree, Label, MoveTemp(Fn), 22, bPrimary);
		if (bPrimary)
		{
			EndDayButton = Button;
		}
		Box->AddChild(Button);
		Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
	};
	Add(TEXT("End Day"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->ConfirmEndDay(); } }, true);
	Add(TEXT("Cancel"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->CloseDoorPrompt(); } }, false);
}

void UFixHimDoorPromptWidget::Refresh()
{
	const AFixHimPlayerController* PC = GetFixHimPC();
	const bool bAllowed = !PC || PC->CanEndDay();
	if (EndDayButton)
	{
		EndDayButton->SetIsEnabled(bAllowed);
	}
	if (BodyText)
	{
		BodyText->SetText(FText::FromString(bAllowed
			? TEXT("The day ends and a week will pass.")
			: TEXT("You feel a presence in the house... someone you still need to meet.")));
	}
}

// ---------------------------------------------------------------------------
// Options

void UFixHimOptionsWidget::BuildUI()
{
	UVerticalBox* Col = MakeCardScreen(TEXT("Options"), 560.f);
	UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	if (!Save)
	{
		return;
	}
	TWeakObjectPtr<UFixHimSaveSubsystem> WeakSave(Save);

	auto AddRow = [&](const FString& Label, UWidget* Control, UTextBlock* ValueText)
	{
		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		UTextBlock* L = MakeText(WidgetTree, Label, 20, Plum, TEXT("Bold"));
		USizeBox* LabelBox = WidgetTree->ConstructWidget<USizeBox>();
		LabelBox->SetWidthOverride(210.f);
		LabelBox->AddChild(L);
		Row->AddChildToHorizontalBox(LabelBox)->SetVerticalAlignment(VAlign_Center);
		UHorizontalBoxSlot* CSlot = Row->AddChildToHorizontalBox(Control);
		CSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		CSlot->SetVerticalAlignment(VAlign_Center);
		if (ValueText)
		{
			USizeBox* VB = WidgetTree->ConstructWidget<USizeBox>();
			VB->SetWidthOverride(70.f);
			VB->AddChild(ValueText);
			ValueText->SetJustification(ETextJustify::Right);
			Row->AddChildToHorizontalBox(VB)->SetVerticalAlignment(VAlign_Center);
		}
		Col->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.f, 6.f));
	};

	auto AddSlider = [&](const FString& Label, float Min, float Max, float Value, TFunction<void(float)> Apply, TFunction<FString(float)> Format)
	{
		UFixHimSlider* S = WidgetTree->ConstructWidget<UFixHimSlider>();
		S->SetMinValue(Min);
		S->SetMaxValue(Max);
		S->SetValue(Value);
		S->SetSliderBarColor(Blush);
		S->SetSliderHandleColor(HotPink);
		UTextBlock* V = MakeText(WidgetTree, Format(Value), 18, PlumSoft);
		TWeakObjectPtr<UTextBlock> WeakV(V);
		S->Init([Apply, Format, WeakV](float NewValue)
		{
			Apply(NewValue);
			if (WeakV.IsValid())
			{
				WeakV->SetText(FText::FromString(Format(NewValue)));
			}
		});
		AddRow(Label, S, V);
	};

	auto AddCheck = [&](const FString& Label, bool bValue, TFunction<void(bool)> Apply)
	{
		UFixHimCheckBox* C = WidgetTree->ConstructWidget<UFixHimCheckBox>();
		C->SetIsChecked(bValue);
		C->Init(MoveTemp(Apply));
		AddRow(Label, C, nullptr);
	};

	auto Percent = [](float V) { return FString::Printf(TEXT("%d%%"), FMath::RoundToInt(V * 100.f)); };
	auto Times = [](float V) { return FString::Printf(TEXT("%.1fx"), V); };

	AddSlider(TEXT("Master volume"), 0.f, 1.f, Save->Options().MasterVolume, [WeakSave](float V) { if (WeakSave.IsValid()) { WeakSave->Options().MasterVolume = V; WeakSave->ApplyOptions(); } }, Percent);
	AddSlider(TEXT("Mouse sensitivity"), 0.2f, 3.f, Save->Options().MouseSensitivity, [WeakSave](float V) { if (WeakSave.IsValid()) { WeakSave->Options().MouseSensitivity = V; } }, Times);
	AddSlider(TEXT("Text speed"), 0.25f, 4.f, Save->Options().TextSpeed, [WeakSave](float V) { if (WeakSave.IsValid()) { WeakSave->Options().TextSpeed = V; } },
		[](float V) { return V >= 3.95f ? FString(TEXT("Instant")) : FString::Printf(TEXT("%.1fx"), V); });
	AddCheck(TEXT("Invert look Y"), Save->Options().bInvertY, [WeakSave](bool b) { if (WeakSave.IsValid()) { WeakSave->Options().bInvertY = b; } });
	AddCheck(TEXT("Fullscreen"), Save->Options().bFullscreen, [WeakSave](bool b) { if (WeakSave.IsValid()) { WeakSave->Options().bFullscreen = b; WeakSave->ApplyOptions(); } });

	TWeakObjectPtr<UFixHimOptionsWidget> Self(this);
	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetHeightOverride(56.f);
	Box->AddChild(UFixHimButton::Make(WidgetTree, TEXT("Back"), [Self, WeakSave]()
	{
		if (WeakSave.IsValid())
		{
			WeakSave->SaveOptions();
		}
		if (Self.IsValid() && Self->GetFixHimPC())
		{
			Self->GetFixHimPC()->CloseSubMenu();
		}
	}, 22, true));
	Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 20.f, 0.f, 0.f));
}

// ---------------------------------------------------------------------------
// Credits

void UFixHimCreditsWidget::BuildUI()
{
	UVerticalBox* Col = MakeCardScreen(TEXT("Credits"), 600.f);
	auto Line = [&](const FString& Text, int32 Size, const FLinearColor& Color, const TCHAR* Face, float Bottom)
	{
		UTextBlock* T = MakeText(WidgetTree, Text, Size, Color, Face);
		T->SetJustification(ETextJustify::Center);
		T->SetAutoWrapText(true);
		Col->AddChildToVerticalBox(T)->SetPadding(FMargin(0.f, 0.f, 0.f, Bottom));
	};
	Line(TEXT("I CAN FIX HIM"), 26, Plum, TEXT("Bold"), 4.f);
	Line(TEXT("Made for AI Game Jam 2026"), 18, PlumSoft, TEXT("Italic"), 18.f);
	Line(TEXT("Created by"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("Kirsten Sugar, David Wallin and Michael Consoli"), 22, Plum, TEXT("Bold"), 12.f);
	Line(TEXT("Code, dialogue & puns (sorry)"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("Claude (Anthropic), directed by David"), 20, Plum, TEXT("Regular"), 12.f);
	Line(TEXT("Built with"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("Unreal Engine 5.8  -  Mannequins from the UE templates"), 18, Plum, TEXT("Regular"), 22.f);
	Line(TEXT("No houses were harmed. Several were flirted with."), 14, PlumSoft, TEXT("Italic"), 0.f);

	TWeakObjectPtr<UFixHimCreditsWidget> Self(this);
	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetHeightOverride(56.f);
	Box->AddChild(UFixHimButton::Make(WidgetTree, TEXT("Back"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->CloseSubMenu(); } }, 22, true));
	Col->AddChildToVerticalBox(Box)->SetPadding(FMargin(0.f, 20.f, 0.f, 0.f));
}
