// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimDialogueWidget.h"
#include "Player/FixHimPlayerController.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "World/FixHimHunk.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Core/FixHimSettings.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/ButtonSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/ProgressBar.h"
#include "Components/SizeBox.h"
#include "Components/Spacer.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/WrapBox.h"
#include "Components/WrapBoxSlot.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"

using namespace FixHimUI;

namespace
{
	constexpr int32 MeterMax = FixHimStatMax;
	constexpr float FadeSeconds = 0.9f;
	constexpr float HoldSeconds = 2.6f;
}

void UFixHimDialogueWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	WidgetTree->RootWidget = Root;

	// ---- Bottom panel ----
	PanelSize = WidgetTree->ConstructWidget<USizeBox>();
	UOverlaySlot* PanelSlot = Root->AddChildToOverlay(PanelSize);
	PanelSlot->SetHorizontalAlignment(HAlign_Fill);
	PanelSlot->SetVerticalAlignment(VAlign_Bottom);
	PanelSlot->SetPadding(FMargin(40.f, 0.f, 40.f, 22.f));

	UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
	Panel->SetBrush(Rounded(FLinearColor(Cream.R, Cream.G, Cream.B, 0.97f), 26.f, Pink, 4.f));
	Panel->SetPadding(FMargin(22.f, 18.f, 26.f, 16.f));
	Panel->SetVisibility(ESlateVisibility::Visible);
	PanelSize->AddChild(Panel);

	UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
	Panel->SetContent(Row);

	// Portrait
	USizeBox* PortraitSize = WidgetTree->ConstructWidget<USizeBox>();
	PortraitSize->SetWidthOverride(210.f);
	PortraitSize->SetHeightOverride(210.f);
	UBorder* Frame = WidgetTree->ConstructWidget<UBorder>();
	Frame->SetBrush(Rounded(Plum, 20.f, HotPink, 4.f));
	Frame->SetPadding(FMargin(6.f));
	PortraitSize->AddChild(Frame);
	UOverlay* PortraitStack = WidgetTree->ConstructWidget<UOverlay>();
	PortraitStack->SetClipping(EWidgetClipping::ClipToBounds);
	Frame->SetContent(PortraitStack);
	Portrait = WidgetTree->ConstructWidget<UImage>();
	{
		// Overlay slots default to top-left at the image's own size; the avatar must fill the whole frame.
		UOverlaySlot* PortraitFill = PortraitStack->AddChildToOverlay(Portrait);
		PortraitFill->SetHorizontalAlignment(HAlign_Fill);
		PortraitFill->SetVerticalAlignment(VAlign_Fill);
	}

	// Player's generic silhouette: a head and shoulders on a flat backdrop.
	UOverlay* Sil = WidgetTree->ConstructWidget<UOverlay>();
	UBorder* SilBack = WidgetTree->ConstructWidget<UBorder>();
	SilBack->SetBrush(Rounded(PlumSoft, 0.f));
	UOverlaySlot* BackFill = Sil->AddChildToOverlay(SilBack);
	BackFill->SetHorizontalAlignment(HAlign_Fill);
	BackFill->SetVerticalAlignment(VAlign_Fill);
	USizeBox* Shoulders = WidgetTree->ConstructWidget<USizeBox>();
	Shoulders->SetWidthOverride(150.f);
	Shoulders->SetHeightOverride(120.f);
	UBorder* ShoulderShape = WidgetTree->ConstructWidget<UBorder>();
	ShoulderShape->SetBrush(Rounded(Plum, 60.f));
	Shoulders->AddChild(ShoulderShape);
	UOverlaySlot* ShoulderSlot = Sil->AddChildToOverlay(Shoulders);
	ShoulderSlot->SetHorizontalAlignment(HAlign_Center);
	ShoulderSlot->SetVerticalAlignment(VAlign_Bottom);
	ShoulderSlot->SetPadding(FMargin(0.f, 0.f, 0.f, -50.f));
	USizeBox* Head = WidgetTree->ConstructWidget<USizeBox>();
	Head->SetWidthOverride(70.f);
	Head->SetHeightOverride(76.f);
	UBorder* HeadShape = WidgetTree->ConstructWidget<UBorder>();
	HeadShape->SetBrush(Rounded(Plum, 36.f));
	Head->AddChild(HeadShape);
	UOverlaySlot* HeadSlot = Sil->AddChildToOverlay(Head);
	HeadSlot->SetHorizontalAlignment(HAlign_Center);
	HeadSlot->SetVerticalAlignment(VAlign_Center);
	HeadSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 36.f));
	Sil->SetVisibility(ESlateVisibility::Collapsed);
	PlayerSilhouette = Sil;
	UOverlaySlot* SilFill = PortraitStack->AddChildToOverlay(Sil);
	SilFill->SetHorizontalAlignment(HAlign_Fill);
	SilFill->SetVerticalAlignment(VAlign_Fill);
	PortraitBox = PortraitSize;
	UHorizontalBoxSlot* PortraitSlot = Row->AddChildToHorizontalBox(PortraitSize);
	PortraitSlot->SetVerticalAlignment(VAlign_Top);
	PortraitSlot->SetPadding(FMargin(0.f, 0.f, 24.f, 0.f));

	// Text column
	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	UHorizontalBoxSlot* ColSlot = Row->AddChildToHorizontalBox(Col);
	ColSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UHorizontalBox* Header = WidgetTree->ConstructWidget<UHorizontalBox>();
	Col->AddChildToVerticalBox(Header)->SetPadding(FMargin(0.f, 0.f, 0.f, 8.f));

	NamePill = WidgetTree->ConstructWidget<UBorder>();
	NamePill->SetBrush(Rounded(HotPink, 16.f));
	NamePill->SetPadding(FMargin(16.f, 4.f));
	NameText = MakeText(WidgetTree, TEXT("NAME"), 22, FLinearColor::White, TEXT("Bold"));
	NamePill->SetContent(NameText);
	Header->AddChildToHorizontalBox(NamePill)->SetVerticalAlignment(VAlign_Center);

	MaladyText = MakeText(WidgetTree, TEXT(""), 16, PlumSoft, TEXT("Italic"));
	UHorizontalBoxSlot* MalSlot = Header->AddChildToHorizontalBox(MaladyText);
	MalSlot->SetVerticalAlignment(VAlign_Center);
	MalSlot->SetPadding(FMargin(12.f, 0.f));
	MalSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	// Meters (right of header)
	UVerticalBox* Meters = WidgetTree->ConstructWidget<UVerticalBox>();
	auto AddMeter = [&](const FString& Label, const FLinearColor& Color) -> UProgressBar*
	{
		UHorizontalBox* M = WidgetTree->ConstructWidget<UHorizontalBox>();
		USizeBox* LB = WidgetTree->ConstructWidget<USizeBox>();
		LB->SetWidthOverride(86.f);
		LB->AddChild(MakeText(WidgetTree, Label, 12, PlumSoft, TEXT("Bold")));
		M->AddChildToHorizontalBox(LB)->SetVerticalAlignment(VAlign_Center);
		USizeBox* BB = WidgetTree->ConstructWidget<USizeBox>();
		BB->SetWidthOverride(120.f);
		BB->SetHeightOverride(9.f);
		UProgressBar* Bar = WidgetTree->ConstructWidget<UProgressBar>();
		FProgressBarStyle Style;
		Style.SetBackgroundImage(Rounded(Blush, 4.f));
		Style.SetFillImage(Rounded(FLinearColor::White, 4.f));
		Style.SetMarqueeImage(Rounded(FLinearColor::White, 4.f));
		Bar->SetWidgetStyle(Style);
		Bar->SetFillColorAndOpacity(Color);
		Bar->SetPercent(0.f);
		BB->AddChild(Bar);
		M->AddChildToHorizontalBox(BB)->SetVerticalAlignment(VAlign_Center);
		Meters->AddChildToVerticalBox(M)->SetPadding(FMargin(0.f, 1.f));
		return Bar;
	};
	RomanceBar = AddMeter(TEXT("ROMANCE"), HotPink);
	FriendBar = AddMeter(TEXT("FRIENDSHIP"), Mint);
	FrictionBar = AddMeter(TEXT("FRICTION"), Ember);
	Header->AddChildToHorizontalBox(Meters)->SetVerticalAlignment(VAlign_Center);
	MetersBox = Meters;

	// Line text: typewriter text while typing, then a wrap box of words so [topics] can be clicked.
	UOverlay* TextArea = WidgetTree->ConstructWidget<UOverlay>();
	Col->AddChildToVerticalBox(TextArea)->SetPadding(FMargin(4.f, 2.f, 0.f, 6.f));
	TypingText = MakeText(WidgetTree, TEXT(""), 24, Plum);
	TypingText->SetAutoWrapText(true);
	TextArea->AddChildToOverlay(TypingText)->SetHorizontalAlignment(HAlign_Fill);
	WordWrap = WidgetTree->ConstructWidget<UWrapBox>();
	WordWrap->SetInnerSlotPadding(FVector2D(0.f, 2.f));
	WordWrap->SetVisibility(ESlateVisibility::Collapsed);
	TextArea->AddChildToOverlay(WordWrap)->SetHorizontalAlignment(HAlign_Fill);

	ChoiceBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Col->AddChildToVerticalBox(ChoiceBox);

	ContinueHint = MakeText(WidgetTree, TEXT("click to continue  >"), 14, Pink, TEXT("Bold"));
	ContinueHint->SetJustification(ETextJustify::Right);
	UVerticalBoxSlot* HintSlot = Col->AddChildToVerticalBox(ContinueHint);
	HintSlot->SetHorizontalAlignment(HAlign_Right);

	// Stat floaters stack above the panel, right side.
	FloaterBox = WidgetTree->ConstructWidget<UVerticalBox>();
	FloaterBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	UOverlaySlot* FloatSlot = Root->AddChildToOverlay(FloaterBox);
	FloatSlot->SetHorizontalAlignment(HAlign_Right);
	FloatSlot->SetVerticalAlignment(VAlign_Bottom);
	FloatSlot->SetPadding(FMargin(0.f, 0.f, 70.f, 330.f));

	// Full-screen fx layers.
	FxCanvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	FxCanvas->SetVisibility(ESlateVisibility::HitTestInvisible);
	UOverlaySlot* FxSlot = Root->AddChildToOverlay(FxCanvas);
	FxSlot->SetHorizontalAlignment(HAlign_Fill);
	FxSlot->SetVerticalAlignment(VAlign_Fill);

	FadeCurtain = WidgetTree->ConstructWidget<UBorder>();
	FadeCurtain->SetBrushColor(FLinearColor::Black);
	FadeCurtain->SetHorizontalAlignment(HAlign_Center);
	FadeCurtain->SetVerticalAlignment(VAlign_Center);
	FadeText = MakeText(WidgetTree, TEXT(""), 30, Blush, TEXT("Italic"));
	FadeText->SetJustification(ETextJustify::Center);
	FadeCurtain->SetContent(FadeText);
	FadeCurtain->SetVisibility(ESlateVisibility::Collapsed);
	UOverlaySlot* FadeSlot = Root->AddChildToOverlay(FadeCurtain);
	FadeSlot->SetHorizontalAlignment(HAlign_Fill);
	FadeSlot->SetVerticalAlignment(VAlign_Fill);
}

void UFixHimDialogueWidget::ClearFx()
{
	for (FFloater& F : Floaters)
	{
		if (UWidget* W = F.Widget.Get())
		{
			W->RemoveFromParent();
		}
	}
	Floaters.Reset();
	FxPhase = EFxPhase::None;
	if (FadeCurtain)
	{
		FadeCurtain->SetVisibility(ESlateVisibility::Collapsed);
	}
}

void UFixHimDialogueWidget::BindScript(const FString& ScriptId, const FString& Title)
{
	ClearFx();
	HunkId = ScriptId;
	bHunkBound = false;
	PortraitBox->SetVisibility(ESlateVisibility::Collapsed);
	MetersBox->SetVisibility(ESlateVisibility::Collapsed);
	MaladyText->SetText(FText::FromString(Title));
}

void UFixHimDialogueWidget::BindHunk(AFixHimHunk* Hunk, const FString& InHunkId)
{
	ClearFx();
	HunkId = InHunkId;
	bHunkBound = true;
	PortraitBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	MetersBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	if (!Portrait || !Hunk)
	{
		return;
	}
	UTextureRenderTarget2D* RT = Hunk->GetPortrait();
	if (UMaterialInterface* Mat = UFixHimSettings::Get()->PortraitMaterial.LoadSynchronous())
	{
		PortraitMID = UMaterialInstanceDynamic::Create(Mat, this);
		PortraitMID->SetTextureParameterValue(TEXT("Portrait"), RT);
		PortraitMID->SetScalarParameterValue(TEXT("Silhouette"), 0.f);
		// Solid backdrop in the character's theme colour.
		if (const UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
		{
			if (const FHunkDefinition* Def = D->FindHunk(HunkId))
			{
				PortraitMID->SetVectorParameterValue(TEXT("Background"), Def->GlowColor * 0.85f);
			}
		}
		Portrait->SetBrushFromMaterial(PortraitMID);
	}
	else
	{
		Portrait->SetBrushResourceObject(RT);
	}
	if (const UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		if (const FHunkDefinition* Def = D->FindHunk(HunkId))
		{
			MaladyText->SetText(FText::FromString(Def->Malady));
		}
	}
	RefreshMeters();
}

void UFixHimDialogueWidget::ShowView(const FDialogueView& View)
{
	Current = View;

	const bool bPlayer = View.Speaker == EDialogueSpeaker::Player;
	const bool bNarration = View.Speaker == EDialogueSpeaker::Narration;
	const bool bNamed = View.Speaker == EDialogueSpeaker::Named;
	NamePill->SetVisibility(bNarration ? ESlateVisibility::Hidden : ESlateVisibility::HitTestInvisible);
	// The malady is the hunk's tag line: not shown while the player or the narrator is the one talking.
	MaladyText->SetVisibility(bPlayer || bNarration ? ESlateVisibility::Hidden : ESlateVisibility::HitTestInvisible);
	if (bHunkBound)
	{
		// Narrator: no avatar box, but it keeps its space so the text does not shift left. Player: generic silhouette.
		PortraitBox->SetVisibility(bNarration ? ESlateVisibility::Hidden : ESlateVisibility::HitTestInvisible);
		PlayerSilhouette->SetVisibility(bPlayer ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
		Portrait->SetVisibility(bPlayer ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
	}
	NamePill->SetBrush(Rounded(bPlayer ? Plum : (bNamed ? PlumSoft : HotPink), 16.f));
	const UFixHimSaveSubsystem* SaveSub = UFixHimSaveSubsystem::Get(this);
	const FString PlayerName = SaveSub ? SaveSub->GetPlayerName() : UFixHimSettings::Get()->PlayerName;
	const FString Speaker = bPlayer ? PlayerName : (bNamed ? View.SpeakerName : View.HunkName);
	NameText->SetText(FText::FromString(Speaker.ToUpper()));
	TypingText->SetFont(Font(24, bNarration ? TEXT("Italic") : TEXT("Regular")));
	TypingText->SetColorAndOpacity(FSlateColor(bNarration ? PlumSoft : Plum));

	ParseTokens(View.Text);
	CharsShown = 0.f;
	LastTypeTick = 0;
	bTyping = true;
	TypingText->SetText(FText::GetEmpty());
	TypingText->SetVisibility(ESlateVisibility::HitTestInvisible);
	WordWrap->SetVisibility(ESlateVisibility::Collapsed);
	ChoiceBox->ClearChildren();
	ContinueHint->SetVisibility(ESlateVisibility::Hidden);

	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const float Speed = Save ? Save->Options().TextSpeed : 1.f;
	if (Speed >= 3.95f)
	{
		TryCompleteTyping();
	}

	if (View.Fx == TEXT("fade"))
	{
		FxPhase = EFxPhase::FadeOut;
		FxTimer = 0.f;
		FixHim::Sfx(this, "FadeOut");
		FadeText->SetText(FText::FromString(View.FxText.IsEmpty() ? TEXT("...") : View.FxText));
		FadeText->SetRenderOpacity(0.f);
		FadeCurtain->SetRenderOpacity(0.f);
		FadeCurtain->SetVisibility(ESlateVisibility::Visible);
	}
	else if (View.Fx == TEXT("hearts"))
	{
		SpawnHearts(16);
		FixHim::Sfx(this, "ReactHearts");
	}
}

void UFixHimDialogueWidget::ParseTokens(const FString& Marked)
{
	Tokens.Reset();
	PlainText.Reset();
	FString Buffer;
	auto FlushWords = [&]()
	{
		// Keep the separators attached so words reflow naturally in the wrap box.
		FString Word;
		for (const TCHAR C : Buffer)
		{
			Word.AppendChar(C);
			if (C == TEXT(' '))
			{
				Tokens.Add({ Word, FString() });
				Word.Reset();
			}
		}
		if (!Word.IsEmpty())
		{
			Tokens.Add({ Word, FString() });
		}
		Buffer.Reset();
	};

	for (int32 i = 0; i < Marked.Len(); ++i)
	{
		if (Marked[i] == TEXT('['))
		{
			const int32 Close = Marked.Find(TEXT("]"), ESearchCase::CaseSensitive, ESearchDir::FromStart, i);
			if (Close != INDEX_NONE)
			{
				FlushWords();
				const FString Inner = Marked.Mid(i + 1, Close - i - 1);
				FString Shown, Topic;
				if (!Inner.Split(TEXT("|"), &Shown, &Topic))
				{
					Shown = Inner;
					Topic = Inner;
				}
				Topic = Topic.TrimStartAndEnd().ToLower();
				Tokens.Add({ Shown, Current.ActiveTopics.Contains(Topic) ? Topic : FString() });
				PlainText += Shown;
				i = Close;
				continue;
			}
		}
		Buffer.AppendChar(Marked[i]);
		PlainText.AppendChar(Marked[i]);
	}
	FlushWords();
}

bool UFixHimDialogueWidget::TryCompleteTyping()
{
	if (!bTyping)
	{
		return false;
	}
	bTyping = false;
	CharsShown = PlainText.Len();
	TypingText->SetText(FText::FromString(PlainText));

	const bool bHasTopics = Tokens.ContainsByPredicate([](const FToken& T) { return !T.Topic.IsEmpty(); });
	if (bHasTopics)
	{
		BuildWordWrap();
		TypingText->SetVisibility(ESlateVisibility::Hidden); // keep its height so the box doesn't jump
		WordWrap->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	}
	BuildChoices();
	ContinueHint->SetVisibility(Current.Choices.IsEmpty() ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Hidden);
	ContinueHint->SetText(FText::FromString(Current.bWillEnd ? TEXT("click to end  x") : TEXT("click to continue  >")));
	return true;
}

void UFixHimDialogueWidget::BuildWordWrap()
{
	WordWrap->ClearChildren();
	const bool bNarration = Current.Speaker == EDialogueSpeaker::Narration;
	TWeakObjectPtr<UFixHimDialogueWidget> Self(this);
	for (const FToken& Tok : Tokens)
	{
		if (Tok.Topic.IsEmpty())
		{
			UTextBlock* W = MakeText(WidgetTree, Tok.Text, 24, bNarration ? PlumSoft : Plum, bNarration ? TEXT("Italic") : TEXT("Regular"));
			WordWrap->AddChildToWrapBox(W)->SetVerticalAlignment(VAlign_Center);
		}
		else
		{
			const FString Topic = Tok.Topic;
			UFixHimButton* B = WidgetTree->ConstructWidget<UFixHimButton>();
			FButtonStyle Style = ButtonStyle(Blush, Pink, HotPink, 10.f);
			Style.SetNormalPadding(FMargin(6.f, 0.f));
			Style.SetPressedPadding(FMargin(6.f, 1.f, 6.f, 0.f));
			B->SetStyle(Style);
			B->Label = MakeText(WidgetTree, Tok.Text, 24, HotPink, TEXT("Bold"));
			B->AddChild(B->Label);
			B->SetToolTipText(FText::FromString(TEXT("Ask about this")));
			B->ClickSfx = TEXT("TopicClick");
			B->Init([Self, Topic]()
			{
				if (Self.IsValid() && !Self->IsBusy())
				{
					if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(Self.Get()))
					{
						D->ClickTopic(Topic);
					}
				}
			});
			UWrapBoxSlot* S = WordWrap->AddChildToWrapBox(B);
			S->SetVerticalAlignment(VAlign_Center);
			S->SetPadding(FMargin(0.f, 0.f, 6.f, 0.f));
		}
	}
}

void UFixHimDialogueWidget::BuildChoices()
{
	ChoiceBox->ClearChildren();
	TWeakObjectPtr<UFixHimDialogueWidget> Self(this);
	for (int32 i = 0; i < Current.Choices.Num(); ++i)
	{
		const FString Label = FString::Printf(TEXT("%d.  %s"), i + 1, *Current.Choices[i]);
		UFixHimButton* B = WidgetTree->ConstructWidget<UFixHimButton>();
		FButtonStyle Style = ButtonStyle(FLinearColor(1.f, 1.f, 1.f, 0.9f), Blush, Pink, 14.f, FLinearColor(Pink.R, Pink.G, Pink.B, 0.6f));
		Style.SetNormalPadding(FMargin(16.f, 6.f));
		Style.SetPressedPadding(FMargin(16.f, 7.f, 16.f, 5.f));
		B->SetStyle(Style);
		B->Label = MakeText(WidgetTree, Label, 20, Plum, TEXT("Bold"));
		B->Label->SetAutoWrapText(true);
		B->Label->SetJustification(ETextJustify::Left);
		if (UButtonSlot* LabelSlot = Cast<UButtonSlot>(B->AddChild(B->Label)))
		{
			LabelSlot->SetHorizontalAlignment(HAlign_Fill);
			LabelSlot->SetPadding(FMargin(4.f, 0.f));
		}
		B->ClickSfx = TEXT("ChoiceSelect");
		B->Init([Self, i]()
		{
			if (Self.IsValid() && !Self->IsBusy())
			{
				if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(Self.Get()))
				{
					D->Choose(i);
				}
			}
		});
		UVerticalBoxSlot* S = ChoiceBox->AddChildToVerticalBox(B);
		S->SetPadding(FMargin(0.f, 3.f));
		S->SetHorizontalAlignment(HAlign_Fill);
	}
}

void UFixHimDialogueWidget::RefreshMeters()
{
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const FHunkProgress* P = Save ? Save->FindHunk(HunkId) : nullptr;
	const auto Pct = [](int32 V) { return FMath::Clamp(float(V) / MeterMax, 0.f, 1.f); };
	RomanceBar->SetPercent(P ? Pct(P->Romance) : 0.f);
	FriendBar->SetPercent(P ? Pct(P->Friendship) : 0.f);
	FrictionBar->SetPercent(P ? Pct(P->Friction) : 0.f);
}

void UFixHimDialogueWidget::OnStatChanged(const FString& InHunkId, ERelationshipAxis Axis, int32 Delta)
{
	if (InHunkId != HunkId)
	{
		return;
	}
	RefreshMeters();
	const TCHAR* Name = Axis == ERelationshipAxis::Romance ? TEXT("Romance") : Axis == ERelationshipAxis::Friendship ? TEXT("Friendship") : TEXT("Friction");
	const FLinearColor Color = Axis == ERelationshipAxis::Romance ? HotPink : Axis == ERelationshipAxis::Friendship ? Mint : Ember;
	SpawnFloater(FString::Printf(TEXT("%s%d %s"), Delta > 0 ? TEXT("+") : TEXT(""), Delta, Name), Color);
	if (Axis == ERelationshipAxis::Romance && Delta > 0)
	{
		SpawnHearts(3 + Delta * 2);
	}

	// Romance up is hearts, friendship up a happy ding, friction up a low grumble, and a loss a sad sigh.
	const bool bGood = Axis != ERelationshipAxis::Friction;
	if (Delta > 0)
	{
		FixHim::Sfx(this, !bGood ? "ReactAngry" : Axis == ERelationshipAxis::Romance ? "ReactHearts" : "ReactHappy");
	}
	else if (Delta < 0 && bGood)
	{
		FixHim::Sfx(this, "ReactSad");
	}
}

void UFixHimDialogueWidget::SpawnFloater(const FString& Text, const FLinearColor& Color)
{
	UBorder* Pill = WidgetTree->ConstructWidget<UBorder>();
	Pill->SetBrush(Rounded(Color, 14.f));
	Pill->SetPadding(FMargin(14.f, 4.f));
	Pill->SetContent(MakeText(WidgetTree, Text, 20, FLinearColor::White, TEXT("Bold")));
	FloaterBox->AddChildToVerticalBox(Pill)->SetPadding(FMargin(0.f, 3.f));
	FFloater F;
	F.Widget = Pill;
	F.Life = 1.8f;
	Floaters.Add(F);
}

void UFixHimDialogueWidget::SpawnHearts(int32 Count)
{
	UTexture2D* HeartTex = UFixHimSettings::Get()->HeartTexture.LoadSynchronous();
	for (int32 i = 0; i < Count; ++i)
	{
		UWidget* W = nullptr;
		const float Size = FMath::FRandRange(28.f, 64.f);
		if (HeartTex)
		{
			UImage* Img = WidgetTree->ConstructWidget<UImage>();
			Img->SetBrushFromTexture(HeartTex);
			Img->SetColorAndOpacity(FMath::Lerp(Pink, HotPink, FMath::FRand()));
			W = Img;
		}
		else
		{
			UTextBlock* T = MakeText(WidgetTree, TEXT("<3"), int32(Size * 0.6f), HotPink, TEXT("Bold"));
			W = T;
		}
		UCanvasPanelSlot* S = FxCanvas->AddChildToCanvas(W);
		S->SetSize(FVector2D(Size, Size));
		S->SetAutoSize(!HeartTex);
		FFloater F;
		F.Widget = W;
		F.bCanvas = true;
		F.Life = FMath::FRandRange(1.6f, 2.8f);
		F.Pos = FVector2D(FMath::FRandRange(0.1f, 0.9f) * ViewSize.X, ViewSize.Y * FMath::FRandRange(0.55f, 0.8f));
		F.Velocity = FVector2D(FMath::FRandRange(-40.f, 40.f), -FMath::FRandRange(140.f, 260.f));
		S->SetPosition(F.Pos);
		Floaters.Add(F);
	}
}

void UFixHimDialogueWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	ViewSize = MyGeometry.GetLocalSize();
	if (PanelSize)
	{
		PanelSize->SetMinDesiredHeight(ViewSize.Y * 0.25f);
	}

	if (bTyping && FxPhase == EFxPhase::None)
	{
		const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
		const float Speed = UFixHimSettings::Get()->TypewriterSpeed * (Save ? Save->Options().TextSpeed : 1.f);
		CharsShown += InDeltaTime * Speed;
		if (CharsShown >= PlainText.Len())
		{
			TryCompleteTyping();
		}
		else
		{
			const int32 Shown = FMath::FloorToInt(CharsShown);
			TypingText->SetText(FText::FromString(PlainText.Left(Shown)));
			// A very soft tick every third letter.
			if (Shown / 3 != LastTypeTick / 3 && !FChar::IsWhitespace(PlainText[Shown - 1]))
			{
				FixHim::Sfx(this, "TypeTick", 0.5f, 0.1f);
			}
			LastTypeTick = Shown;
		}
	}

	HintBlink += InDeltaTime;
	ContinueHint->SetRenderOpacity(0.55f + 0.45f * FMath::Sin(HintBlink * 4.f));

	// Fade-to-black ("...and then the lights went out").
	if (FxPhase != EFxPhase::None)
	{
		FxTimer += InDeltaTime;
		switch (FxPhase)
		{
		case EFxPhase::FadeOut:
			FadeCurtain->SetRenderOpacity(FMath::Clamp(FxTimer / FadeSeconds, 0.f, 1.f));
			if (FxTimer >= FadeSeconds) { FxPhase = EFxPhase::Hold; FxTimer = 0.f; }
			break;
		case EFxPhase::Hold:
			FadeText->SetRenderOpacity(FMath::Clamp(FxTimer / 0.6f, 0.f, 1.f) * FMath::Clamp((HoldSeconds - FxTimer) / 0.5f, 0.f, 1.f));
			if (FxTimer >= HoldSeconds) { FxPhase = EFxPhase::FadeIn; FxTimer = 0.f; }
			break;
		case EFxPhase::FadeIn:
			FadeCurtain->SetRenderOpacity(1.f - FMath::Clamp(FxTimer / FadeSeconds, 0.f, 1.f));
			if (FxTimer >= FadeSeconds)
			{
				FxPhase = EFxPhase::None;
				FadeCurtain->SetVisibility(ESlateVisibility::Collapsed);
			}
			break;
		default:
			break;
		}
	}

	for (int32 i = Floaters.Num() - 1; i >= 0; --i)
	{
		FFloater& F = Floaters[i];
		F.Age += InDeltaTime;
		UWidget* W = F.Widget.Get();
		if (!W || F.Age >= F.Life)
		{
			if (W)
			{
				W->RemoveFromParent();
			}
			Floaters.RemoveAtSwap(i);
			continue;
		}
		const float T = F.Age / F.Life;
		W->SetRenderOpacity(FMath::Clamp((1.f - T) * 2.f, 0.f, 1.f));
		if (F.bCanvas)
		{
			F.Pos += F.Velocity * InDeltaTime;
			F.Pos.X += FMath::Sin(F.Age * 5.f + i) * 30.f * InDeltaTime;
			if (UCanvasPanelSlot* S = Cast<UCanvasPanelSlot>(W->Slot))
			{
				S->SetPosition(F.Pos);
			}
			W->SetRenderTransformAngle(FMath::Sin(F.Age * 3.f + i) * 12.f);
		}
		else
		{
			W->SetRenderTranslation(FVector2D(0.f, -40.f * T));
		}
	}
}

FReply UFixHimDialogueWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	if (InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton)
	{
		if (AFixHimPlayerController* PC = GetFixHimPC())
		{
			PC->AdvanceDialogue();
		}
		return FReply::Handled();
	}
	return Super::NativeOnMouseButtonDown(InGeometry, InMouseEvent);
}
