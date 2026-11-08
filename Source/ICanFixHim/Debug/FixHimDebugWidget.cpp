// I Can Fix Him - AI Game Jam 2026

#include "Debug/FixHimDebugWidget.h"

#if FIXHIM_DEBUG

#include "Debug/FixHimDebug.h"
#include "Player/FixHimPlayerController.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Core/FixHimSettings.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/EditableTextBox.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/ScrollBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

using namespace FixHimUI;

namespace
{
	constexpr int32 SmallFont = 13;

	FString AutoChoiceName(EFixHimAutoChoice C)
	{
		return C == EFixHimAutoChoice::First ? TEXT("first") : C == EFixHimAutoChoice::Last ? TEXT("last") : TEXT("random");
	}

	TArray<FString> SortedEndingIds(const FHunkDefinition& Def)
	{
		TArray<FString> Ids;
		Def.Endings.GetKeys(Ids);
		Ids.Sort();
		return Ids;
	}
}

void UFixHimDebugWidget::Setup(UFixHimDebugComponent* InOwner)
{
	Owner = InOwner;
}

UFixHimSaveSubsystem* UFixHimDebugWidget::Save() const
{
	return UFixHimSaveSubsystem::Get(this);
}

// ---------------------------------------------------------------------------
// Building blocks

UFixHimButton* UFixHimDebugWidget::MakeSmallButton(const FString& Label, TFunction<void()> OnClick)
{
	UFixHimButton* B = UFixHimButton::Make(WidgetTree, Label, MoveTemp(OnClick), SmallFont, false);
	FButtonStyle Style = B->GetStyle();
	Style.SetNormalPadding(FMargin(8.f, 3.f));
	Style.SetPressedPadding(FMargin(8.f, 4.f, 8.f, 2.f));
	B->SetStyle(Style);
	return B;
}

UVerticalBox* UFixHimDebugWidget::AddSection(const FString& Title)
{
	UTextBlock* Head = MakeText(WidgetTree, Title.ToUpper(), 12, Pink, TEXT("Bold"));
	Content->AddChildToVerticalBox(Head)->SetPadding(FMargin(0.f, 12.f, 0.f, 3.f));
	UVerticalBox* Box = WidgetTree->ConstructWidget<UVerticalBox>();
	Content->AddChildToVerticalBox(Box);
	return Box;
}

void UFixHimDebugWidget::AddStepper(UHorizontalBox* Row, const FString& Label, int32 Min, int32 Max, TFunction<int32()> Get, TFunction<void(int32)> Set, FSyncList& SyncList, float LabelWidth)
{
	USizeBox* LabelBox = WidgetTree->ConstructWidget<USizeBox>();
	LabelBox->SetWidthOverride(LabelWidth);
	LabelBox->AddChild(MakeText(WidgetTree, Label, SmallFont, Cream));
	Row->AddChildToHorizontalBox(LabelBox)->SetVerticalAlignment(VAlign_Center);

	UTextBlock* Value = MakeText(WidgetTree, TEXT("0"), SmallFont, Gold, TEXT("Bold"));
	Value->SetJustification(ETextJustify::Center);
	TWeakObjectPtr<UTextBlock> WeakValue(Value);
	auto Refresh = [WeakValue, Get]()
	{
		if (WeakValue.IsValid())
		{
			WeakValue->SetText(FText::AsNumber(Get()));
		}
	};
	auto Step = [Get, Set, Min, Max, Refresh](int32 Delta)
	{
		const int32 Wanted = FMath::Clamp(Get() + Delta, Min, Max);
		if (Wanted != Get())
		{
			Set(Wanted);
		}
		Refresh();
	};
	SyncList.Add(Refresh);

	UFixHimButton* Minus = MakeSmallButton(TEXT("-"), [Step]() { Step(-1); });
	UFixHimButton* Plus = MakeSmallButton(TEXT("+"), [Step]() { Step(+1); });
	USizeBox* ValueBox = WidgetTree->ConstructWidget<USizeBox>();
	ValueBox->SetWidthOverride(30.f);
	ValueBox->AddChild(Value);
	Row->AddChildToHorizontalBox(Minus)->SetVerticalAlignment(VAlign_Center);
	UHorizontalBoxSlot* ValueSlot = Row->AddChildToHorizontalBox(ValueBox);
	ValueSlot->SetVerticalAlignment(VAlign_Center);
	ValueSlot->SetPadding(FMargin(2.f, 0.f));
	Row->AddChildToHorizontalBox(Plus)->SetVerticalAlignment(VAlign_Center);
}

// ---------------------------------------------------------------------------
// Layout

void UFixHimDebugWidget::BuildUI()
{
	// Not hit-testable itself, so the game keeps getting clicks around the panel.
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	WidgetTree->RootWidget = Root;

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(400.f);
	UOverlaySlot* SizeSlot = Root->AddChildToOverlay(Size);
	SizeSlot->SetHorizontalAlignment(HAlign_Right);
	SizeSlot->SetVerticalAlignment(VAlign_Fill);
	SizeSlot->SetPadding(FMargin(0.f, 12.f, 12.f, 12.f));

	UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
	Panel->SetBrush(Rounded(FLinearColor(Plum.R, Plum.G, Plum.B, 0.93f), 18.f, Pink, 2.f));
	Panel->SetPadding(FMargin(14.f, 10.f));
	Size->AddChild(Panel);

	UVerticalBox* Frame = WidgetTree->ConstructWidget<UVerticalBox>();
	Panel->SetContent(Frame);

	UHorizontalBox* Title = WidgetTree->ConstructWidget<UHorizontalBox>();
	UTextBlock* TitleText = MakeText(WidgetTree, TEXT("DEBUG"), 18, HotPink, TEXT("Bold"));
	Title->AddChildToHorizontalBox(TitleText)->SetVerticalAlignment(VAlign_Center);
	UTextBlock* TitleHint = MakeText(WidgetTree, TEXT("  \\ / Insert to close"), 12, PlumSoft, TEXT("Italic"));
	UHorizontalBoxSlot* HintSlot = Title->AddChildToHorizontalBox(TitleHint);
	HintSlot->SetVerticalAlignment(VAlign_Center);
	HintSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	Frame->AddChildToVerticalBox(Title)->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));

	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Scroll->SetScrollBarVisibility(ESlateVisibility::Visible);
	UVerticalBoxSlot* ScrollSlot = Frame->AddChildToVerticalBox(Scroll);
	ScrollSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	Content = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(Content);

	UFixHimDebugComponent* Comp = Owner.Get();
	const int32 NumWeeks = UFixHimSettings::Get()->NumWeeks;
	TWeakObjectPtr<UFixHimDebugWidget> Self(this);
	auto WithPC = [Self](TFunction<void(AFixHimPlayerController*)> Fn)
	{
		return [Self, Fn]()
		{
			if (Self.IsValid() && Self->GetFixHimPC())
			{
				Fn(Self->GetFixHimPC());
			}
		};
	};

	// ---- Days -------------------------------------------------------------
	{
		UVerticalBox* Box = AddSection(TEXT("Day"));
		WeekText = MakeText(WidgetTree, TEXT(""), 14, Cream, TEXT("Bold"));
		Box->AddChildToVerticalBox(WeekText)->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));

		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		UFixHimButton* Next = MakeSmallButton(TEXT("Next day (+1 week)"), WithPC([Self](AFixHimPlayerController* PC)
		{
			if (UFixHimSaveSubsystem* S = Self->Save())
			{
				PC->DebugSetWeek(S->Data().Week + 1);
				Self->TargetWeek = FMath::Clamp(S->Data().Week + 1, 1, UFixHimSettings::Get()->NumWeeks + 1);
				Self->SyncAll();
			}
		}));
		Row->AddChildToHorizontalBox(Next)->SetPadding(FMargin(0.f, 0.f, 6.f, 0.f));
		UFixHimButton* Door = MakeSmallButton(TEXT("Teleport to door"), WithPC([](AFixHimPlayerController* PC) { PC->DebugTeleportToDoor(); }));
		Row->AddChildToHorizontalBox(Door);
		Box->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));

		UHorizontalBox* WeekRow = WidgetTree->ConstructWidget<UHorizontalBox>();
		AddStepper(WeekRow, TEXT("Week"), 1, NumWeeks + 1,
			[Self]() { return Self.IsValid() ? Self->TargetWeek : 1; },
			[Self](int32 V) { if (Self.IsValid()) { Self->TargetWeek = V; } },
			Syncs, 40.f);
		UFixHimButton* Go = MakeSmallButton(TEXT("Set week"), WithPC([Self](AFixHimPlayerController* PC)
		{
			PC->DebugSetWeek(Self->TargetWeek);
			Self->SyncAll();
		}));
		WeekRow->AddChildToHorizontalBox(Go)->SetPadding(FMargin(8.f, 0.f, 0.f, 0.f));
		Box->AddChildToVerticalBox(WeekRow);
		Box->AddChildToVerticalBox(MakeText(WidgetTree, FString::Printf(TEXT("Week %d = inspection day / finale."), NumWeeks + 1), 11, PlumSoft, TEXT("Italic")));
	}

	// ---- Auto-play ----------------------------------------------------------
	{
		UVerticalBox* Box = AddSection(TEXT("Auto-play"));
		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		UFixHimCheckBox* Check = WidgetTree->ConstructWidget<UFixHimCheckBox>();
		Check->SetIsChecked(Comp && Comp->bAutoPlay);
		TWeakObjectPtr<UFixHimDebugComponent> WeakComp(Comp);
		Check->Init([WeakComp](bool b) { if (WeakComp.IsValid()) { WeakComp->bAutoPlay = b; } });
		Row->AddChildToHorizontalBox(Check)->SetVerticalAlignment(VAlign_Center);
		UHorizontalBoxSlot* LabelSlot = Row->AddChildToHorizontalBox(MakeText(WidgetTree, TEXT("Auto-skip dialogue"), 14, Cream, TEXT("Bold")));
		LabelSlot->SetVerticalAlignment(VAlign_Center);
		LabelSlot->SetPadding(FMargin(6.f, 0.f));
		Box->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));
		Box->AddChildToVerticalBox(MakeText(WidgetTree, TEXT("Plays out conversations, podcast captions, splash cards and cutscenes. Never clicks [topic] links."), 11, PlumSoft, TEXT("Italic")))->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));

		UHorizontalBox* SpeedRow = WidgetTree->ConstructWidget<UHorizontalBox>();
		USizeBox* SpeedLabel = WidgetTree->ConstructWidget<USizeBox>();
		SpeedLabel->SetWidthOverride(86.f);
		UTextBlock* SpeedValue = MakeText(WidgetTree, TEXT(""), SmallFont, Gold, TEXT("Bold"));
		TWeakObjectPtr<UTextBlock> WeakSpeedValue(SpeedValue);
		SpeedLabel->AddChild(MakeText(WidgetTree, TEXT("Step delay"), SmallFont, Cream));
		SpeedRow->AddChildToHorizontalBox(SpeedLabel)->SetVerticalAlignment(VAlign_Center);
		UFixHimSlider* Slider = WidgetTree->ConstructWidget<UFixHimSlider>();
		Slider->SetMinValue(0.05f);
		Slider->SetMaxValue(1.f);
		Slider->SetValue(Comp ? Comp->StepDelay : 0.2f);
		Slider->SetSliderBarColor(Blush);
		Slider->SetSliderHandleColor(HotPink);
		auto SetSpeedText = [WeakSpeedValue](float V)
		{
			if (WeakSpeedValue.IsValid())
			{
				WeakSpeedValue->SetText(FText::FromString(FString::Printf(TEXT("%.2fs"), V)));
			}
		};
		SetSpeedText(Comp ? Comp->StepDelay : 0.2f);
		Slider->Init([WeakComp, SetSpeedText](float V)
		{
			if (WeakComp.IsValid())
			{
				WeakComp->StepDelay = V;
			}
			SetSpeedText(V);
		});
		UHorizontalBoxSlot* SliderSlot = SpeedRow->AddChildToHorizontalBox(Slider);
		SliderSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		SliderSlot->SetVerticalAlignment(VAlign_Center);
		USizeBox* SpeedValueBox = WidgetTree->ConstructWidget<USizeBox>();
		SpeedValueBox->SetWidthOverride(48.f);
		SpeedValueBox->AddChild(SpeedValue);
		SpeedValue->SetJustification(ETextJustify::Right);
		SpeedRow->AddChildToHorizontalBox(SpeedValueBox)->SetVerticalAlignment(VAlign_Center);
		Box->AddChildToVerticalBox(SpeedRow)->SetPadding(FMargin(0.f, 0.f, 0.f, 4.f));

		UHorizontalBox* PolicyRow = WidgetTree->ConstructWidget<UHorizontalBox>();
		USizeBox* PolicyLabel = WidgetTree->ConstructWidget<USizeBox>();
		PolicyLabel->SetWidthOverride(86.f);
		PolicyLabel->AddChild(MakeText(WidgetTree, TEXT("Choices"), SmallFont, Cream));
		PolicyRow->AddChildToHorizontalBox(PolicyLabel)->SetVerticalAlignment(VAlign_Center);
		UFixHimButton* Policy = MakeSmallButton(AutoChoiceName(Comp ? Comp->ChoicePolicy : EFixHimAutoChoice::First), nullptr);
		TWeakObjectPtr<UFixHimButton> WeakPolicy(Policy);
		Policy->Init([WeakComp, WeakPolicy]()
		{
			if (WeakComp.IsValid() && WeakPolicy.IsValid())
			{
				// first -> random -> last -> first
				WeakComp->ChoicePolicy = WeakComp->ChoicePolicy == EFixHimAutoChoice::First ? EFixHimAutoChoice::Random
					: WeakComp->ChoicePolicy == EFixHimAutoChoice::Random ? EFixHimAutoChoice::Last : EFixHimAutoChoice::First;
				WeakPolicy->Label->SetText(FText::FromString(AutoChoiceName(WeakComp->ChoicePolicy)));
			}
		});
		PolicyRow->AddChildToHorizontalBox(Policy);
		Box->AddChildToVerticalBox(PolicyRow);
	}

	// ---- Player & flags -----------------------------------------------------
	{
		UVerticalBox* Box = AddSection(TEXT("Player"));
		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		USizeBox* NameLabel = WidgetTree->ConstructWidget<USizeBox>();
		NameLabel->SetWidthOverride(62.f);
		NameLabel->AddChild(MakeText(WidgetTree, TEXT("Name"), SmallFont, Cream));
		Row->AddChildToHorizontalBox(NameLabel)->SetVerticalAlignment(VAlign_Center);
		NameBox = WidgetTree->ConstructWidget<UEditableTextBox>();
		FEditableTextBoxStyle Style = NameBox->WidgetStyle;
		Style.SetBackgroundImageNormal(Rounded(FLinearColor::White, 8.f, Pink, 1.f));
		Style.SetBackgroundImageHovered(Rounded(FLinearColor::White, 8.f, HotPink, 1.f));
		Style.SetBackgroundImageFocused(Rounded(FLinearColor::White, 8.f, HotPink, 2.f));
		Style.SetPadding(FMargin(8.f, 3.f));
		Style.SetFont(Font(SmallFont, TEXT("Bold")));
		Style.SetForegroundColor(FSlateColor(Plum));
		NameBox->WidgetStyle = Style;
		Row->AddChildToHorizontalBox(NameBox)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		Box->AddChildToVerticalBox(Row);

		UVerticalBox* FlagsBox = AddSection(TEXT("Flags"));
		FlagList = WidgetTree->ConstructWidget<UVerticalBox>();
		FlagsBox->AddChildToVerticalBox(FlagList);

		// Add / set a flag by name.
		FEditableTextBoxStyle FlagStyle = Style;
		UHorizontalBox* AddRow = WidgetTree->ConstructWidget<UHorizontalBox>();
		FlagNameBox = WidgetTree->ConstructWidget<UEditableTextBox>();
		FlagNameBox->WidgetStyle = FlagStyle;
		FlagNameBox->SetHintText(FText::FromString(TEXT("flag name")));
		AddRow->AddChildToHorizontalBox(FlagNameBox)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		USizeBox* ValueSize = WidgetTree->ConstructWidget<USizeBox>();
		ValueSize->SetWidthOverride(46.f);
		FlagValueBox = WidgetTree->ConstructWidget<UEditableTextBox>();
		FlagValueBox->WidgetStyle = FlagStyle;
		FlagValueBox->SetText(FText::FromString(TEXT("1")));
		ValueSize->AddChild(FlagValueBox);
		AddRow->AddChildToHorizontalBox(ValueSize)->SetPadding(FMargin(4.f, 0.f));
		UFixHimButton* AddFlag = MakeSmallButton(TEXT("Add / set"), [Self]()
		{
			UFixHimSaveSubsystem* S = Self.IsValid() ? Self->Save() : nullptr;
			if (!S || !Self->FlagNameBox)
			{
				return;
			}
			const FString Name = Self->FlagNameBox->GetText().ToString().TrimStartAndEnd();
			if (!Name.IsEmpty())
			{
				S->Data().Flags.FindOrAdd(Name) = FCString::Atoi(*Self->FlagValueBox->GetText().ToString());
				Self->FlagNameBox->SetText(FText::GetEmpty());
				Self->SyncAll();
			}
		});
		AddRow->AddChildToHorizontalBox(AddFlag);
		FlagsBox->AddChildToVerticalBox(AddRow)->SetPadding(FMargin(0.f, 4.f, 0.f, 0.f));
	}

	// ---- Characters ---------------------------------------------------------
	{
		UVerticalBox* Box = AddSection(TEXT("Characters"));
		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		UFixHimButton* FixAll = MakeSmallButton(TEXT("Fix everything"), [Self]()
		{
			UFixHimSaveSubsystem* S = Self.IsValid() ? Self->Save() : nullptr;
			const UFixHimDialogueSubsystem* D = S ? UFixHimDialogueSubsystem::Get(Self.Get()) : nullptr;
			if (!S || !D)
			{
				return;
			}
			for (const auto& Pair : D->GetAllHunks())
			{
				if (Pair.Value.IsHunk())
				{
					FHunkProgress& P = S->Hunk(Pair.Key);
					P.bMet = true;
					P.bFixed = true;
					P.Visits = FMath::Max(P.Visits, 1);
					if (P.Ending.IsEmpty())
					{
						P.Ending = D->ResolveAutoEnding(Pair.Key);
					}
				}
			}
			if (Self->GetFixHimPC())
			{
				Self->GetFixHimPC()->DebugRefreshWorld();
			}
			Self->SyncAll();
		});
		Row->AddChildToHorizontalBox(FixAll)->SetPadding(FMargin(0.f, 0.f, 6.f, 0.f));
		UFixHimButton* Reset = MakeSmallButton(TEXT("Reset all (and flags)"), [Self]()
		{
			UFixHimSaveSubsystem* S = Self.IsValid() ? Self->Save() : nullptr;
			if (!S)
			{
				return;
			}
			S->Data().Hunks.Empty();
			S->Data().Flags.Empty();
			if (Self->GetFixHimPC())
			{
				Self->GetFixHimPC()->DebugRefreshWorld();
			}
			Self->SyncAll();
		});
		Row->AddChildToHorizontalBox(Reset);
		Box->AddChildToVerticalBox(Row);

		if (const UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
		{
			TArray<FString> Ids;
			for (const auto& Pair : D->GetAllHunks())
			{
				if (Pair.Value.IsHunk())
				{
					Ids.Add(Pair.Key);
				}
			}
			Ids.Sort();
			for (const FString& Id : Ids)
			{
				BuildHunkSection(Id);
			}
		}
	}

	SyncAll();
}

void UFixHimDebugWidget::BuildHunkSection(const FString& HunkId)
{
	const UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this);
	const FHunkDefinition* Def = D ? D->FindHunk(HunkId) : nullptr;
	if (!Def)
	{
		return;
	}
	TWeakObjectPtr<UFixHimDebugWidget> Self(this);

	UBorder* Card = WidgetTree->ConstructWidget<UBorder>();
	Card->SetBrush(Rounded(FLinearColor(1.f, 1.f, 1.f, 0.07f), 10.f));
	Card->SetPadding(FMargin(8.f, 6.f));
	Content->AddChildToVerticalBox(Card)->SetPadding(FMargin(0.f, 6.f, 0.f, 0.f));
	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	Card->SetContent(Col);

	Col->AddChildToVerticalBox(MakeText(WidgetTree, FString::Printf(TEXT("%s  (%s)"), *Def->Name, *HunkId), 14, Blush, TEXT("Bold")))->SetPadding(FMargin(0.f, 0.f, 0.f, 3.f));

	auto Progress = [Self, HunkId]() -> FHunkProgress*
	{
		UFixHimSaveSubsystem* S = Self.IsValid() ? Self->Save() : nullptr;
		return S ? &S->Hunk(HunkId) : nullptr;
	};
	auto StatGet = [Self, HunkId](ERelationshipAxis Axis) -> int32
	{
		const UFixHimSaveSubsystem* S = Self.IsValid() ? Self->Save() : nullptr;
		const FHunkProgress* P = S ? S->FindHunk(HunkId) : nullptr;
		if (!P)
		{
			return 0;
		}
		return Axis == ERelationshipAxis::Romance ? P->Romance : Axis == ERelationshipAxis::Friendship ? P->Friendship : P->Friction;
	};
	// AddStat keeps the 0..FixHimStatMax clamp and fires OnStatChanged like the dialogue does.
	auto StatSet = [Self, HunkId, StatGet](ERelationshipAxis Axis, int32 Value)
	{
		if (UFixHimSaveSubsystem* S = Self.IsValid() ? Self->Save() : nullptr)
		{
			S->AddStat(HunkId, Axis, Value - StatGet(Axis));
		}
	};

	UHorizontalBox* Row1 = WidgetTree->ConstructWidget<UHorizontalBox>();
	AddStepper(Row1, TEXT("Romance"), 0, FixHimStatMax, [StatGet]() { return StatGet(ERelationshipAxis::Romance); }, [StatSet](int32 V) { StatSet(ERelationshipAxis::Romance, V); }, Syncs, 56.f);
	Col->AddChildToVerticalBox(Row1)->SetPadding(FMargin(0.f, 1.f));
	UHorizontalBox* Row2 = WidgetTree->ConstructWidget<UHorizontalBox>();
	AddStepper(Row2, TEXT("Friends"), 0, FixHimStatMax, [StatGet]() { return StatGet(ERelationshipAxis::Friendship); }, [StatSet](int32 V) { StatSet(ERelationshipAxis::Friendship, V); }, Syncs, 56.f);
	Col->AddChildToVerticalBox(Row2)->SetPadding(FMargin(0.f, 1.f));
	UHorizontalBox* Row3 = WidgetTree->ConstructWidget<UHorizontalBox>();
	AddStepper(Row3, TEXT("Friction"), 0, FixHimStatMax, [StatGet]() { return StatGet(ERelationshipAxis::Friction); }, [StatSet](int32 V) { StatSet(ERelationshipAxis::Friction, V); }, Syncs, 56.f);
	Col->AddChildToVerticalBox(Row3)->SetPadding(FMargin(0.f, 1.f));
	UHorizontalBox* Row4 = WidgetTree->ConstructWidget<UHorizontalBox>();
	AddStepper(Row4, TEXT("Visits"), 0, 99, [Progress]() { const FHunkProgress* P = Progress(); return P ? P->Visits : 0; }, [Progress](int32 V) { if (FHunkProgress* P = Progress()) { P->Visits = V; } }, Syncs, 56.f);
	Col->AddChildToVerticalBox(Row4)->SetPadding(FMargin(0.f, 1.f));

	// Met / Fixed
	UHorizontalBox* Flags = WidgetTree->ConstructWidget<UHorizontalBox>();
	auto AddCheck = [&](const FString& Label, TFunction<bool()> Get, TFunction<void(bool)> Set)
	{
		UFixHimCheckBox* Check = WidgetTree->ConstructWidget<UFixHimCheckBox>();
		Check->Init([Self, Set](bool b)
		{
			Set(b);
			if (Self.IsValid() && Self->GetFixHimPC())
			{
				Self->GetFixHimPC()->DebugRefreshWorld();
			}
		});
		Flags->AddChildToHorizontalBox(Check)->SetVerticalAlignment(VAlign_Center);
		UHorizontalBoxSlot* L = Flags->AddChildToHorizontalBox(MakeText(WidgetTree, Label, SmallFont, Cream));
		L->SetVerticalAlignment(VAlign_Center);
		L->SetPadding(FMargin(4.f, 0.f, 14.f, 0.f));
		TWeakObjectPtr<UFixHimCheckBox> WeakCheck(Check);
		Syncs.Add([WeakCheck, Get]() { if (WeakCheck.IsValid()) { WeakCheck->SetIsChecked(Get()); } });
	};
	AddCheck(TEXT("Met"), [Progress]() { const FHunkProgress* P = Progress(); return P && P->bMet; }, [Progress](bool b) { if (FHunkProgress* P = Progress()) { P->bMet = b; } });
	AddCheck(TEXT("Fixed"), [Progress]() { const FHunkProgress* P = Progress(); return P && P->bFixed; }, [Progress](bool b) { if (FHunkProgress* P = Progress()) { P->bFixed = b; } });

	// Ending: none, or one of this hunk's endings (click cycles).
	UFixHimButton* EndingButton = MakeSmallButton(TEXT("ending: none"), nullptr);
	TWeakObjectPtr<UFixHimButton> WeakEnding(EndingButton);
	auto EndingLabel = [Progress]()
	{
		const FHunkProgress* P = Progress();
		return FString::Printf(TEXT("ending: %s"), P && !P->Ending.IsEmpty() ? *P->Ending : TEXT("none"));
	};
	EndingButton->Init([Self, HunkId, Progress, WeakEnding, EndingLabel]()
	{
		const UFixHimDialogueSubsystem* Dlg = UFixHimDialogueSubsystem::Get(Self.Get());
		const FHunkDefinition* Definition = Dlg ? Dlg->FindHunk(HunkId) : nullptr;
		FHunkProgress* P = Progress();
		if (!Definition || !P)
		{
			return;
		}
		TArray<FString> Options = { FString() };
		Options.Append(SortedEndingIds(*Definition));
		const int32 Current = Options.IndexOfByKey(P->Ending);
		P->Ending = Options[(Current + 1) % Options.Num()];
		if (WeakEnding.IsValid())
		{
			WeakEnding->Label->SetText(FText::FromString(EndingLabel()));
		}
		if (Self->GetFixHimPC())
		{
			Self->GetFixHimPC()->DebugRefreshWorld();
		}
	});
	Syncs.Add([WeakEnding, EndingLabel]() { if (WeakEnding.IsValid()) { WeakEnding->Label->SetText(FText::FromString(EndingLabel())); } });
	Flags->AddChildToHorizontalBox(EndingButton)->SetVerticalAlignment(VAlign_Center);
	Col->AddChildToVerticalBox(Flags)->SetPadding(FMargin(0.f, 3.f, 0.f, 0.f));
}

void UFixHimDebugWidget::BuildFlagList()
{
	FlagList->ClearChildren();
	FlagSyncs.Reset();
	const UFixHimSaveSubsystem* S = Save();
	if (!S)
	{
		return;
	}
	TWeakObjectPtr<UFixHimDebugWidget> Self(this);
	TArray<FString> Names;
	S->Data().Flags.GetKeys(Names);
	Names.Sort();
	for (const FString& Name : Names)
	{
		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
		UTextBlock* NameText = MakeText(WidgetTree, Name, SmallFont, Cream);
		UHorizontalBoxSlot* NameSlot = Row->AddChildToHorizontalBox(NameText);
		NameSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		NameSlot->SetVerticalAlignment(VAlign_Center);
		AddStepper(Row, FString(), -99, 999,
			[Self, Name]() { const UFixHimSaveSubsystem* Sv = Self.IsValid() ? Self->Save() : nullptr; return Sv ? Sv->GetFlag(Name) : 0; },
			[Self, Name](int32 V) { if (UFixHimSaveSubsystem* Sv = Self.IsValid() ? Self->Save() : nullptr) { Sv->Data().Flags.FindOrAdd(Name) = V; } },
			FlagSyncs, 0.f);
		FlagList->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.f, 1.f));
	}
	if (Names.IsEmpty())
	{
		FlagList->AddChildToVerticalBox(MakeText(WidgetTree, TEXT("(no flags)"), 12, PlumSoft, TEXT("Italic")));
	}
}

// ---------------------------------------------------------------------------
// Syncing

void UFixHimDebugWidget::SyncAll()
{
	const UFixHimSaveSubsystem* S = Save();
	if (!S || !Content)
	{
		return;
	}
	// The flag list is rebuilt only when the set of flag names changes.
	TArray<FString> Names;
	S->Data().Flags.GetKeys(Names);
	Names.Sort();
	const FString Signature = FString::Join(Names, TEXT("|"));
	if (Signature != FlagSignature || !FlagList->HasAnyChildren())
	{
		FlagSignature = Signature;
		BuildFlagList();
	}

	for (const TFunction<void()>& Fn : Syncs)
	{
		Fn();
	}
	for (const TFunction<void()>& Fn : FlagSyncs)
	{
		Fn();
	}
	if (NameBox && !NameBox->HasKeyboardFocus())
	{
		const FText Name = FText::FromString(S->Data().PlayerName);
		if (!NameBox->GetText().EqualTo(Name))
		{
			NameBox->SetText(Name);
		}
	}
	if (WeekText)
	{
		const int32 NumWeeks = UFixHimSettings::Get()->NumWeeks;
		const int32 Week = S->Data().Week;
		WeekText->SetText(FText::FromString(Week > NumWeeks ? FString(TEXT("Current: inspection day")) : FString::Printf(TEXT("Current: week %d of %d"), Week, NumWeeks)));
	}
}

void UFixHimDebugWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	// The player name is edited live while its box has focus.
	if (NameBox && NameBox->HasKeyboardFocus())
	{
		if (UFixHimSaveSubsystem* S = Save())
		{
			S->Data().PlayerName = NameBox->GetText().ToString().Left(16);
		}
	}
	SyncTimer += InDeltaTime;
	if (SyncTimer >= 0.25f)
	{
		SyncTimer = 0.f;
		SyncAll();
	}
}

#endif // FIXHIM_DEBUG
