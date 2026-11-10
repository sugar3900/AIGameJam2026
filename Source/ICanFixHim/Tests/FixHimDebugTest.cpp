// Run FixHim.TestDebugAutoPlay while a character conversation is open in PIE.
#include "ICanFixHim.h"

#if WITH_DEV_AUTOMATION_TESTS && FIXHIM_DEBUG
#include "HAL/IConsoleManager.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CheckBox.h"
#include "Debug/FixHimDebug.h"
#include "Debug/FixHimDebugWidget.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "Player/FixHimPlayerController.h"
#include "TimerManager.h"
#include "UObject/UObjectIterator.h"

namespace
{
FAutoConsoleCommandWithWorld TestDebugAutoPlay(
	TEXT("FixHim.TestDebugAutoPlay"),
	TEXT("During PIE dialogue, exercise the debug checkbox and verify automatic advancement."),
	FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
	{
		TActorIterator<AFixHimPlayerController> It(World);
		AFixHimPlayerController* PC = It ? *It : nullptr;
		if (!PC || PC->GetState() != EFixHimState::Dialogue)
		{
			UE_LOG(LogFixHim, Error, TEXT("Auto-play test: enter character dialogue first"));
			return;
		}
		auto* Comp = PC->FindComponentByClass<UFixHimDebugComponent>();
		if (!Comp || !Comp->IsComponentTickEnabled())
		{
			UE_LOG(LogFixHim, Error, TEXT("Auto-play test FAIL: debug component tick is disabled"));
			return;
		}
		const bool bWasOpen = Comp->IsPanelOpen();
		const bool bWasAuto = Comp->bAutoPlay;
		if (!bWasOpen) { Comp->TogglePanel(); }
		UCheckBox* AutoCheck = nullptr;
		for (TObjectIterator<UFixHimDebugWidget> Widget; Widget; ++Widget)
		{
			if (Widget->GetOwningPlayer() == PC && Widget->IsInViewport())
			{
				Widget->WidgetTree->ForEachWidget([&AutoCheck](UWidget* Child)
				{
					// Auto-play is the first checkbox; subsequent ones edit save flags.
					if (!AutoCheck) { AutoCheck = Cast<UCheckBox>(Child); }
				});
			}
		}
		if (AutoCheck)
		{
			AutoCheck->SetIsChecked(true);
			AutoCheck->OnCheckStateChanged.Broadcast(true);
		}
		if (!bWasOpen) { Comp->TogglePanel(); }
		if (!AutoCheck || !Comp->bAutoPlay)
		{
			UE_LOG(LogFixHim, Error, TEXT("Auto-play test FAIL: checkbox did not enable auto-play"));
			return;
		}
		const auto* D = UFixHimDialogueSubsystem::Get(Comp);
		const FString Node = D->GetView().NodeId;
		const int32 Line = D->GetView().LineIndex;
		TWeakObjectPtr<UFixHimDebugComponent> WeakComp(Comp);
		TWeakObjectPtr<UCheckBox> WeakCheck(AutoCheck);
		FTimerHandle Timer;
		World->GetTimerManager().SetTimer(Timer, [WeakComp, WeakCheck, Node, Line, bWasAuto]()
		{
			if (!WeakComp.IsValid()) { return; }
			const auto* Dialogue = UFixHimDialogueSubsystem::Get(WeakComp.Get());
			const bool bAdvanced = !Dialogue->IsActive() || Dialogue->GetView().NodeId != Node || Dialogue->GetView().LineIndex != Line;
			WeakComp->bAutoPlay = bWasAuto;
			if (WeakCheck.IsValid()) { WeakCheck->SetIsChecked(bWasAuto); }
			if (bAdvanced) { UE_LOG(LogFixHim, Display, TEXT("Auto-play test PASS: checkbox advanced live dialogue")); }
			else { UE_LOG(LogFixHim, Error, TEXT("Auto-play test FAIL: dialogue did not advance")); }
		}, 8.f, false);
	}));
}
#endif
