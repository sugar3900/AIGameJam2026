// Run: -ExecCmds="Automation RunTests FixHim.UI.Reticles" -TestExit="Automation Test Queue Empty"
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/Texture2D.h"
#include "Core/FixHimSaveSubsystem.h"
#include "World/FixHimBed.h"
#include "World/FixHimDoor.h"
#include "World/FixHimMalady.h"
#include "UI/FixHimHUDWidget.h"
#include "Components/Image.h"
#include "Components/Border.h"
#include "Components/TextBlock.h"
#include "Components/SizeBox.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFixHimReticlesTest, "FixHim.UI.Reticles",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FFixHimReticlesTest::RunTest(const FString& Parameters)
{
	// An isolated world and in-memory progress: never load or write the player's save.
	UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
	UGameInstance* GI = NewObject<UGameInstance>();
	World->SetGameInstance(GI);
	GI->Init();
	auto* Prop = World->SpawnActor<AFixHimInteractable>();
	auto* Bed = World->SpawnActor<AFixHimBed>();
	auto* Door = World->SpawnActor<AFixHimDoor>();
	auto* Malady = World->SpawnActor<AFixHimMalady>();
	TestEqual(TEXT("Ordinary controls use/open"), Prop->GetInteractionAction(), EFixHimInteractionAction::Use);
	Prop->PromptOff = FText::FromString(TEXT("Localized label unrelated to action"));
	TestEqual(TEXT("Prompt text never classifies action"), Prop->GetInteractionAction(), EFixHimInteractionAction::Use);
	TestEqual(TEXT("Bed opens end-day confirmation"), Bed->GetInteractionAction(), EFixHimInteractionAction::EndDay);
	TestEqual(TEXT("Exit opens end-day confirmation"), Door->GetInteractionAction(), EFixHimInteractionAction::EndDay);
	TestEqual(TEXT("Unmet malady inspects"), Malady->GetInteractionAction(), EFixHimInteractionAction::Inspect);
	UFixHimSaveSubsystem* Save = GI->GetSubsystem<UFixHimSaveSubsystem>();
	if (TestNotNull(TEXT("In-memory save subsystem"), Save))
	{
		Save->Hunk(Malady->HunkId).bMet = true;
		TestEqual(TEXT("Met malady talks"), Malady->GetInteractionAction(), EFixHimInteractionAction::Talk);
		Save->Hunk(Malady->HunkId).bMet = false;
		TestEqual(TEXT("Progress change refreshes action"), Malady->GetInteractionAction(), EFixHimInteractionAction::Inspect);
	}
	Prop->bEnabled = false;
	TestFalse(TEXT("Disabled targets still filtered"), Prop->CanInteract());

	auto* HUD = NewObject<UFixHimHUDWidget>();
	HUD->Initialize();
	HUD->TakeWidget();
	TestEqual(TEXT("Only five runtime textures; unavailable reserved"), HUD->ReticleTextures.Num(), 5);
	for (auto Action : { EFixHimInteractionAction::Inspect, EFixHimInteractionAction::Talk,
		EFixHimInteractionAction::Use, EFixHimInteractionAction::EndDay, EFixHimInteractionAction::None })
	{
		auto* Texture = HUD->ReticleTextures.FindRef(Action).Get();
		TestNotNull(TEXT("Configured texture loads (including idle)"), Texture);
		if (Texture)
		{
#if WITH_EDITORONLY_DATA
			TestEqual(TEXT("4x raster source"), int32(Texture->Source.GetSizeX()), 128);
#endif
			TestEqual(TEXT("UI texture group"), Texture->LODGroup, TEXTUREGROUP_UI);
			TestTrue(TEXT("sRGB preserves selected color"), bool(Texture->SRGB));
		}
		const FText Prompt = FText::FromString(TEXT("Original interaction prompt"));
		HUD->SetReticle(true, Action, Prompt);
		TestEqual(TEXT("Correct brush on target change"), HUD->ReticleImage->GetBrush().GetResourceObject(), static_cast<UObject*>(Texture));
		TestTrue(TEXT("Prompt text preserved"), HUD->PromptText->GetText().EqualTo(Prompt));
		TestEqual(TEXT("Prompt visible only on target"), HUD->PromptPill->GetVisibility(),
			Action == EFixHimInteractionAction::None ? ESlateVisibility::Collapsed : ESlateVisibility::HitTestInvisible);
		HUD->SetReticle(false, Action, Prompt);
		TestEqual(TEXT("World reticle hidden outside exploration"), HUD->ReticleRoot->GetVisibility(), ESlateVisibility::Collapsed);
		TestEqual(TEXT("Prompt also hidden"), HUD->PromptPill->GetVisibility(), ESlateVisibility::Collapsed);
	}
	const auto* Box = Cast<USizeBox>(HUD->ReticleImage->GetParent());
	TestTrue(TEXT("Shared 32-unit box uses UMG DPI scaling"), Box && Box->GetWidthOverride() == 32.f && Box->GetHeightOverride() == 32.f);
	GI->Shutdown();
	World->DestroyWorld(false);
	return true;
}
#endif
