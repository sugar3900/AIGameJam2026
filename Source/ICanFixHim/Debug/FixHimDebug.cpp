// I Can Fix Him - AI Game Jam 2026

#include "Debug/FixHimDebug.h"

#if FIXHIM_DEBUG

#include "Debug/FixHimDebugWidget.h"
#include "Player/FixHimPlayerController.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "UI/FixHimDialogueWidget.h"
#include "UI/FixHimDayWidgets.h"
#include "UI/FixHimCards.h"
#include "Blueprint/UserWidget.h"
#include "Engine/LocalPlayer.h"
#include "Framework/Application/IInputProcessor.h"
#include "Framework/Application/SlateApplication.h"
#include "InputCoreTypes.h"

/**
 * Listens for the toggle keys at the Slate level, before any focus or input-mode routing, so it works in every state
 * (and in the editor's play window). Not F1 / tilde: in the editor those are viewport wireframe and the console.
 */
class FFixHimDebugKeys : public IInputProcessor
{
public:
	explicit FFixHimDebugKeys(UFixHimDebugComponent* InOwner) : Owner(InOwner) {}

	virtual void Tick(const float DeltaTime, FSlateApplication& SlateApp, TSharedRef<ICursor> Cursor) override {}

	virtual bool HandleKeyDownEvent(FSlateApplication& SlateApp, const FKeyEvent& InKeyEvent) override
	{
		const FKey Key = InKeyEvent.GetKey();
		if (!InKeyEvent.IsRepeat() && (Key == EKeys::Backslash || Key == EKeys::Insert) && Owner.IsValid())
		{
			Owner->TogglePanel();
		}
		return false; // never swallow the key
	}

	virtual const TCHAR* GetDebugName() const override { return TEXT("FixHimDebugKeys"); }

private:
	TWeakObjectPtr<UFixHimDebugComponent> Owner;
};

UFixHimDebugComponent::UFixHimDebugComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	// The panel must also open under the pause / door popups.
	PrimaryComponentTick.bTickEvenWhenPaused = true;
}

UFixHimDebugComponent* UFixHimDebugComponent::Install(AFixHimPlayerController* PC)
{
	if (!PC || PC->FindComponentByClass<UFixHimDebugComponent>())
	{
		return nullptr;
	}
	UFixHimDebugComponent* Comp = NewObject<UFixHimDebugComponent>(PC, TEXT("FixHimDebug"));
	PC->AddOwnedComponent(Comp);
	Comp->RegisterComponent();
	if (FSlateApplication::IsInitialized())
	{
		Comp->KeyProcessor = MakeShared<FFixHimDebugKeys>(Comp);
		FSlateApplication::Get().RegisterInputPreProcessor(Comp->KeyProcessor);
	}
	return Comp;
}

AFixHimPlayerController* UFixHimDebugComponent::GetPC() const
{
	return Cast<AFixHimPlayerController>(GetOwner());
}

void UFixHimDebugComponent::RemoveKeyProcessor()
{
	if (KeyProcessor.IsValid() && FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().UnregisterInputPreProcessor(KeyProcessor);
	}
	KeyProcessor.Reset();
}

void UFixHimDebugComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	RemoveKeyProcessor();
	Super::EndPlay(EndPlayReason);
}

void UFixHimDebugComponent::OnComponentDestroyed(bool bDestroyingHierarchy)
{
	RemoveKeyProcessor();
	if (Panel.IsValid() && Panel->IsInViewport())
	{
		Panel->RemoveFromParent();
	}
	Super::OnComponentDestroyed(bDestroyingHierarchy);
}

bool UFixHimDebugComponent::IsPanelOpen() const
{
	return Panel.IsValid() && Panel->IsInViewport();
}

void UFixHimDebugComponent::TogglePanel()
{
	AFixHimPlayerController* PC = GetPC();
	if (!PC)
	{
		return;
	}
	if (IsPanelOpen())
	{
		Panel->RemoveFromParent();
		PC->DebugSetPanelOpen(false);
		return;
	}
	if (PC->GetState() == EFixHimState::Title)
	{
		UE_LOG(LogFixHim, Log, TEXT("Debug panel: not available on the title screen"));
		return; // no save data to poke at yet
	}
	if (!Panel.IsValid())
	{
		Panel = CreateWidget<UFixHimDebugWidget>(PC, UFixHimDebugWidget::StaticClass());
		Panel->Setup(this);
	}
	UE_LOG(LogFixHim, Log, TEXT("Debug panel: opened"));
	Panel->AddToViewport(100);
	Panel->SyncAll();
	PC->DebugSetPanelOpen(true);
}

void UFixHimDebugComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!bAutoPlay)
	{
		StepTimer = 0.f;
		return;
	}
	StepTimer += DeltaTime;
	if (StepTimer >= FMath::Max(0.02f, StepDelay))
	{
		StepTimer = 0.f;
		AutoStep();
	}
}

void UFixHimDebugComponent::AutoStep()
{
	AFixHimPlayerController* PC = GetPC();
	UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this);
	if (!PC || !D)
	{
		return;
	}

	switch (PC->State)
	{
	case EFixHimState::Dialogue:
	case EFixHimState::Cutscene:
	{
		UFixHimDialogueWidget* Widget = PC->DialogueWidget;
		if (!Widget || !D->IsActive() || Widget->IsBusy())
		{
			return; // a fade / hearts fx is still playing
		}
		const int32 NumChoices = D->GetView().Choices.Num();
		if (NumChoices > 0)
		{
			// Same path as the controller's OnChoice: finish the typing, then choose. Hypertext [topic] links are never clicked.
			const int32 Pick = ChoicePolicy == EFixHimAutoChoice::First ? 0
				: ChoicePolicy == EFixHimAutoChoice::Last ? NumChoices - 1
				: FMath::RandRange(0, NumChoices - 1);
			Widget->TryCompleteTyping();
			D->Choose(Pick);
		}
		else
		{
			// AdvanceDialogue completes the typewriter first and only then moves on, so finish it here to move a line per step.
			Widget->TryCompleteTyping();
			PC->AdvanceDialogue();
		}
		break;
	}
	case EFixHimState::Encounter:
		// First-meeting splash card.
		if (PC->IntroWidget)
		{
			PC->IntroWidget->Skip();
		}
		break;
	case EFixHimState::Playing:
		// Opening podcast captions.
		if (PC->bPodcastPlaying && PC->RadioWidget && PC->RadioWidget->IsPlaying())
		{
			PC->RadioWidget->Advance();
		}
		break;
	default:
		break;
	}
}

#endif // FIXHIM_DEBUG
