// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimMenus.h"
#include "Player/FixHimPlayerController.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
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
	Add(TEXT("Main Menu"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->ReturnToMainMenu(); } }, false);

	UTextBlock* Hint = MakeText(WidgetTree, TEXT("Progress auto-saves after every conversation."), 14, PlumSoft, TEXT("Italic"));
	Hint->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(Hint)->SetPadding(FMargin(0.f, 6.f, 0.f, 0.f));
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
	Line(TEXT("Game design & direction"), 16, Pink, TEXT("Bold"), 0.f);
	Line(TEXT("David Wallin"), 20, Plum, TEXT("Regular"), 12.f);
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
