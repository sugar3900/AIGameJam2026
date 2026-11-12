#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "UI/FixHimDesignReview.h"
#include "UI/FixHimMenus.h"
#include "UI/FixHimDialogueWidget.h"
#include "UI/FixHimDayWidgets.h"
#include "UI/FixHimCards.h"
#include "UI/FixHimFloorPlanWidget.h"
#include "UI/FixHimHUDWidget.h"
#include "Framework/Application/SlateApplication.h"
#include "Widgets/SWindow.h"
#include "Components/EditableTextBox.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/Font.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Components/SizeBox.h"
#include "Components/Image.h"
#include "Engine/Texture2D.h"
#include "Slate/WidgetRenderer.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Styling/CoreStyle.h"
#include "ImageUtils.h"
#include "ImageCore.h"
#include "Serialization/BufferArchive.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Json.h"
#include "RHI.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#endif

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFixHimDesignSystemTest, "FixHim.UI.DesignSystem",
                                 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FFixHimDesignSystemTest::RunTest(const FString &Parameters)
{
	UWorld *World = UWorld::CreateWorld(EWorldType::Game, false);
	auto &Context = GEngine->CreateNewWorldContext(EWorldType::Game);
	Context.SetCurrentWorld(World);
	UGameInstance *GI = NewObject<UGameInstance>();
	World->SetGameInstance(GI);
	GI->Init();
	auto *Save = GI->GetSubsystem<UFixHimSaveSubsystem>();
	Save->Options().bReducedMotion = true;
	// Font asset import and cooked object references must work; silently falling back isn't acceptable.
	const auto BodyFont = FixHimUI::Font(22);
	const auto *Font = Cast<UFont>(BodyFont.FontObject);
	TestTrue(TEXT("Imported Barlow regular and semibold loaded"),
	         Font && Font->GetCompositeFont()->DefaultTypeface.Fonts.Num() == 2);
	const auto *Display = Cast<UFont>(FixHimUI::Font(36, TEXT("Display")).FontObject);
	TestTrue(TEXT("Imported Barlow Condensed display loaded"),
	         Display && Display->GetCompositeFont()->DefaultTypeface.Fonts.Num() == 1);
	FString Json;
	FFileHelper::LoadFileToString(
	    Json, *(FPaths::ProjectDir() / TEXT("Art Source/UI Concepts/Exploration 02/dialogue-stress-cases.json")));
	TSharedPtr<FJsonObject> Fixtures;
	TestTrue(TEXT("Authored dialogue stress fixtures load"),
	         FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Fixtures));
	if (!Fixtures)
		return false;
	const FString LongLine = Fixtures->GetArrayField(TEXT("longestLines"))[0]->AsObject()->GetStringField(TEXT("text"));
	const FString LongReply =
	    TEXT("Because somebody loved it. And because I love it. All of it. Including the part that argues.");
	const FString Output = FPaths::ProjectSavedDir() / TEXT("DesignSystem/Review");
	IFileManager::Get().MakeDirectory(*Output, true);
	auto Render = [&](UFixHimWidget *W, const FString &Name, FVector2D Physical, FVector2D Logical) {
		auto Slate = W->TakeWidget();
		W->bInitialFocus = true; // Rendering fixtures must not activate an OS input context in a virtual window.
#if WITH_EDITOR
		FAssetCompilingManager::Get().FinishAllCompilation();
#endif
		if (GUsingNullRHI)
			return;
		auto Scaled = SNew(SScaleBox).Stretch(
		    EStretch::ScaleToFit)[SNew(SBox).WidthOverride(Logical.X).HeightOverride(Logical.Y)[Slate]];
		// Render in linear HDR, then let ImageCore encode PNG as sRGB exactly once.
		// The default BGRA8 render target reports ambiguous gamma on UE 5.8/macOS.
		FWidgetRenderer Renderer(false);
		UTextureRenderTarget2D *RT = NewObject<UTextureRenderTarget2D>();
		RT->ClearColor = FLinearColor::Transparent;
		RT->InitCustomFormat(int32(Physical.X), int32(Physical.Y), PF_FloatRGBA, true);
		RT->UpdateResourceImmediate(true);
		// Auto-wrapped text invalidates its desired size after the first paint. Settle the real layout,
		// just as several frames do in the game, before checking or exporting it.
		for (int Frame = 0; Frame < 6; ++Frame)
		{
			W->NativeTick(FGeometry::MakeRoot(Logical, FSlateLayoutTransform()), .2f);
			Scaled->SlatePrepass(1.f);
			Renderer.DrawWidget(RT, Scaled, Physical, 0.016f);
			FlushRenderingCommands();
		}
		FImage LinearImage, EncodedImage;
		TestTrue(TEXT("Read linear HDR widget image"), FImageUtils::GetRenderTargetImage(RT, LinearImage));
		LinearImage.CopyTo(EncodedImage, ERawImageFormat::BGRA8, EGammaSpace::sRGB);
		const auto Pixels = EncodedImage.AsBGRA8();
		if (Name == TEXT("01-components-1080p"))
		{
			const FColor Sample = Pixels[400 * RT->SizeX + 1400];
			const FColor Expected = FColor::FromHex(TEXT("FFF5E5"));
			TestTrue(*FString::Printf(TEXT("Captured cream matches sRGB token (got %s)"), *Sample.ToString()),
			         FMath::Abs(int(Sample.R) - Expected.R) < 5 && FMath::Abs(int(Sample.G) - Expected.G) < 5 &&
			             FMath::Abs(int(Sample.B) - Expected.B) < 5);
		}
		TArray64<uint8> Bytes;
		FImageUtils::CompressImage(Bytes, TEXT("PNG"), EncodedImage);
		TestTrue(*FString::Printf(TEXT("%s PNG saved"), *Name),
		         FFileHelper::SaveArrayToFile(Bytes, *(Output / Name + TEXT(".png"))));
		W->WidgetTree->ForEachWidget([&](UWidget *Node) {
			if (auto *Text = Cast<UTextBlock>(Node))
			{
				TestTrue(TEXT("All text retains a nonzero size"), Text->GetFont().Size > 0);
				bool Visible = Text->IsVisible();
				for (UWidget *Parent = Text->GetParent(); Parent; Parent = Parent->GetParent())
					Visible &= Parent->IsVisible();
				const auto Allocated = Text->GetCachedGeometry().GetLocalSize();
				if (Visible && Allocated.Y > 1)
				{
					TestTrue(*FString::Printf(TEXT("%s: text height fits (%s, desired %.1f / allocated %.1f)"), *Name,
					                          *Text->GetText().ToString().Left(32), Text->GetDesiredSize().Y,
					                          Allocated.Y),
					         Text->GetDesiredSize().Y <= Allocated.Y + 1);
				}
			}
		});
	};
	auto Make = [&]<typename T>() {
		T *W = NewObject<T>(World);
		W->Initialize();
		return W;
	};
	auto *Workshop = Make.template operator()<UFixHimDesignReviewWidget>();
	Render(Workshop, TEXT("01-components-1080p"), {1920, 1080}, {1920, 1080});
	auto *Pause = Make.template operator()<UFixHimPauseWidget>();
	Render(Pause, TEXT("02-pause-720p"), {1280, 720}, {1920, 1080});
	UTextBlock *CachedText = nullptr;
	Pause->WidgetTree->ForEachWidget([&](UWidget *W) {
		if (!CachedText)
			CachedText = Cast<UTextBlock>(W);
	});
	if (TestNotNull(TEXT("Cached pause contains text"), CachedText))
	{
		const int32 Original = CachedText->GetFont().Size;
		Save->Options().UITextScale = 1.35f;
		static_cast<UFixHimWidget *>(Pause)->NativeConstruct();
		TestEqual(TEXT("Reopening a cached screen applies enlarged text"), int32(CachedText->GetFont().Size),
		          FMath::RoundToInt(Original * 1.35f));
		Save->Options().UITextScale = 1.f;
		static_cast<UFixHimWidget *>(Pause)->NativeConstruct();
		TestEqual(TEXT("Returning to 100% restores authored size exactly"), int32(CachedText->GetFont().Size), Original);
	}
	auto *Options = Make.template operator()<UFixHimOptionsWidget>();
	Render(Options, TEXT("03-options-1080p"), {1920, 1080}, {1920, 1080});
	auto *Dialogue = Make.template operator()<UFixHimDialogueWidget>();
	Dialogue->TakeWidget();
	FDialogueView View;
	View.HunkName = TEXT("TYLER");
	View.Speaker = EDialogueSpeaker::Hunk;
	View.Text = TEXT("The tile remembers things. Don't ask me how. A girl had chicken pox in that tub in 1964 and "
	                 "counted every tile. A man hid an engagement ring in the soap dish in 1979. A girl dyed her hair "
	                 "pink in that sink in 1994. Kool-Aid. Good instincts.");
	View.Choices = {LongReply, TEXT("I want to know who you were before the house. If you want to tell me."),
	                TEXT("You can love a place and still want to leave it."), TEXT("Let's fix this together.")};
	Dialogue->ShowView(View);
	Dialogue->TryCompleteTyping();
	bool SetPaintedPortrait = false;
	Dialogue->WidgetTree->ForEachWidget([&](UWidget *Child) {
		if (auto *Image = Cast<UImage>(Child); Image && !SetPaintedPortrait)
		{
			auto *Texture = LoadObject<UTexture2D>(
			    nullptr, TEXT("/Game/ICanFixHim/UI/Portraits/T_Portrait_Tyler.T_Portrait_Tyler"));
			TestNotNull(TEXT("Real Tyler review portrait loads"), Texture);
			Image->SetBrushFromTexture(Texture);
			SetPaintedPortrait = true;
		}
	});
	Render(Dialogue, TEXT("04-dialogue-four-replies"), {1920, 1080}, {1920, 1080});
	// Assert real authored copy survives both the typewriter and the rendered choices.
	bool FoundReply = false;
	int32 ReplyCount = 0;
	Dialogue->WidgetTree->ForEachWidget([&](UWidget *W) {
		if (auto *B = Cast<UFixHimButton>(W); B && B->bDesignSurface && B->Label)
		{
			++ReplyCount;
			FoundReply |= B->Label->GetText().ToString().Contains(LongReply);
		}
	});
	TestEqual(TEXT("Four simultaneously visible complete replies"), ReplyCount, 4);
	TestTrue(TEXT("Longest reply is never truncated"), FoundReply);
	View.Text = LongLine;
	View.Speaker = EDialogueSpeaker::Narration;
	View.Choices.Reset();
	Dialogue->ShowView(View);
	Dialogue->TryCompleteTyping();
	Render(Dialogue, TEXT("05-long-narration-ultrawide"), {2560, 1080}, {2560, 1080});
	Save->Options().UITextScale = 1.35f;
	Save->Options().TextSpeed = 4.f;
	auto *Large = Make.template operator()<UFixHimOptionsWidget>();
	Render(Large, TEXT("06-large-text-options"), {1920, 1080}, {1920, 1080});
	auto *LargeDialogue = Make.template operator()<UFixHimDialogueWidget>();
	LargeDialogue->TakeWidget();
	View.Choices = {LongReply, LongReply, LongReply, LongReply};
	LargeDialogue->ShowView(View);
	LargeDialogue->TryCompleteTyping();
	Render(LargeDialogue, TEXT("07-large-text-dialogue-720p"), {1280, 720}, {1920, 1080});
	auto *LargeTitle = Make.template operator()<UFixHimTitleWidget>();
	Render(LargeTitle, TEXT("19-large-text-title"), {1920, 1080}, {1920, 1080});
	Save->Options().UITextScale = 1.f;
	auto *Title = Make.template operator()<UFixHimTitleWidget>();
	Render(Title, TEXT("08-title-1440p"), {2560, 1440}, {1920, 1080});
	auto *Name = Make.template operator()<UFixHimNameEntryWidget>();
	Render(Name, TEXT("09-name-entry"), {1920, 1080}, {1920, 1080});
	auto *Door = Make.template operator()<UFixHimDoorPromptWidget>();
	Render(Door, TEXT("10-end-day-confirmation"), {1920, 1080}, {1920, 1080});
	auto *Credits = Make.template operator()<UFixHimCreditsWidget>();
	Render(Credits, TEXT("11-credits"), {1920, 1080}, {1920, 1080});
	// The screen's native navigation must skip a disabled action and wrap in both directions.
	if (FSlateApplication::IsInitialized() && !GUsingNullRHI)
	{
		auto Window = SNew(SWindow).ClientSize(FVector2D(1920, 1080)).FocusWhenFirstShown(false);
		Window->SetContent(Pause->TakeWidget());
		FSlateApplication::Get().AddWindow(Window, true);
		FSlateApplication::Get().Tick();
		TArray<UFixHimButton *> Actions;
		Pause->WidgetTree->ForEachWidget([&](UWidget *W) {
			if (auto *B = Cast<UFixHimButton>(W))
				Actions.Add(B);
		});
		if (TestEqual(TEXT("Pause navigation has three actions"), Actions.Num(), 3))
		{
			Actions[1]->SetIsEnabled(false);
			Actions[0]->SetKeyboardFocus();
			const FKeyEvent Down(EKeys::Down, FModifierKeysState(), 0, false, 0, 0);
			static_cast<UFixHimWidget *>(Pause)->NativeOnKeyDown(FGeometry(), Down);
			TestTrue(TEXT("Keyboard skips disabled Options"), Actions[2]->HasKeyboardFocus());
			static_cast<UFixHimWidget *>(Pause)->NativeOnKeyDown(FGeometry(), Down);
			TestTrue(TEXT("Keyboard wraps to Resume"), Actions[0]->HasKeyboardFocus());
			const FKeyEvent Up(EKeys::Gamepad_DPad_Up, FModifierKeysState(), 0, false, 0, 0);
			static_cast<UFixHimWidget *>(Pause)->NativeOnKeyDown(FGeometry(), Up);
			TestTrue(TEXT("Gamepad D-pad wraps backwards"), Actions[2]->HasKeyboardFocus());
		}
		int32 Activations = 0;
		Actions[0]->Init([&Activations]() { ++Activations; });
		Actions[0]->SetKeyboardFocus();
		const FKeyEvent Accept(EKeys::Gamepad_FaceButton_Bottom, FModifierKeysState(), 0, false, 0, 0);
		Actions[0]->GetCachedWidget()->OnKeyDown(FGeometry(), Accept);
		Actions[0]->GetCachedWidget()->OnKeyUp(FGeometry(), Accept);
		TestEqual(TEXT("Gamepad accept activates exactly once"), Activations, 1);
		// macOS IME activation requires a real native window. The native run covers this;
		// offscreen captures test the same controls without trying to activate the OS input context.
		if (!FParse::Param(FCommandLine::Get(), TEXT("RenderOffscreen")))
		{
			Window->SetContent(Name->TakeWidget());
			FSlateApplication::Get().Tick();
			UEditableTextBox *Field = nullptr;
			UFixHimButton *BackAction = nullptr;
			Name->WidgetTree->ForEachWidget([&](UWidget *W) {
				if (auto *E = Cast<UEditableTextBox>(W))
					Field = E;
				if (auto *B = Cast<UFixHimButton>(W); B && B->Label && B->Label->GetText().ToString() == TEXT("Back"))
					BackAction = B;
			});
			if (TestNotNull(TEXT("Name field participates in navigation"), Field) &&
			    TestNotNull(TEXT("Name Back action"), BackAction))
			{
				Field->SetKeyboardFocus();
				const FKeyEvent Tab(EKeys::Tab, FModifierKeysState(), 0, false, 0, 0);
				static_cast<UFixHimWidget *>(Name)->NativeOnKeyDown(FGeometry(), Tab);
				TestTrue(TEXT("Tab leaves name field and skips disabled Move in"), BackAction->HasKeyboardFocus());
				const FKeyEvent Previous(EKeys::Up, FModifierKeysState(), 0, false, 0, 0);
				static_cast<UFixHimWidget *>(Name)->NativeOnKeyDown(FGeometry(), Previous);
				TestTrue(TEXT("Navigation can return to editable name field"), Field->HasKeyboardFocus());
			}
		}

		FSlateApplication::Get().ClearKeyboardFocus();
		Window->RequestDestroyWindow();
	}
	auto *Radio = Make.template operator()<UFixHimRadioWidget>();
	Radio->TakeWidget();
	FDialogueNode Episode;
	FDialogueLine RadioLine;
	RadioLine.Speaker = EDialogueSpeaker::Named;
	RadioLine.SpeakerName = TEXT("BEV");
	RadioLine.Text = TEXT("Four weeks to turn this condemned house around. The wiring is unreliable, the plumbing has "
	                      "opinions, and someone appears to be living in the closet. Welcome home, Rosie.");
	Episode.Lines.Add(RadioLine);
	Radio->Play(TEXT("BEV & TRISH"), Episode, [] {});
	Render(Radio, TEXT("12-radio-caption"), {1920, 1080}, {1920, 1080});
	auto *Intro = Make.template operator()<UFixHimIntroCardWidget>();
	Intro->TakeWidget();
	FHunkDefinition Def;
	Def.Id = TEXT("tyler");
	Def.Name = TEXT("Tyler");
	Def.Malady = TEXT("Pink bathroom tile");
	Def.Tagline = TEXT("Some things deserve to stay pink.");
	Def.Portrait = TEXT("/Game/ICanFixHim/UI/Portraits/T_Portrait_Tyler.T_Portrait_Tyler");
	Intro->Setup(Def, nullptr, [] {});
	static_cast<UFixHimWidget *>(Intro)->NativeTick(FGeometry::MakeRoot(FVector2D(1920, 1080), FSlateLayoutTransform()),
	                                                1.f);
	Render(Intro, TEXT("13-character-introduction"), {1920, 1080}, {1920, 1080});
	auto *Ending = Make.template operator()<UFixHimEndingCardWidget>();
	Ending->TakeWidget();
	FHunkEnding EndingData;
	EndingData.Title = TEXT("A little rough around the edges");
	EndingData.Text = LongReply;
	Def.Endings.Add(TEXT("friend_success"), EndingData);
	Ending->Setup(Def, TEXT("friend_success"), 2, 4);
	Render(Ending, TEXT("14-ending-card"), {1920, 1080}, {1920, 1080});
	auto *Transition = Make.template operator()<UFixHimTransitionWidget>();
	Transition->TakeWidget();
	Transition->Play(TEXT("WEEK TWO"), TEXT("A fresh coat. A fresh start."), true, true, [] {}, [] {});
	Render(Transition, TEXT("15-week-transition"), {1920, 1080}, {1920, 1080});
	auto *Keepsake = Make.template operator()<UFixHimKeepsakeWidget>();
	Keepsake->TakeWidget();
	FFixHimKeepsakeEntry Entry;
	Entry.HunkId = TEXT("tyler");
	Entry.Name = TEXT("Tyler");
	Entry.EndingTitle = EndingData.Title;
	Keepsake->Setup({Entry});
	Render(Keepsake, TEXT("16-keepsake-chooser"), {1920, 1080}, {1920, 1080});
	auto *HUD = Make.template operator()<UFixHimHUDWidget>();
	HUD->TakeWidget();
	HUD->SetRoomName(FText::FromString(TEXT("LIVING ROOM")));
	HUD->SetRepairs(2, 4, 2, 4);
	HUD->SetReticle(true, EFixHimInteractionAction::Talk, FText::FromString(TEXT("Talk to Wyatt")));
	HUD->ShowToast(TEXT("A little less broken."), 4.f, false);
	Render(HUD, TEXT("17-hud-labels"), {1920, 1080}, {1920, 1080});
	// Every audited authored exchange is also rendered unshortened, including active topic links.
	int32 FixtureIndex = 0;
	for (const auto &Value : Fixtures->GetArrayField(TEXT("fixtures")))
	{
		const auto Case = Value->AsObject();
		const FString Script = Case->GetStringField(TEXT("script"));
		View.HunkName = Script.ToUpper();
		View.Speaker = FixtureIndex == 0 ? EDialogueSpeaker::Narration : EDialogueSpeaker::Hunk;
		View.Text = Case->GetStringField(FixtureIndex == 0 ? TEXT("displayText") : TEXT("rawLine"));
		View.Choices.Reset();
		for (const auto &Choice : Case->GetArrayField(TEXT("choices")))
			View.Choices.Add(Choice->AsObject()->GetStringField(TEXT("text")));
		View.ActiveTopics = {TEXT("pox"), TEXT("mudset"), TEXT("bonjovi")};
		Dialogue->ShowView(View);
		Dialogue->TryCompleteTyping();
		const FString PortraitName = Script.Left(1).ToUpper() + Script.Mid(1);
		bool Assigned = false;
		Dialogue->WidgetTree->ForEachWidget([&](UWidget *W) {
			if (auto *Image = Cast<UImage>(W); Image && !Assigned)
			{
				const FString Path = FString::Printf(TEXT("/Game/ICanFixHim/UI/Portraits/T_Portrait_%s.T_Portrait_%s"),
				                                     *PortraitName, *PortraitName);
				Image->SetBrushFromTexture(LoadObject<UTexture2D>(nullptr, *Path));
				Assigned = true;
			}
		});
		Render(Dialogue, FString::Printf(TEXT("18-authored-case-%02d"), ++FixtureIndex), {1920, 1080}, {1920, 1080});
	}

	GI->Shutdown();
	World->DestroyWorld(false);
	GEngine->DestroyWorldContext(World);
	return true;
}
#endif
