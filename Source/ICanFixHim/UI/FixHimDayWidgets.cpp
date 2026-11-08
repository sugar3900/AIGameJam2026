// I Can Fix Him - AI Game Jam 2026

#include "UI/FixHimDayWidgets.h"
#include "Player/FixHimPlayerController.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "World/FixHimHunk.h"
#include "Core/FixHimSettings.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"

using namespace FixHimUI;

// ---------------------------------------------------------------------------
// Radio

void UFixHimRadioWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	Root->SetVisibility(ESlateVisibility::HitTestInvisible);
	WidgetTree->RootWidget = Root;

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(860.f);
	UOverlaySlot* SizeSlot = Root->AddChildToOverlay(Size);
	SizeSlot->SetHorizontalAlignment(HAlign_Center);
	SizeSlot->SetVerticalAlignment(VAlign_Bottom);
	SizeSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 64.f));

	Panel = WidgetTree->ConstructWidget<UBorder>();
	Panel->SetBrush(Rounded(FLinearColor(Plum.R, Plum.G, Plum.B, 0.86f), 20.f, Pink, 2.f));
	Panel->SetPadding(FMargin(22.f, 12.f));
	Size->AddChild(Panel);

	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	Panel->SetContent(Col);

	UHorizontalBox* Top = WidgetTree->ConstructWidget<UHorizontalBox>();
	Col->AddChildToVerticalBox(Top)->SetPadding(FMargin(0.f, 0.f, 0.f, 6.f));

	OnAirDot = WidgetTree->ConstructWidget<UBorder>();
	OnAirDot->SetBrush(Rounded(FLinearColor(1.f, 0.2f, 0.25f), 8.f));
	OnAirDot->SetPadding(FMargin(10.f, 2.f));
	OnAirDot->SetContent(MakeText(WidgetTree, TEXT("ON AIR"), 12, FLinearColor::White, TEXT("Bold")));
	Top->AddChildToHorizontalBox(OnAirDot)->SetVerticalAlignment(VAlign_Center);

	Header = MakeText(WidgetTree, TEXT(""), 14, Blush, TEXT("Bold"));
	UHorizontalBoxSlot* HeaderSlot = Top->AddChildToHorizontalBox(Header);
	HeaderSlot->SetVerticalAlignment(VAlign_Center);
	HeaderSlot->SetPadding(FMargin(10.f, 0.f));

	UHorizontalBox* Body = WidgetTree->ConstructWidget<UHorizontalBox>();
	Col->AddChildToVerticalBox(Body);
	Speaker = MakeText(WidgetTree, TEXT(""), 19, Pink, TEXT("Bold"));
	Body->AddChildToHorizontalBox(Speaker)->SetPadding(FMargin(0.f, 0.f, 10.f, 0.f));
	Line = MakeText(WidgetTree, TEXT(""), 19, Cream);
	Line->SetAutoWrapText(true);
	UHorizontalBoxSlot* LineSlot = Body->AddChildToHorizontalBox(Line);
	LineSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	Panel->SetVisibility(ESlateVisibility::Collapsed);
}

void UFixHimRadioWidget::Play(const FString& ShowName, const FDialogueNode& Episode, TFunction<void()> InOnFinished)
{
	Lines = Episode.Lines;
	OnFinished = MoveTemp(InOnFinished);
	bPlaying = Lines.Num() > 0;
	Header->SetText(FText::FromString(ShowName.ToUpper()));
	Panel->SetVisibility(bPlaying ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	if (bPlaying)
	{
		ShowLine(0);
	}
	else if (OnFinished)
	{
		OnFinished();
	}
}

void UFixHimRadioWidget::Stop()
{
	bPlaying = false;
	Panel->SetVisibility(ESlateVisibility::Collapsed);
	OnFinished = nullptr;
}

void UFixHimRadioWidget::ShowLine(int32 Index)
{
	LineIndex = Index;
	LineTimer = 0.f;
	const FDialogueLine& L = Lines[Index];
	const bool bCue = L.Speaker == EDialogueSpeaker::Narration;
	Speaker->SetText(FText::FromString(bCue ? FString() : (L.SpeakerName.IsEmpty() ? FString(TEXT("")) : L.SpeakerName.ToUpper() + TEXT(":"))));
	Speaker->SetVisibility(bCue || L.SpeakerName.IsEmpty() ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
	Line->SetFont(Font(19, bCue ? TEXT("Italic") : TEXT("Regular")));
	Line->SetColorAndOpacity(FSlateColor(bCue ? Blush : Cream));
	Line->SetText(FText::FromString(L.Text));
	// Roughly read-aloud pace: ~2.8 words per second plus a beat.
	TArray<FString> Words;
	L.Text.ParseIntoArrayWS(Words);
	LineDuration = 1.1f + Words.Num() * 0.36f;
}

void UFixHimRadioWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;
	if (!bPlaying)
	{
		return;
	}
	OnAirDot->SetRenderOpacity(0.6f + 0.4f * FMath::Sin(Age * 5.f));
	LineTimer += InDeltaTime;
	if (LineTimer >= LineDuration)
	{
		if (LineIndex + 1 < Lines.Num())
		{
			ShowLine(LineIndex + 1);
		}
		else
		{
			bPlaying = false;
			Panel->SetVisibility(ESlateVisibility::Collapsed);
			TFunction<void()> Done = MoveTemp(OnFinished);
			OnFinished = nullptr;
			if (Done)
			{
				Done();
			}
		}
	}
}

// ---------------------------------------------------------------------------
// Transition

namespace
{
	constexpr float FadeTime = 1.2f;
	constexpr float CardTime = 2.6f;
}

void UFixHimTransitionWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	Curtain = WidgetTree->ConstructWidget<UBorder>();
	Curtain->SetBrushColor(FLinearColor(0.02f, 0.f, 0.03f, 1.f));
	Curtain->SetHorizontalAlignment(HAlign_Center);
	Curtain->SetVerticalAlignment(VAlign_Center);
	UOverlaySlot* CSlot = Root->AddChildToOverlay(Curtain);
	CSlot->SetHorizontalAlignment(HAlign_Fill);
	CSlot->SetVerticalAlignment(VAlign_Fill);

	UVerticalBox* Col = WidgetTree->ConstructWidget<UVerticalBox>();
	Curtain->SetContent(Col);
	TitleText = MakeText(WidgetTree, TEXT(""), 76, Pink, TEXT("Bold"));
	TitleText->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(TitleText)->SetHorizontalAlignment(HAlign_Center);
	SubtitleText = MakeText(WidgetTree, TEXT(""), 26, Blush, TEXT("Italic"));
	SubtitleText->SetJustification(ETextJustify::Center);
	Col->AddChildToVerticalBox(SubtitleText)->SetHorizontalAlignment(HAlign_Center);
}

void UFixHimTransitionWidget::Play(const FString& Title, const FString& Subtitle, bool bStartBlack, bool bFadeBackIn, TFunction<void()> InOnMidpoint, TFunction<void()> InOnDone)
{
	FixHim::Sfx(this, bStartBlack ? "DayStart" : "DayEnd");
	TitleText->SetText(FText::FromString(Title));
	SubtitleText->SetText(FText::FromString(Subtitle));
	TitleText->SetRenderOpacity(0.f);
	SubtitleText->SetRenderOpacity(0.f);
	OnMidpoint = MoveTemp(InOnMidpoint);
	OnDone = MoveTemp(InOnDone);
	bFadeIn = bFadeBackIn;
	Timer = 0.f;
	SetVisibility(ESlateVisibility::Visible);
	if (bStartBlack)
	{
		Curtain->SetRenderOpacity(1.f);
		Phase = EPhase::Card;
		if (OnMidpoint) { TFunction<void()> M = MoveTemp(OnMidpoint); M(); }
	}
	else
	{
		Curtain->SetRenderOpacity(0.f);
		Phase = EPhase::FadeOut;
	}
}

void UFixHimTransitionWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	if (Phase == EPhase::Idle)
	{
		return;
	}
	Timer += InDeltaTime;
	switch (Phase)
	{
	case EPhase::FadeOut:
		Curtain->SetRenderOpacity(FMath::Clamp(Timer / FadeTime, 0.f, 1.f));
		if (Timer >= FadeTime)
		{
			Phase = EPhase::Card;
			Timer = 0.f;
			if (OnMidpoint) { TFunction<void()> M = MoveTemp(OnMidpoint); M(); }
		}
		break;
	case EPhase::Card:
	{
		const float In = FMath::Clamp(Timer / 0.6f, 0.f, 1.f);
		const float Out = FMath::Clamp((CardTime - Timer) / 0.5f, 0.f, 1.f);
		TitleText->SetRenderOpacity(In * Out);
		TitleText->SetRenderScale(FVector2D(FMath::Lerp(1.25f, 1.f, EaseOutBack(Timer / 0.6f))));
		SubtitleText->SetRenderOpacity(FMath::Clamp((Timer - 0.4f) / 0.6f, 0.f, 1.f) * Out);
		if (Timer >= CardTime)
		{
			Timer = 0.f;
			if (bFadeIn)
			{
				Phase = EPhase::FadeIn;
			}
			else
			{
				Phase = EPhase::Idle;
				if (OnDone) { TFunction<void()> D = MoveTemp(OnDone); D(); }
			}
		}
		break;
	}
	case EPhase::FadeIn:
		Curtain->SetRenderOpacity(1.f - FMath::Clamp(Timer / FadeTime, 0.f, 1.f));
		if (Timer >= FadeTime)
		{
			Phase = EPhase::Idle;
			SetVisibility(ESlateVisibility::Collapsed);
			if (OnDone) { TFunction<void()> D = MoveTemp(OnDone); D(); }
		}
		break;
	default:
		break;
	}
}

// ---------------------------------------------------------------------------
// Keepsake

void UFixHimKeepsakeWidget::BuildUI()
{
	UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
	WidgetTree->RootWidget = Root;

	UBorder* Dim = WidgetTree->ConstructWidget<UBorder>();
	Dim->SetBrushColor(FLinearColor(0.06f, 0.f, 0.05f, 0.92f));
	UOverlaySlot* DimSlot = Root->AddChildToOverlay(Dim);
	DimSlot->SetHorizontalAlignment(HAlign_Fill);
	DimSlot->SetVerticalAlignment(VAlign_Fill);

	Card = WidgetTree->ConstructWidget<UBorder>();
	Card->SetBrush(Rounded(Cream, 28.f, Pink, 4.f));
	Card->SetPadding(FMargin(36.f, 28.f));
	UOverlaySlot* CardSlot = Root->AddChildToOverlay(Card);
	CardSlot->SetHorizontalAlignment(HAlign_Center);
	CardSlot->SetVerticalAlignment(VAlign_Center);

	Content = WidgetTree->ConstructWidget<UVerticalBox>();
	Card->SetContent(Content);
}

void UFixHimKeepsakeWidget::Setup(const TArray<FFixHimKeepsakeEntry>& InEntries)
{
	Entries = InEntries;
	ShowChooser();
}

void UFixHimKeepsakeWidget::ShowChooser()
{
	Content->ClearChildren();
	Age = 0.f;
	TWeakObjectPtr<UFixHimKeepsakeWidget> Self(this);

	UTextBlock* Title = MakeText(WidgetTree, TEXT("You fixed him."), 44, HotPink, TEXT("Bold"));
	Title->SetJustification(ETextJustify::Center);
	Content->AddChildToVerticalBox(Title)->SetHorizontalAlignment(HAlign_Center);

	FString Names;
	for (int32 i = 0; i < Entries.Num(); ++i)
	{
		Names += (i == 0 ? TEXT("") : (i == Entries.Num() - 1 ? TEXT(" and ") : TEXT(", "))) + Entries[i].Name;
	}
	UTextBlock* Sub = MakeText(WidgetTree, FString::Printf(TEXT("...and somewhere along the way, you fell for %s."), *Names), 20, Plum, TEXT("Italic"));
	Sub->SetJustification(ETextJustify::Center);
	Content->AddChildToVerticalBox(Sub)->SetPadding(FMargin(0.f, 6.f, 0.f, 22.f));

	for (int32 i = 0; i < Entries.Num(); ++i)
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetHeightOverride(58.f);
		Box->SetWidthOverride(360.f);
		Box->AddChild(UFixHimButton::Make(WidgetTree, FString::Printf(TEXT("See %s"), *Entries[i].Name), [Self, i]() { if (Self.IsValid()) { Self->ShowPortrait(i); } }, 22, true));
		UVerticalBoxSlot* BoxSlot = Content->AddChildToVerticalBox(Box);
		BoxSlot->SetHorizontalAlignment(HAlign_Center);
		BoxSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 10.f));
	}

	USizeBox* Back = WidgetTree->ConstructWidget<USizeBox>();
	Back->SetHeightOverride(52.f);
	Back->SetWidthOverride(360.f);
	Back->AddChild(UFixHimButton::Make(WidgetTree, TEXT("Return to title"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->FinishGame(); } }, 20, false));
	UVerticalBoxSlot* BackSlot = Content->AddChildToVerticalBox(Back);
	BackSlot->SetHorizontalAlignment(HAlign_Center);
	BackSlot->SetPadding(FMargin(0.f, 12.f, 0.f, 0.f));
}

void UFixHimKeepsakeWidget::ShowPortrait(int32 Index)
{
	if (!Entries.IsValidIndex(Index))
	{
		return;
	}
	const FFixHimKeepsakeEntry& E = Entries[Index];
	Content->ClearChildren();
	Age = 0.f;
	TWeakObjectPtr<UFixHimKeepsakeWidget> Self(this);

	UTextBlock* Name = MakeText(WidgetTree, E.Name.ToUpper(), 40, HotPink, TEXT("Bold"));
	Name->SetJustification(ETextJustify::Center);
	Content->AddChildToVerticalBox(Name)->SetHorizontalAlignment(HAlign_Center);

	if (!KeepsakeTarget)
	{
		KeepsakeTarget = NewObject<UTextureRenderTarget2D>(this);
		KeepsakeTarget->RenderTargetFormat = RTF_RGBA16f;
		KeepsakeTarget->ClearColor = FLinearColor(0.f, 0.f, 0.f, 1.f);
		KeepsakeTarget->InitAutoFormat(1024, 1024);
	}
	if (AFixHimHunk* Hunk = E.Hunk.Get())
	{
		Hunk->CaptureKeepsake(KeepsakeTarget);
	}

	USizeBox* ImgBox = WidgetTree->ConstructWidget<USizeBox>();
	ImgBox->SetWidthOverride(620.f);
	ImgBox->SetHeightOverride(620.f);
	UBorder* Frame = WidgetTree->ConstructWidget<UBorder>();
	Frame->SetBrush(Rounded(Plum, 24.f, HotPink, 5.f));
	Frame->SetPadding(FMargin(8.f));
	ImgBox->AddChild(Frame);
	UImage* Img = WidgetTree->ConstructWidget<UImage>();
	if (UMaterialInterface* Mat = UFixHimSettings::Get()->PortraitMaterial.LoadSynchronous())
	{
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Mat, this);
		MID->SetTextureParameterValue(TEXT("Portrait"), KeepsakeTarget);
		MID->SetScalarParameterValue(TEXT("Silhouette"), 0.f);
		MID->SetScalarParameterValue(TEXT("Transparent"), 0.f);
		Img->SetBrushFromMaterial(MID);
	}
	else
	{
		Img->SetBrushResourceObject(KeepsakeTarget);
	}
	Frame->SetContent(Img);
	Content->AddChildToVerticalBox(ImgBox)->SetPadding(FMargin(0.f, 10.f));

	UTextBlock* Ending = MakeText(WidgetTree, E.EndingTitle, 22, Plum, TEXT("Italic"));
	Ending->SetJustification(ETextJustify::Center);
	Content->AddChildToVerticalBox(Ending)->SetHorizontalAlignment(HAlign_Center);

	UHorizontalBox* Buttons = WidgetTree->ConstructWidget<UHorizontalBox>();
	UVerticalBoxSlot* BSlot = Content->AddChildToVerticalBox(Buttons);
	BSlot->SetHorizontalAlignment(HAlign_Center);
	BSlot->SetPadding(FMargin(0.f, 16.f, 0.f, 0.f));
	auto Add = [&](const FString& Label, TFunction<void()> Fn, bool bPrimary)
	{
		USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
		Box->SetHeightOverride(52.f);
		Box->SetWidthOverride(240.f);
		Box->AddChild(UFixHimButton::Make(WidgetTree, Label, MoveTemp(Fn), 20, bPrimary));
		Buttons->AddChildToHorizontalBox(Box)->SetPadding(FMargin(8.f, 0.f));
	};
	if (Entries.Num() > 1)
	{
		Add(TEXT("Back"), [Self]() { if (Self.IsValid()) { Self->ShowChooser(); } }, false);
	}
	Add(TEXT("Return to title"), [Self]() { if (Self.IsValid() && Self->GetFixHimPC()) { Self->GetFixHimPC()->FinishGame(); } }, true);
}

void UFixHimKeepsakeWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Age += InDeltaTime;
	if (Card)
	{
		Card->SetRenderScale(FVector2D(FMath::Max(0.01f, EaseOutBack(Age / 0.5f))));
	}
}
