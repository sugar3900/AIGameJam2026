// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimDialogueWidget.h"
#include "ICanFixHim.h"
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
#include "Components/ScrollBox.h"
#include "Components/ScrollBoxSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/WrapBox.h"
#include "Components/WrapBoxSlot.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/PackageName.h"

using namespace FixHimUI;

namespace
{
constexpr int32 MeterMax = FixHimStatMax;
constexpr float FadeSeconds = 0.9f;
constexpr float HoldSeconds = 2.6f;
} // namespace

void UFixHimDialogueWidget::BuildUI()
{
	UOverlay *Root = WidgetTree->ConstructWidget<UOverlay>();
	Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	WidgetTree->RootWidget = Root;

	// ---- Bottom panel ----
	PanelSize = WidgetTree->ConstructWidget<USizeBox>();
	UOverlaySlot *PanelSlot = Root->AddChildToOverlay(PanelSize);
	PanelSlot->SetHorizontalAlignment(HAlign_Fill);
	PanelSlot->SetVerticalAlignment(VAlign_Bottom);
	PanelSlot->SetPadding(FMargin(40.f, 0.f, 40.f, 22.f));

	UBorder *Panel = WidgetTree->ConstructWidget<UFixHimSurface>();
	Panel->SetBrush(Rounded(Cream, 26.f, Pink, 4.f));
	Panel->SetPadding(FMargin(32, 24, 48, 30));
	Panel->SetVisibility(ESlateVisibility::Visible);
	PanelSize->SetMaxDesiredHeight(760.f);
	PanelSize->AddChild(Panel);
	UHorizontalBox *Row = WidgetTree->ConstructWidget<UHorizontalBox>();
	Panel->SetContent(Row);

	// Portrait
	USizeBox *PortraitSize = WidgetTree->ConstructWidget<USizeBox>();
	PortraitSize->SetWidthOverride(210.f);
	PortraitSize->SetHeightOverride(210.f);
	UBorder *Frame = WidgetTree->ConstructWidget<UBorder>();
	Frame->SetBrush(Rounded(Plum, 20.f, HotPink, 4.f));
	Frame->SetPadding(FMargin(6.f));
	PortraitSize->AddChild(Frame);
	Portrait = WidgetTree->ConstructWidget<UImage>();
	Frame->SetContent(Portrait);
	PortraitBox = PortraitSize;
	UHorizontalBoxSlot *PortraitSlot = Row->AddChildToHorizontalBox(PortraitSize);
	PortraitSlot->SetVerticalAlignment(VAlign_Bottom);
	PortraitSlot->SetPadding(FMargin(0.f, 0.f, 24.f, 0.f));

	// Text column
	UVerticalBox *Col = WidgetTree->ConstructWidget<UFixHimStack>();
	UHorizontalBoxSlot *ColSlot = Row->AddChildToHorizontalBox(Col);
	ColSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UHorizontalBox *Header = WidgetTree->ConstructWidget<UHorizontalBox>();
	Col->AddChildToVerticalBox(Header)->SetPadding(FMargin(0.f, 0.f, 0.f, 8.f));

	NamePill = WidgetTree->ConstructWidget<UFixHimSurface>();
	NamePill->SetBrush(Rounded(HotPink, 16.f));
	NamePill->SetPadding(FMargin(28, 6, 36, 20));
	NameText = MakeText(WidgetTree, TEXT("NAME"), 28, FLinearColor::White, TEXT("Display"));
	NamePill->SetContent(NameText);
	Header->AddChildToHorizontalBox(NamePill)->SetVerticalAlignment(VAlign_Center);

	MaladyText = MakeText(WidgetTree, TEXT(""), 16, PlumSoft, TEXT("Italic"));
	UHorizontalBoxSlot *MalSlot = Header->AddChildToHorizontalBox(MaladyText);
	MalSlot->SetVerticalAlignment(VAlign_Center);
	MalSlot->SetPadding(FMargin(12.f, 0.f));
	MalSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	// Meters: one horizontal row at the right end of the header, each a label then its bar.
	UHorizontalBox *Meters = WidgetTree->ConstructWidget<UHorizontalBox>();
	auto AddMeter = [&](const FString &Label, const FLinearColor &Color) -> UProgressBar * {
		UHorizontalBox *M = WidgetTree->ConstructWidget<UHorizontalBox>();
		const FString IconName = Label == TEXT("ROMANCE")      ? TEXT("heart")
		                         : Label == TEXT("FRIENDSHIP") ? TEXT("users")
		                                                       : TEXT("lightning");
		USizeBox *IconBox = WidgetTree->ConstructWidget<USizeBox>();
		IconBox->SetWidthOverride(22);
		IconBox->SetHeightOverride(22);
		IconBox->AddChild(FixHimDesign::Icon(WidgetTree, IconName, Color));
		M->AddChildToHorizontalBox(IconBox)->SetPadding(FMargin(0, 0, 6, 0));
		UHorizontalBoxSlot *LabelSlot =
		    M->AddChildToHorizontalBox(MakeText(WidgetTree, Label, 14, PlumSoft, TEXT("Bold")));
		LabelSlot->SetVerticalAlignment(VAlign_Center);
		LabelSlot->SetPadding(FMargin(0.f, 0.f, 14.f, 0.f));
		USizeBox *BB = WidgetTree->ConstructWidget<USizeBox>();
		BB->SetWidthOverride(100.f);
		BB->SetHeightOverride(16.f);
		UProgressBar *Bar = WidgetTree->ConstructWidget<UProgressBar>();
		FProgressBarStyle Style;
		Style.SetBackgroundImage(Rounded(Plum.CopyWithNewOpacity(.14f), 8.f));
		Style.SetFillImage(Rounded(FLinearColor::White, 8.f));
		Style.SetMarqueeImage(Rounded(FLinearColor::White, 8.f));
		Bar->SetWidgetStyle(Style);
		Bar->SetFillColorAndOpacity(Color);
		Bar->SetPercent(0.f);
		BB->AddChild(Bar);
		M->AddChildToHorizontalBox(BB)->SetVerticalAlignment(VAlign_Center);
		Meters->AddChildToHorizontalBox(M)->SetPadding(FMargin(12.f, 0.f, 0.f, 0.f));
		return Bar;
	};
	RomanceBar = AddMeter(TEXT("ROMANCE"), HotPink);
	FriendBar = AddMeter(TEXT("FRIENDSHIP"), Mint);
	FrictionBar = AddMeter(TEXT("FRICTION"), Ember);
	Col->AddChildToVerticalBox(Meters)->SetPadding(FMargin(0, 0, 0, 12));
	MetersBox = Meters;

	// Line text: typewriter text while typing, then a wrap box of words so [topics] can be clicked.
	UOverlay *TextArea = WidgetTree->ConstructWidget<UOverlay>();
	LineArea = TextArea;
	LineBounds = WidgetTree->ConstructWidget<USizeBox>();
	LineBounds->SetMaxDesiredHeight(240);
	auto *Inset = WidgetTree->ConstructWidget<UBorder>();
	Inset->SetBrushColor(FLinearColor::Transparent);
	Inset->SetPadding(FMargin(8, 0, 16, 0));
	LineBounds->AddChild(Inset);
	auto *LineScroll = WidgetTree->ConstructWidget<UScrollBox>();
	LineScroll->SetAnimateWheelScrolling(false);
	LineScroll->SetScrollbarThickness(FVector2D(7, 7));
	auto BarStyle = LineScroll->GetWidgetBarStyle();
	BarStyle.SetNormalThumbImage(Rounded(PlumSoft, 3));
	BarStyle.SetHoveredThumbImage(Rounded(Pink, 3));
	LineScroll->SetWidgetBarStyle(BarStyle);
	Inset->SetContent(LineScroll);
	// Room inside the scroll clip for the sheared line, whose lower rows lean left of its layout box.
	CastChecked<UScrollBoxSlot>(LineScroll->AddChild(TextArea))->SetPadding(FMargin(20, 0, 20, 0));
	Col->AddChildToVerticalBox(LineBounds)->SetPadding(FMargin(0, 2, 0, 20));
	TypingText = MakeText(WidgetTree, TEXT(""), 24, Plum);
	TypingText->SetAutoWrapText(true);
	TextArea->AddChildToOverlay(TypingText)->SetHorizontalAlignment(HAlign_Fill);
	WordWrap = WidgetTree->ConstructWidget<UWrapBox>();
	WordWrap->SetInnerSlotPadding(FVector2D(0.f, 2.f));
	WordWrap->SetVisibility(ESlateVisibility::Collapsed);
	TextArea->AddChildToOverlay(WordWrap)->SetHorizontalAlignment(HAlign_Fill);

	ChoiceBox = WidgetTree->ConstructWidget<UFixHimStack>();
	Col->AddChildToVerticalBox(ChoiceBox);

	ContinueHint = MakeText(WidgetTree, TEXT("Continue  /  Enter"), 18, Pink, TEXT("Bold"));
	ContinueHint->SetJustification(ETextJustify::Right);
	UVerticalBoxSlot *HintSlot = Col->AddChildToVerticalBox(ContinueHint);
	HintSlot->SetHorizontalAlignment(HAlign_Right);

	// Stat floaters stack above the panel, right side.
	FloaterBox = WidgetTree->ConstructWidget<UVerticalBox>();
	FloaterBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	UOverlaySlot *FloatSlot = Root->AddChildToOverlay(FloaterBox);
	FloatSlot->SetHorizontalAlignment(HAlign_Right);
	FloatSlot->SetVerticalAlignment(VAlign_Bottom);
	FloatSlot->SetPadding(FMargin(0.f, 0.f, 70.f, 400.f));

	// Full-screen fx layers.
	FxCanvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	FxCanvas->SetVisibility(ESlateVisibility::HitTestInvisible);
	UOverlaySlot *FxSlot = Root->AddChildToOverlay(FxCanvas);
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
	UOverlaySlot *FadeSlot = Root->AddChildToOverlay(FadeCurtain);
	FadeSlot->SetHorizontalAlignment(HAlign_Fill);
	FadeSlot->SetVerticalAlignment(VAlign_Fill);
}

void UFixHimDialogueWidget::ClearFx()
{
	for (FFloater &F : Floaters)
	{
		if (UWidget *W = F.Widget.Get())
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

void UFixHimDialogueWidget::BindScript(const FString &ScriptId, const FString &Title)
{
	ClearFx();
	HunkId = ScriptId;
	bScriptScene = true;
	PortraitBox->SetVisibility(ESlateVisibility::Collapsed);
	MetersBox->SetVisibility(ESlateVisibility::Collapsed);
	MaladyText->SetText(FText::FromString(Title));
}

void UFixHimDialogueWidget::BindHunk(AFixHimHunk *Hunk, const FString &InHunkId)
{
	ClearFx();
	HunkId = InHunkId;
	bScriptScene = false;
	PortraitBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	MetersBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	if (!Portrait || !Hunk)
	{
		return;
	}
	HunkPortraitRT = Hunk->GetPortrait();
	PortraitMID = nullptr;
	HunkPortraitTexture = nullptr;
	if (const UFixHimDialogueSubsystem *D = UFixHimDialogueSubsystem::Get(this))
	{
		const FHunkDefinition *Def = D->FindHunk(HunkId);
		if (Def && !Def->Portrait.IsEmpty())
		{
			// Painted portrait from look.portrait: "/Game/Dir/Asset" or "/Game/Dir/Asset.Asset", like look.mesh.
			FString ObjectPath = Def->Portrait;
			if (!FPackageName::GetShortName(ObjectPath).Contains(TEXT(".")))
			{
				ObjectPath += TEXT(".") + FPackageName::GetShortName(ObjectPath);
			}
			HunkPortraitTexture = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(ObjectPath)).LoadSynchronous();
			if (!HunkPortraitTexture)
			{
				UE_LOG(LogFixHim, Warning, TEXT("Portrait '%s' for %s not found; using the scene capture"),
				       *Def->Portrait, *HunkId);
			}
		}
	}
	if (!PlayerPortraitTexture)
	{
		// Load up front so the first "You:" line doesn't flash an empty frame.
		PlayerPortraitTexture = UFixHimSettings::Get()->PlayerPortraitTexture.LoadSynchronous();
	}
	if (UMaterialInterface *Mat = UFixHimSettings::Get()->PortraitMaterial.LoadSynchronous())
	{
		PortraitMID = UMaterialInstanceDynamic::Create(Mat, this);
		PortraitMID->SetTextureParameterValue(TEXT("Portrait"), HunkPortraitRT);
		PortraitMID->SetScalarParameterValue(TEXT("Silhouette"), 0.f);
		// Solid backdrop in the character's theme colour.
		if (const UFixHimDialogueSubsystem *D = UFixHimDialogueSubsystem::Get(this))
		{
			if (const FHunkDefinition *Def = D->FindHunk(HunkId))
			{
				PortraitMID->SetVectorParameterValue(TEXT("Background"), Def->GlowColor * 0.85f);
			}
		}
	}
	ApplySpeakerPortrait(EDialogueSpeaker::Hunk);
	if (const UFixHimDialogueSubsystem *D = UFixHimDialogueSubsystem::Get(this))
	{
		if (const FHunkDefinition *Def = D->FindHunk(HunkId))
		{
			MaladyText->SetText(FText::FromString(Def->Malady));
		}
	}
	RefreshMeters();
}

void UFixHimDialogueWidget::ApplySpeakerPortrait(EDialogueSpeaker Speaker)
{
	if (bScriptScene || !Portrait || !PortraitBox)
	{
		return; // scenes never show a portrait
	}
	if (Speaker == EDialogueSpeaker::Narration)
	{
		// Narration uses the full reading width instead of keeping an empty portrait column.
		PortraitBox->SetVisibility(ESlateVisibility::Collapsed);
		return;
	}
	PortraitBox->SetVisibility(ESlateVisibility::HitTestInvisible);
	if (Speaker == EDialogueSpeaker::Player)
	{
		if (!PlayerPortraitTexture)
		{
			PlayerPortraitTexture = UFixHimSettings::Get()->PlayerPortraitTexture.LoadSynchronous();
		}
		if (PlayerPortraitTexture)
		{
			Portrait->SetBrushFromTexture(PlayerPortraitTexture);
			Portrait->SetColorAndOpacity(FLinearColor::White);
			return;
		}
	}
	// The hunk (and declared extra speakers, as before): his painted portrait, else the scene-capture still.
	if (HunkPortraitTexture)
	{
		Portrait->SetBrushFromTexture(HunkPortraitTexture);
		Portrait->SetColorAndOpacity(FLinearColor::White);
	}
	else if (PortraitMID)
	{
		Portrait->SetBrushFromMaterial(PortraitMID);
	}
	else if (HunkPortraitRT)
	{
		Portrait->SetBrushResourceObject(HunkPortraitRT);
	}
}

void UFixHimDialogueWidget::ShowView(const FDialogueView &View)
{
	Current = View;
	ApplySpeakerPortrait(View.Speaker);

	const bool bPlayer = View.Speaker == EDialogueSpeaker::Player;
	const bool bNarration = View.Speaker == EDialogueSpeaker::Narration;
	MetersBox->SetVisibility(bNarration || bScriptScene ? ESlateVisibility::Collapsed
	                                                    : ESlateVisibility::HitTestInvisible);
	const bool bNamed = View.Speaker == EDialogueSpeaker::Named;
	NamePill->SetVisibility(bNarration ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
	// The malady is the hunk's tag line: not shown while the player or the narrator is the one talking.
	if (!bScriptScene)
	{
		MaladyText->SetVisibility(bPlayer || bNarration ? ESlateVisibility::Collapsed
		                                                : ESlateVisibility::HitTestInvisible);
	}
	NamePill->SetBrush(Rounded(bPlayer ? Plum : (bNamed ? PlumSoft : HotPink), 16.f));
	const UFixHimSaveSubsystem *SaveSub = UFixHimSaveSubsystem::Get(this);
	const FString PlayerName = SaveSub ? SaveSub->GetPlayerName() : UFixHimSettings::Get()->PlayerName;
	const FString Speaker = bPlayer ? PlayerName : (bNamed ? View.SpeakerName : View.HunkName);
	NameText->SetText(FText::FromString(Speaker.ToUpper()));
	// Spoken lines use the display face, sheared to the 12° grid as one block. Narration stays upright body text.
	TypingText->SetFont(bNarration ? Font(24, TEXT("Regular")) : Font(FixHimDesign::Line, TEXT("Display")));
	FWidgetTransform LineLean;
	if (!bNarration)
		LineLean.Shear = FVector2D(-FMath::RadiansToDegrees(FMath::Atan(FixHimDesign::DisplayShear)), 0);
	LineArea->SetRenderTransform(LineLean);
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

	const UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this);
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

void UFixHimDialogueWidget::ParseTokens(const FString &Marked)
{
	Tokens.Reset();
	PlainText.Reset();
	FString Buffer;
	auto FlushWords = [&]() {
		// Keep the separators attached so words reflow naturally in the wrap box.
		FString Word;
		for (const TCHAR C : Buffer)
		{
			Word.AppendChar(C);
			if (C == TEXT(' '))
			{
				Tokens.Add({Word, FString()});
				Word.Reset();
			}
		}
		if (!Word.IsEmpty())
		{
			Tokens.Add({Word, FString()});
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
				Tokens.Add({Shown, Current.ActiveTopics.Contains(Topic) ? Topic : FString()});
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

	const bool bHasTopics = Tokens.ContainsByPredicate([](const FToken &T) { return !T.Topic.IsEmpty(); });
	if (bHasTopics)
	{
		BuildWordWrap();
		TypingText->SetVisibility(ESlateVisibility::Hidden); // keep its height so the box doesn't jump
		WordWrap->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	}
	BuildChoices();
	ContinueHint->SetVisibility(Current.Choices.IsEmpty() ? ESlateVisibility::HitTestInvisible
	                                                      : ESlateVisibility::Hidden);
	ContinueHint->SetText(FText::FromString(Current.bWillEnd ? TEXT("Finish  /  Enter") : TEXT("Continue  /  Enter")));
	return true;
}

void UFixHimDialogueWidget::BuildWordWrap()
{
	WordWrap->ClearChildren();
	const bool bNarration = Current.Speaker == EDialogueSpeaker::Narration;
	TWeakObjectPtr<UFixHimDialogueWidget> Self(this);
	const int32 LineSize = bNarration ? 24 : FixHimDesign::Line;
	// "Body" resolves to the display face without MakeText's per-widget shear; LineArea leans the whole line.
	const TCHAR *LineFace = bNarration ? TEXT("Regular") : TEXT("DisplayFace");
	auto FlowTokens = Tokens;
	for (int32 TokenIndex = 0; TokenIndex < FlowTokens.Num(); ++TokenIndex)
	{
		const FToken &Tok = FlowTokens[TokenIndex];
		if (Tok.Text.IsEmpty())
			continue;
		if (Tok.Topic.IsEmpty())
		{
			UTextBlock *W = MakeText(WidgetTree, Tok.Text, LineSize, bNarration ? PlumSoft : Plum, LineFace);
			WordWrap->AddChildToWrapBox(W)->SetVerticalAlignment(VAlign_Center);
		}
		else
		{
			const FString Topic = Tok.Topic;
			UFixHimButton *B = WidgetTree->ConstructWidget<UFixHimButton>();
			B->SetVariant(EFixHimButtonVariant::Topic);
			FButtonStyle Style = ButtonStyle(Cream, Cream, Cream, 0.f, Pink);
			Style.SetNormalPadding(FMargin(0));
			Style.SetPressedPadding(FMargin(0));
			B->SetStyle(Style);
			B->Label = MakeText(WidgetTree, Tok.Text, LineSize, HotPink, bNarration ? TEXT("Semibold") : LineFace);
			B->SetCursor(EMouseCursor::Hand);
			CastChecked<UButtonSlot>(B->AddChild(B->Label))->SetPadding(FMargin(0));
			B->SetToolTipText(FText::FromString(TEXT("Ask about this")));
			B->ClickSfx = TEXT("TopicClick");
			B->Init([Self, Topic]() {
				if (Self.IsValid() && !Self->IsBusy())
				{
					if (UFixHimDialogueSubsystem *D = UFixHimDialogueSubsystem::Get(Self.Get()))
					{
						D->ClickTopic(Topic);
					}
				}
			});
			auto *Run = WidgetTree->ConstructWidget<UHorizontalBox>();
			Run->AddChildToHorizontalBox(B)->SetVerticalAlignment(VAlign_Center);
			// Keep trailing punctuation with its linked word, without expanding the underline.
			if (FlowTokens.IsValidIndex(TokenIndex + 1) && FlowTokens[TokenIndex + 1].Topic.IsEmpty())
			{
				auto &Next = FlowTokens[TokenIndex + 1].Text;
				int32 End = 0;
				while (End < Next.Len() && FString(TEXT(".,!?;:)]")).Contains(Next.Mid(End, 1)))
					++End;
				if (End > 0)
				{
					while (End < Next.Len() && FChar::IsWhitespace(Next[End]))
						++End;
					auto *Punctuation =
					    MakeText(WidgetTree, Next.Left(End), LineSize, bNarration ? PlumSoft : Plum, LineFace);
					Run->AddChildToHorizontalBox(Punctuation)->SetVerticalAlignment(VAlign_Center);
					Next.RightChopInline(End);
				}
			}
			UWrapBoxSlot *S = WordWrap->AddChildToWrapBox(Run);
			S->SetVerticalAlignment(VAlign_Center);
			S->SetPadding(FMargin(0));
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
		UFixHimButton *B = WidgetTree->ConstructWidget<UFixHimButton>();
		B->SetVariant(EFixHimButtonVariant::Reply);
		FButtonStyle Style = ButtonStyle(Cream, Pink, Pink, 12, Gold);
		Style.SetNormalPadding(FMargin(52, 9, 32, 21));
		Style.SetPressedPadding(FMargin(54, 12, 30, 18));
		B->SetStyle(Style);
		B->Label = MakeText(WidgetTree, Label, FixHimDesign::Reply, Plum, TEXT("Display"));
		B->Label->SetAutoWrapText(true);
		B->Label->SetRenderTranslation(FVector2D(0, B->Label->GetFont().Size * .08f));
		B->Label->SetColorAndOpacity(FSlateColor::UseForeground());
		B->Label->SetJustification(ETextJustify::Left);
		if (UButtonSlot *LabelSlot = Cast<UButtonSlot>(B->AddChild(B->Label)))
		{
			LabelSlot->SetHorizontalAlignment(HAlign_Fill);
			LabelSlot->SetPadding(FMargin(4.f, 0.f));
		}
		B->ClickSfx = TEXT("ChoiceSelect");
		B->Init([Self, i]() {
			if (Self.IsValid() && !Self->IsBusy())
			{
				if (UFixHimDialogueSubsystem *D = UFixHimDialogueSubsystem::Get(Self.Get()))
				{
					D->Choose(i);
				}
			}
		});
		UVerticalBoxSlot *S = ChoiceBox->AddChildToVerticalBox(B);
		S->SetPadding(FMargin(0.f, 3.f));
		S->SetHorizontalAlignment(HAlign_Fill);
		if (i == 0)
			B->SetKeyboardFocus();
	}
}

void UFixHimDialogueWidget::RefreshMeters()
{
	const UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this);
	const FHunkProgress *P = Save ? Save->FindHunk(HunkId) : nullptr;
	const auto Pct = [](int32 V) { return FMath::Clamp(float(V) / MeterMax, 0.f, 1.f); };
	RomanceBar->SetPercent(P ? Pct(P->Romance) : 0.f);
	FriendBar->SetPercent(P ? Pct(P->Friendship) : 0.f);
	FrictionBar->SetPercent(P ? Pct(P->Friction) : 0.f);
}

void UFixHimDialogueWidget::OnStatChanged(const FString &InHunkId, ERelationshipAxis Axis, int32 Delta)
{
	if (InHunkId != HunkId)
	{
		return;
	}
	RefreshMeters();
	const TCHAR *Name = Axis == ERelationshipAxis::Romance      ? TEXT("Romance")
	                    : Axis == ERelationshipAxis::Friendship ? TEXT("Friendship")
	                                                            : TEXT("Friction");
	const FLinearColor Color = Axis == ERelationshipAxis::Romance      ? HotPink
	                           : Axis == ERelationshipAxis::Friendship ? Mint
	                                                                   : Ember;
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

void UFixHimDialogueWidget::SpawnFloater(const FString &Text, const FLinearColor &Color)
{
	UBorder *Pill = WidgetTree->ConstructWidget<UFixHimSurface>();
	Pill->SetBrush(Rounded(Color, 20.f));
	Pill->SetPadding(FMargin(20.f, 7.f));
	Pill->SetContent(MakeText(WidgetTree, Text, 30, FLinearColor::White, TEXT("Bold")));
	FloaterBox->AddChildToVerticalBox(Pill)->SetPadding(FMargin(0.f, 4.f));
	FFloater F;
	F.Widget = Pill;
	F.Life = 1.8f;
	Floaters.Add(F);
}

void UFixHimDialogueWidget::SpawnHearts(int32 Count)
{
	if (FixHimDesign::ReducedMotion())
		return;
	UTexture2D *HeartTex = UFixHimSettings::Get()->HeartTexture.LoadSynchronous();
	for (int32 i = 0; i < Count; ++i)
	{
		UWidget *W = nullptr;
		const float Size = FMath::FRandRange(40.f, 88.f);
		if (HeartTex)
		{
			UImage *Img = WidgetTree->ConstructWidget<UImage>();
			Img->SetBrushFromTexture(HeartTex);
			Img->SetColorAndOpacity(FMath::Lerp(Pink, HotPink, FMath::FRand()));
			W = Img;
		}
		else
		{
			UTextBlock *T = MakeText(WidgetTree, TEXT("<3"), int32(Size * 0.6f), HotPink, TEXT("Bold"));
			W = T;
		}
		UCanvasPanelSlot *S = FxCanvas->AddChildToCanvas(W);
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

void UFixHimDialogueWidget::NativeTick(const FGeometry &MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	ViewSize = MyGeometry.GetLocalSize();
	if (PanelSize)
	{
		// A quarter of the screen plus room for two more lines of text (24pt, ~32px each).
		PanelSize->SetMinDesiredHeight(160);
		PanelSize->SetMaxDesiredHeight(ViewSize.Y * .78f);
		const float HeaderHeight = NamePill->IsVisible() ? 160.f : 20.f;
		LineBounds->SetMaxDesiredHeight(
		    FMath::Max(72.f, ViewSize.Y * .78f - ChoiceBox->GetDesiredSize().Y - HeaderHeight - 100.f));
	}

	if (bTyping && FxPhase == EFxPhase::None)
	{
		const UFixHimSaveSubsystem *Save = UFixHimSaveSubsystem::Get(this);
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
			if (Shown / 3 != LastTypeTick / 3 && Shown > 0 && !FChar::IsWhitespace(PlainText[Shown - 1]))
			{
				FixHim::Sfx(this, "TypeTick", 0.5f, 0.1f);
			}
			LastTypeTick = Shown;
		}
	}

	HintBlink += InDeltaTime;
	ContinueHint->SetRenderOpacity(FixHimDesign::ReducedMotion() ? 1.f : .8f + .2f * FMath::Sin(HintBlink * 3.f));

	// Fade-to-black ("...and then the lights went out").
	if (FxPhase != EFxPhase::None)
	{
		FxTimer += InDeltaTime;
		switch (FxPhase)
		{
		case EFxPhase::FadeOut:
			FadeCurtain->SetRenderOpacity(FMath::Clamp(FxTimer / FadeSeconds, 0.f, 1.f));
			if (FxTimer >= FadeSeconds)
			{
				FxPhase = EFxPhase::Hold;
				FxTimer = 0.f;
			}
			break;
		case EFxPhase::Hold:
			FadeText->SetRenderOpacity(FMath::Clamp(FxTimer / 0.6f, 0.f, 1.f) *
			                           FMath::Clamp((HoldSeconds - FxTimer) / 0.5f, 0.f, 1.f));
			if (FxTimer >= HoldSeconds)
			{
				FxPhase = EFxPhase::FadeIn;
				FxTimer = 0.f;
			}
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
		FFloater &F = Floaters[i];
		F.Age += InDeltaTime;
		UWidget *W = F.Widget.Get();
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
		if (FixHimDesign::ReducedMotion())
			continue;
		if (F.bCanvas)
		{
			F.Pos += F.Velocity * InDeltaTime;
			F.Pos.X += FMath::Sin(F.Age * 5.f + i) * 30.f * InDeltaTime;
			if (UCanvasPanelSlot *S = Cast<UCanvasPanelSlot>(W->Slot))
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

FReply UFixHimDialogueWidget::NativeOnMouseButtonDown(const FGeometry &InGeometry, const FPointerEvent &InMouseEvent)
{
	if (InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton)
	{
		if (AFixHimPlayerController *PC = GetFixHimPC())
		{
			PC->AdvanceDialogue();
		}
		return FReply::Handled();
	}
	return Super::NativeOnMouseButtonDown(InGeometry, InMouseEvent);
}
