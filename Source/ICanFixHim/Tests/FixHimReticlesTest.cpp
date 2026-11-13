// Run: -ExecCmds="Automation RunTests FixHim.UI.Reticles" -TestExit="Automation Test Queue Empty"
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/Texture2D.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Core/FixHimSettings.h"
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
	const UFixHimSettings* Settings = UFixHimSettings::Get();
	TestEqual(TEXT("Center layer per action (dot + four icons); unavailable reserved"), HUD->ReticleCenterTextures.Num(), 5);
	TArray<UTexture2D*> Layers = { Cast<UTexture2D>(HUD->ReticleBackground->GetBrush().GetResourceObject()),
		Cast<UTexture2D>(HUD->ReticleRing->GetBrush().GetResourceObject()),
		Cast<UTexture2D>(HUD->ReticleRingIdle->GetBrush().GetResourceObject()) };
	for (const auto& Pair : HUD->ReticleCenterTextures)
	{
		Layers.Add(Pair.Value.Get());
	}
	for (UTexture2D* Texture : Layers)
	{
		if (!TestNotNull(TEXT("Configured layer texture loads"), Texture))
		{
			continue;
		}
#if WITH_EDITORONLY_DATA
		// 2x the box each layer draws in: 128px for the 64-unit box, 96px for the 48-unit idle ring.
		const bool bIdleRing = Texture == HUD->ReticleRingIdle->GetBrush().GetResourceObject();
		TestEqual(TEXT("Source is 2x its box: 1:1 at 4K"), int32(Texture->Source.GetSizeX()),
			FMath::RoundToInt32(2.f * Settings->ReticleSize * (bIdleRing ? Settings->ReticleIdleRingScale : 1.f)));
		// <=2x minification at 1080p and up: bilinear is exact there, and mips would only add blur.
		TestEqual(TEXT("No mips"), Texture->MipGenSettings, TMGS_NoMipmaps);
#endif
		TestEqual(TEXT("Bilinear"), Texture->Filter, TF_Bilinear);
		TestEqual(TEXT("UI texture group"), Texture->LODGroup, TEXTUREGROUP_UI);
		TestTrue(TEXT("sRGB preserves selected color"), bool(Texture->SRGB));
	}

	const FText Prompt = FText::FromString(TEXT("Original interaction prompt"));
	const auto Center = [HUD]() { return HUD->ReticleCenter->GetBrush().GetResourceObject(); };
	UObject* Dot = HUD->ReticleCenterTextures.FindRef(EFixHimInteractionAction::None);
	TestEqual(TEXT("Idle starts on the dot"), Center(), Dot);
	TestEqual(TEXT("Idle background transparent"), HUD->ReticleBackground->GetRenderOpacity(), 0.f);
	TestEqual(TEXT("Idle ring shown at its own size"), HUD->ReticleRingIdle->GetRenderOpacity(), 1.f);
	TestEqual(TEXT("Idle ring unscaled"), HUD->ReticleRingIdle->GetRenderTransform().Scale, FVector2D(1.f));
	TestEqual(TEXT("Full ring hidden at idle"), HUD->ReticleRing->GetRenderOpacity(), 0.f);
	const auto* IdleBox = Cast<USizeBox>(HUD->ReticleRingIdle->GetParent());
	TestTrue(TEXT("Idle ring box is ReticleSize x idle scale"), IdleBox
		&& IdleBox->GetWidthOverride() == Settings->ReticleSize * Settings->ReticleIdleRingScale);
	for (auto Action : { EFixHimInteractionAction::Inspect, EFixHimInteractionAction::Talk,
		EFixHimInteractionAction::Use, EFixHimInteractionAction::EndDay, EFixHimInteractionAction::None })
	{
		UObject* Previous = Center();
		UObject* Expected = HUD->ReticleCenterTextures.FindRef(Action);
		HUD->SetReticle(true, Action, Prompt);
		TestEqual(TEXT("Center switches to the action's layer"), Center(), Expected);
		TestEqual(TEXT("Previous center cross-fades out"), HUD->ReticleCenterOut->GetBrush().GetResourceObject(), Previous);
		TestEqual(TEXT("Incoming center starts transparent"), HUD->ReticleCenter->GetRenderOpacity(), 0.f);
		HUD->TickReticle(Settings->ReticleTransitionSeconds * 0.5f);
		const float Mid = HUD->ReticleCenter->GetRenderOpacity();
		TestTrue(TEXT("Transition is in progress mid-way"), Mid > 0.f && Mid < 1.f);
		const float IdleRadius = HUD->ReticleRingIdle->GetRenderTransform().Scale.X * Settings->ReticleIdleRingScale;
		TestTrue(TEXT("Swapping rings share a radius"), FMath::IsNearlyEqual(IdleRadius, float(HUD->ReticleRing->GetRenderTransform().Scale.X), 1e-4f));
		HUD->TickReticle(Settings->ReticleTransitionSeconds);
		const bool bActionable = Action != EFixHimInteractionAction::None;
		TestEqual(TEXT("Partial ink background only for actionable targets"), HUD->ReticleBackground->GetRenderOpacity(),
			bActionable ? Settings->ReticleBackgroundOpacity : 0.f);
		TestEqual(TEXT("Full ring only on targets"), HUD->ReticleRing->GetRenderOpacity(), bActionable ? 1.f : 0.f);
		TestEqual(TEXT("Full ring settles at full size"), HUD->ReticleRing->GetRenderTransform().Scale,
			FVector2D(bActionable ? 1.f : Settings->ReticleIdleRingScale));
		TestEqual(TEXT("Idle ring only at idle"), HUD->ReticleRingIdle->GetRenderOpacity(), bActionable ? 0.f : 1.f);
		TestEqual(TEXT("Idle ring settles unscaled at idle"), HUD->ReticleRingIdle->GetRenderTransform().Scale,
			FVector2D(bActionable ? 1.f / Settings->ReticleIdleRingScale : 1.f));
		TestEqual(TEXT("Center settles opaque at full size"), HUD->ReticleCenter->GetRenderOpacity(), 1.f);
		TestEqual(TEXT("Center settles at full size"), HUD->ReticleCenter->GetRenderTransform().Scale, FVector2D(1.f));
		TestEqual(TEXT("Outgoing center gone"), HUD->ReticleCenterOut->GetRenderOpacity(), 0.f);
		TestTrue(TEXT("Prompt text preserved"), HUD->PromptText->GetText().EqualTo(Prompt));
		TestEqual(TEXT("Prompt visible only on target"), HUD->PromptPill->GetVisibility(),
			bActionable ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	}

	// Interrupting a transition re-targets from the current state; hiding and reappearing never animate.
	HUD->SetReticle(true, EFixHimInteractionAction::Use, Prompt);
	HUD->TickReticle(Settings->ReticleTransitionSeconds * 0.5f);
	HUD->SetReticle(true, EFixHimInteractionAction::None, Prompt);
	TestTrue(TEXT("Interrupted icon fades out from its partial state"), HUD->ReticleCenterOut->GetRenderOpacity() < 1.f);
	HUD->SetReticle(false, EFixHimInteractionAction::Talk, Prompt);
	TestEqual(TEXT("World reticle hidden outside exploration"), HUD->ReticleRoot->GetVisibility(), ESlateVisibility::Collapsed);
	TestEqual(TEXT("Prompt also hidden"), HUD->PromptPill->GetVisibility(), ESlateVisibility::Collapsed);
	TestEqual(TEXT("Hidden reticle settles instantly"), HUD->ReticleCenter->GetRenderOpacity(), 1.f);
	HUD->SetReticle(true, EFixHimInteractionAction::Inspect, Prompt);
	TestEqual(TEXT("Reappearing shows the settled state"), HUD->ReticleCenter->GetRenderOpacity(), 1.f);
	TestEqual(TEXT("Reappearing background settled"), HUD->ReticleBackground->GetRenderOpacity(), Settings->ReticleBackgroundOpacity);
	TestEqual(TEXT("Reappearing ring settled"), HUD->ReticleRing->GetRenderTransform().Scale, FVector2D(1.f));
	TestEqual(TEXT("Reappearing idle ring hidden"), HUD->ReticleRingIdle->GetRenderOpacity(), 0.f);

	const auto* Box = Cast<USizeBox>(HUD->ReticleCenter->GetParent()->GetParent());
	TestTrue(TEXT("Reticle box uses the configured UMG size (DPI scaled)"),
		Box && Box->GetWidthOverride() == Settings->ReticleSize && Box->GetHeightOverride() == Settings->ReticleSize);
	TestEqual(TEXT("Default size is double the 32-unit kit reference"), Settings->ReticleSize, 64.f);
	TestEqual(TEXT("Idle ring default 75%"), Settings->ReticleIdleRingScale, 0.75f);
	TestEqual(TEXT("Background default 50% opacity"), Settings->ReticleBackgroundOpacity, 0.5f);
	TestEqual(TEXT("Prompt sits below the reticle"), HUD->PromptPill->GetRenderTransform().Translation.Y, double(Settings->ReticleSize * 0.5f + 56.f));
	GI->Shutdown();
	World->DestroyWorld(false);
	return true;
}
#endif
