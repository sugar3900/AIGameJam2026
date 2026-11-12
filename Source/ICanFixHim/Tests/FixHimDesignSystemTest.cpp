#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "UI/FixHimDesignReview.h"
#include "UI/FixHimMenus.h"
#include "UI/FixHimDialogueWidget.h"
#include "UI/FixHimDayWidgets.h"
#include "UI/FixHimCards.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/Font.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Components/SizeBox.h"
#include "Slate/WidgetRenderer.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/Layout/SBox.h"
#include "ImageUtils.h"
#include "Serialization/BufferArchive.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Json.h"
#include "RHI.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#endif

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFixHimDesignSystemTest,"FixHim.UI.DesignSystem",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FFixHimDesignSystemTest::RunTest(const FString& Parameters)
{
 UWorld* World=UWorld::CreateWorld(EWorldType::Game,false);
 auto& Context=GEngine->CreateNewWorldContext(EWorldType::Game); Context.SetCurrentWorld(World);
 UGameInstance* GI=NewObject<UGameInstance>(); World->SetGameInstance(GI); GI->Init();
 auto* Save=GI->GetSubsystem<UFixHimSaveSubsystem>();
 Save->Options().bReducedMotion=true;
 // Font asset import and cooked object references must work; silently falling back isn't acceptable.
 const auto BodyFont=FixHimUI::Font(22);
 const auto* Font=Cast<UFont>(BodyFont.FontObject);
 TestTrue(TEXT("Imported Barlow regular and semibold loaded"),Font && Font->GetCompositeFont()->DefaultTypeface.Fonts.Num()==2);
 const auto* Display=Cast<UFont>(FixHimUI::Font(36,TEXT("Display")).FontObject);
 TestTrue(TEXT("Imported Barlow Condensed display loaded"),Display && Display->GetCompositeFont()->DefaultTypeface.Fonts.Num()==1);
 FString Json;
 FFileHelper::LoadFileToString(Json,*(FPaths::ProjectDir()/TEXT("Art Source/UI Concepts/Exploration 02/dialogue-stress-cases.json")));
 TSharedPtr<FJsonObject> Fixtures;
 TestTrue(TEXT("Authored dialogue stress fixtures load"),FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json),Fixtures));
 if(!Fixtures) return false;
 const FString LongLine=Fixtures->GetArrayField(TEXT("longestLines"))[0]->AsObject()->GetStringField(TEXT("text"));
 const FString LongReply=TEXT("Because somebody loved it. And because I love it. All of it. Including the part that argues.");
 const FString Output=FPaths::ProjectSavedDir()/TEXT("DesignSystem/Review");
 IFileManager::Get().MakeDirectory(*Output,true);
 auto Render=[&](UFixHimWidget* W,const FString& Name,FVector2D Physical,FVector2D Logical)
 {
  auto Slate=W->TakeWidget();
#if WITH_EDITOR
  FAssetCompilingManager::Get().FinishAllCompilation();
#endif
  if(GUsingNullRHI) return;
  auto Scaled=SNew(SScaleBox).Stretch(EStretch::ScaleToFit)[SNew(SBox).WidthOverride(Logical.X).HeightOverride(Logical.Y)[Slate]];
  FWidgetRenderer Renderer(true);
  UTextureRenderTarget2D* RT=FWidgetRenderer::CreateTargetFor(Physical,TF_Bilinear,true);
  // Auto-wrapped text invalidates its desired size after the first paint. Settle the real layout,
  // just as several frames do in the game, before checking or exporting it.
  for(int Frame=0;Frame<6;++Frame)
  {
   Scaled->SlatePrepass(1.f);
   Renderer.DrawWidget(RT,Scaled,Physical,0.016f);
   FlushRenderingCommands();
  }
  TArray<FColor> Pixels;
  FReadSurfaceDataFlags ReadFlags(RCM_MinMax); ReadFlags.SetLinearToGamma(false);
  TestTrue(TEXT("Read gamma-corrected Slate pixels without a second gamma conversion"),RT->GameThread_GetRenderTargetResource()->ReadPixels(Pixels,ReadFlags));
  if(Name==TEXT("01-components-1080p"))
  {
   const FColor Sample=Pixels[400*RT->SizeX+1400];
   const FColor Expected=FColor::FromHex(TEXT("FFF5E5"));
   TestTrue(*FString::Printf(TEXT("Captured cream matches sRGB token (got %s)"),*Sample.ToString()),FMath::Abs(int(Sample.R)-Expected.R)<5 && FMath::Abs(int(Sample.G)-Expected.G)<5 && FMath::Abs(int(Sample.B)-Expected.B)<5);
  }
  TArray64<uint8> Bytes;
  FImageUtils::PNGCompressImageArray(RT->SizeX,RT->SizeY,Pixels,Bytes);
  TestTrue(*FString::Printf(TEXT("%s PNG saved"),*Name),FFileHelper::SaveArrayToFile(Bytes,*(Output/Name+TEXT(".png"))));
  W->WidgetTree->ForEachWidget([&](UWidget* Node)
  {
   if(auto* Text=Cast<UTextBlock>(Node))
   {
    TestTrue(TEXT("All text retains a nonzero size"),Text->GetFont().Size>0);
    bool Visible=Text->IsVisible();
    for(UWidget* Parent=Text->GetParent();Parent;Parent=Parent->GetParent()) Visible &= Parent->IsVisible();
    const auto Allocated=Text->GetCachedGeometry().GetLocalSize();
    if(Visible && Allocated.Y>1)
    {
     TestTrue(*FString::Printf(TEXT("%s: text height fits (%s, desired %.1f / allocated %.1f)"),*Name,*Text->GetText().ToString().Left(32),Text->GetDesiredSize().Y,Allocated.Y),Text->GetDesiredSize().Y<=Allocated.Y+1);
    }
   }
  });
 };
 auto Make=[&]<typename T>(){T* W=NewObject<T>(World); W->Initialize(); return W;};
 auto* Workshop=Make.template operator()<UFixHimDesignReviewWidget>();
 Render(Workshop,TEXT("01-components-1080p"),{1920,1080},{1920,1080});
 auto* Pause=Make.template operator()<UFixHimPauseWidget>();
 Render(Pause,TEXT("02-pause-720p"),{1280,720},{1920,1080});
 auto* Options=Make.template operator()<UFixHimOptionsWidget>();
 Render(Options,TEXT("03-options-1080p"),{1920,1080},{1920,1080});
 auto* Dialogue=Make.template operator()<UFixHimDialogueWidget>(); Dialogue->TakeWidget();
 FDialogueView View; View.HunkName=TEXT("TYLER"); View.Speaker=EDialogueSpeaker::Hunk;
 View.Text=TEXT("The tile remembers things. Don't ask me how. A girl had chicken pox in that tub in 1964 and counted every tile. A man hid an engagement ring in the soap dish in 1979. A girl dyed her hair pink in that sink in 1994. Kool-Aid. Good instincts.");
 View.Choices={LongReply,TEXT("I want to know who you were before the house. If you want to tell me."),TEXT("You can love a place and still want to leave it."),TEXT("Let's fix this together.")};
 Dialogue->ShowView(View); Dialogue->TryCompleteTyping();
 Render(Dialogue,TEXT("04-dialogue-four-replies"),{1920,1080},{1920,1080});
 // Assert real authored copy survives both the typewriter and the rendered choices.
 bool FoundReply=false; int32 ReplyCount=0;
 Dialogue->WidgetTree->ForEachWidget([&](UWidget* W)
 {
  if(auto* B=Cast<UFixHimButton>(W);B && B->bDesignSurface && B->Label)
  { ++ReplyCount; FoundReply |= B->Label->GetText().ToString().Contains(LongReply); }
 });
 TestEqual(TEXT("Four simultaneously visible complete replies"),ReplyCount,4);
 TestTrue(TEXT("Longest reply is never truncated"),FoundReply);
 View.Text=LongLine; View.Speaker=EDialogueSpeaker::Narration; View.Choices.Reset();
 Dialogue->ShowView(View); Dialogue->TryCompleteTyping();
 Render(Dialogue,TEXT("05-long-narration-ultrawide"),{2560,1080},{2560,1080});
 Save->Options().UITextScale=1.35f;
 auto* Large=Make.template operator()<UFixHimOptionsWidget>();
 Render(Large,TEXT("06-large-text-options"),{1920,1080},{1920,1080});
 auto* LargeDialogue=Make.template operator()<UFixHimDialogueWidget>(); LargeDialogue->TakeWidget();
 View.Choices={LongReply,LongReply,LongReply,LongReply}; LargeDialogue->ShowView(View); LargeDialogue->TryCompleteTyping();
 Render(LargeDialogue,TEXT("07-large-text-dialogue-720p"),{1280,720},{1920,1080});
 Save->Options().UITextScale=1.f;
 auto* Title=Make.template operator()<UFixHimTitleWidget>();
 Render(Title,TEXT("08-title-1440p"),{2560,1440},{1920,1080});
 auto* Name=Make.template operator()<UFixHimNameEntryWidget>();
 Render(Name,TEXT("09-name-entry"),{1920,1080},{1920,1080});
 auto* Door=Make.template operator()<UFixHimDoorPromptWidget>();
 Render(Door,TEXT("10-end-day-confirmation"),{1920,1080},{1920,1080});
 auto* Credits=Make.template operator()<UFixHimCreditsWidget>();
 Render(Credits,TEXT("11-credits"),{1920,1080},{1920,1080});
 GI->Shutdown(); World->DestroyWorld(false); GEngine->DestroyWorldContext(World);
 return true;
}
#endif
