// I Can Fix Him - AI Game Jam 2026

#include "Player/FixHimPlayerController.h"
#include "Player/FixHimCharacter.h"
#include "World/FixHimInteractable.h"
#include "World/FixHimMalady.h"
#include "World/FixHimDoor.h"
#include "World/FixHimHunk.h"
#include "World/FixHimRoom.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Audio/FixHimMusicSubsystem.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Core/FixHimSettings.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "UI/FixHimMenus.h"
#include "UI/FixHimHUDWidget.h"
#include "UI/FixHimDialogueWidget.h"
#include "UI/FixHimFloorPlanWidget.h"
#include "UI/FixHimCards.h"
#include "UI/FixHimDayWidgets.h"
#include "Debug/FixHimDebug.h"
#include "Engine/DirectionalLight.h"
#include "Engine/Light.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/LightComponent.h"
#include "ICanFixHim.h"
#include "Blueprint/UserWidget.h"
#include "Camera/CameraActor.h"
#include "Components/ArrowComponent.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Misc/CommandLine.h"
#include "UnrealClient.h"
#include "TimerManager.h"
#include "Engine/GameViewportClient.h"
#include "Widgets/SViewport.h"

namespace
{
	/** Degrees of turn per mouse count at sensitivity 1.0. */
	constexpr float MouseLookScale = 0.3f;
}

AFixHimPlayerController::AFixHimPlayerController()
{
	bShowMouseCursor = true;
	bEnableClickEvents = false;
	bEnableMouseOverEvents = false;
}

// ---------------------------------------------------------------------------
// Lifecycle

void AFixHimPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalController())
	{
		return;
	}

	BuildInput();
#if WITH_EDITOR || !UE_BUILD_SHIPPING
	UFixHimDebugComponent::Install(this);
#endif

	if (UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this))
	{
		ViewHandle = Dialogue->OnView.AddUObject(this, &AFixHimPlayerController::HandleDialogueView);
		StartedHandle = Dialogue->OnConversationStarted.AddUObject(this, &AFixHimPlayerController::HandleConversationStarted);
		EndHandle = Dialogue->OnConversationEnded.AddUObject(this, &AFixHimPlayerController::HandleConversationEnded);
	}
	if (UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this))
	{
		StatHandle = Save->OnStatChanged.AddUObject(this, &AFixHimPlayerController::HandleStatChanged);
		SavedHandle = Save->OnSaved.AddUObject(this, &AFixHimPlayerController::HandleSaved);
		PreSaveHandle = Save->OnPreSave.AddUObject(this, &AFixHimPlayerController::HandlePreSave);
		Save->ApplyOptions();
	}

	HUDWidget = CreateWidget<UFixHimHUDWidget>(this, UFixHimHUDWidget::StaticClass());
	TitleWidget = CreateWidget<UFixHimTitleWidget>(this, UFixHimTitleWidget::StaticClass());

	for (TActorIterator<ACameraActor> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("TitleCamera")))
		{
			TitleCamera = *It;
			if (It->ActorHasTag(TEXT("TitleCameraAsPlaced")))
			{
				// The level placed this camera for its own layout (e.g. L_Apartment_Rev02): use it as is.
				TitleCameraBase = It->GetActorTransform();
			}
			else
			{
				// The original L_Apartment's camera sits near the living room's corner and clips into the walls as
				// it drifts; hold it further into that room instead.
				TitleCameraBase = FTransform(FRotator(-11.f, -150.f, 0.f), FVector(600.f, 430.f, 185.f));
				It->SetActorTransform(TitleCameraBase);
			}
			break;
		}
	}

	TActorIterator<ADirectionalLight> SunIt(GetWorld());
	if (SunIt)
	{
		Sun = *SunIt;
		// The map's sun is placed Static/Stationary; UpdateDaylight moves it every tick, which otherwise
		// spams a "has to be 'Movable'" error into the Message Log.
		if (USceneComponent* SunRoot = Sun->GetRootComponent())
		{
			SunRoot->SetMobility(EComponentMobility::Movable);
		}
		SunBaseRotation = Sun->GetActorRotation();
		if (ULightComponent* LC = Sun->GetLightComponent())
		{
			SunBaseIntensity = LC->Intensity;
			SunBaseColor = LC->GetLightColor();
		}
	}

	// Authored exterior window spots follow the same day curve as the painted views.
	// Cache once, so restarting a day never mistakes the faded intensity for its authored value.
	for (TActorIterator<ALight> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("WindowSun")))
		{
			if (ULightComponent* LC = It->GetLightComponent())
			{
				LC->SetMobility(EComponentMobility::Movable);
				WindowSunLights.Add(LC);
				WindowSunBaseIntensities.Add(LC->Intensity);
			}
		}
	}

	for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("WindowView")))
		{
			if (UMaterialInstanceDynamic* View = It->GetStaticMeshComponent()->CreateDynamicMaterialInstance(0))
			{
				WindowViews.Add(View);
			}
		}
	}

	// The saved map may predate the door; make sure there is always one to click.
	AFixHimDoor::EnsureInWorld(GetWorld());

	EnterState(EFixHimState::Title);

	FString Script;
	if (FParse::Value(FCommandLine::Get(), TEXT("FixHimScript="), Script, false))
	{
		FixHimScript(Script);
	}
}

void AFixHimPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{
	if (UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this))
	{
		Dialogue->OnView.Remove(ViewHandle);
		Dialogue->OnConversationStarted.Remove(StartedHandle);
		Dialogue->OnConversationEnded.Remove(EndHandle);
		Dialogue->AbortConversation();
	}
	if (UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this))
	{
		Save->OnStatChanged.Remove(StatHandle);
		Save->OnSaved.Remove(SavedHandle);
		Save->OnPreSave.Remove(PreSaveHandle);
	}
	Super::EndPlay(Reason);
}

// ---------------------------------------------------------------------------
// Input

void AFixHimPlayerController::BuildInput()
{
	// Input is defined in code so the whole control scheme is visible in one place.
	auto MakeAction = [this](EInputActionValueType Type, bool bWhenPaused = false)
	{
		UInputAction* A = NewObject<UInputAction>(this);
		A->ValueType = Type;
		A->bTriggerWhenPaused = bWhenPaused;
		return A;
	};

	Mapping = NewObject<UInputMappingContext>(this);
	MoveAction = MakeAction(EInputActionValueType::Axis2D);
	MouseLookAction = MakeAction(EInputActionValueType::Axis2D);
	StickLookAction = MakeAction(EInputActionValueType::Axis2D);
	InteractAction = MakeAction(EInputActionValueType::Boolean);
	AdvanceAction = MakeAction(EInputActionValueType::Boolean);
	PauseAction = MakeAction(EInputActionValueType::Boolean, true);
	MapAction = MakeAction(EInputActionValueType::Boolean);

	auto Swizzle = [this]() { return NewObject<UInputModifierSwizzleAxis>(this); };
	auto Negate = [this]() { return NewObject<UInputModifierNegate>(this); };

	Mapping->MapKey(MoveAction, EKeys::W).Modifiers.Add(Swizzle());
	{
		FEnhancedActionKeyMapping& S = Mapping->MapKey(MoveAction, EKeys::S);
		S.Modifiers.Add(Swizzle());
		S.Modifiers.Add(Negate());
	}
	Mapping->MapKey(MoveAction, EKeys::A).Modifiers.Add(Negate());
	Mapping->MapKey(MoveAction, EKeys::D);
	Mapping->MapKey(MoveAction, EKeys::Up).Modifiers.Add(Swizzle());
	{
		FEnhancedActionKeyMapping& Down = Mapping->MapKey(MoveAction, EKeys::Down);
		Down.Modifiers.Add(Swizzle());
		Down.Modifiers.Add(Negate());
	}
	Mapping->MapKey(MoveAction, EKeys::Left).Modifiers.Add(Negate());
	Mapping->MapKey(MoveAction, EKeys::Right);
	Mapping->MapKey(MoveAction, EKeys::Gamepad_Left2D);

	Mapping->MapKey(MouseLookAction, EKeys::Mouse2D);
	Mapping->MapKey(StickLookAction, EKeys::Gamepad_Right2D);

	Mapping->MapKey(InteractAction, EKeys::LeftMouseButton);
	Mapping->MapKey(InteractAction, EKeys::E);
	Mapping->MapKey(InteractAction, EKeys::Gamepad_FaceButton_Bottom);

	Mapping->MapKey(AdvanceAction, EKeys::SpaceBar);
	Mapping->MapKey(AdvanceAction, EKeys::Enter);

	Mapping->MapKey(PauseAction, EKeys::Escape);
	Mapping->MapKey(PauseAction, EKeys::P);
	Mapping->MapKey(PauseAction, EKeys::Gamepad_Special_Right);

	Mapping->MapKey(MapAction, EKeys::M);
	Mapping->MapKey(MapAction, EKeys::Tab);
	Mapping->MapKey(MapAction, EKeys::Gamepad_FaceButton_Top);

	const FKey ChoiceKeys[] = { EKeys::One, EKeys::Two, EKeys::Three, EKeys::Four, EKeys::Five };
	for (const FKey& Key : ChoiceKeys)
	{
		UInputAction* A = MakeAction(EInputActionValueType::Boolean);
		Mapping->MapKey(A, Key);
		ChoiceActions.Add(A);
	}

	if (UEnhancedInputLocalPlayerSubsystem* Sub = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		Sub->AddMappingContext(Mapping, 0);
	}

	if (UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(InputComponent))
	{
		EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AFixHimPlayerController::OnMove);
		EIC->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &AFixHimPlayerController::OnMouseLook);
		EIC->BindAction(StickLookAction, ETriggerEvent::Triggered, this, &AFixHimPlayerController::OnStickLook);
		EIC->BindAction(InteractAction, ETriggerEvent::Started, this, &AFixHimPlayerController::OnInteract);
		EIC->BindAction(AdvanceAction, ETriggerEvent::Started, this, &AFixHimPlayerController::OnAdvance);
		EIC->BindAction(PauseAction, ETriggerEvent::Started, this, &AFixHimPlayerController::OnPausePressed);
		EIC->BindAction(MapAction, ETriggerEvent::Started, this, &AFixHimPlayerController::OnMapPressed);
		for (int32 i = 0; i < ChoiceActions.Num(); ++i)
		{
			EIC->BindAction(ChoiceActions[i], ETriggerEvent::Started, this, &AFixHimPlayerController::OnChoice, i);
		}
	}
	else
	{
		UE_LOG(LogFixHim, Error, TEXT("Enhanced Input component missing; check DefaultInput.ini"));
	}
}

void AFixHimPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
}

void AFixHimPlayerController::OnMove(const FInputActionValue& Value)
{
	if (State == EFixHimState::Playing)
	{
		if (AFixHimCharacter* C = Cast<AFixHimCharacter>(GetPawn()))
		{
			const FVector2D V = Value.Get<FVector2D>();
			C->DoMove(V.X, V.Y);
		}
	}
}

void AFixHimPlayerController::OnMouseLook(const FInputActionValue& Value)
{
	if (State != EFixHimState::Playing)
	{
		return;
	}
#if WITH_EDITOR || !UE_BUILD_SHIPPING
	if (bDebugPanelOpen)
	{
		return; // the mouse drives the debug panel's cursor
	}
#endif
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const float Sens = MouseLookScale * (Save ? Save->Options().MouseSensitivity : 1.f);
	const bool bInvert = Save && Save->Options().bInvertY;
	const FVector2D V = Value.Get<FVector2D>();
	if (AFixHimCharacter* C = Cast<AFixHimCharacter>(GetPawn()))
	{
		C->DoLook(V.X * Sens, V.Y * Sens * (bInvert ? -1.f : 1.f));
	}
}

void AFixHimPlayerController::OnStickLook(const FInputActionValue& Value)
{
	if (State != EFixHimState::Playing)
	{
		return;
	}
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const float Rate = 150.f * GetWorld()->GetDeltaSeconds() * (Save ? Save->Options().MouseSensitivity : 1.f);
	const bool bInvert = Save && Save->Options().bInvertY;
	const FVector2D V = Value.Get<FVector2D>();
	if (AFixHimCharacter* C = Cast<AFixHimCharacter>(GetPawn()))
	{
		C->DoLook(V.X * Rate, V.Y * Rate * (bInvert ? -1.f : 1.f));
	}
}

void AFixHimPlayerController::OnInteract()
{
	switch (State)
	{
	case EFixHimState::Playing:
		if (bPodcastPlaying && RadioWidget)
		{
			// Click through the opening podcast captions one line at a time, even when pointing at something
			// interactable: skipping wins until the episode is over.
			RadioWidget->Advance();
		}
		else if (Hovered && Hovered->CanInteract())
		{
			Hovered->Interact(this);
		}
		break;
	case EFixHimState::Dialogue:
	case EFixHimState::Cutscene:
		AdvanceDialogue();
		break;
	case EFixHimState::Encounter:
		// Click through the first-meeting splash.
		if (IntroWidget)
		{
			IntroWidget->Skip();
		}
		break;
	default:
		break;
	}
}

void AFixHimPlayerController::OnAdvance()
{
	if (State == EFixHimState::Dialogue || State == EFixHimState::Cutscene)
	{
		AdvanceDialogue();
	}
	else if (State == EFixHimState::Playing || State == EFixHimState::Encounter)
	{
		OnInteract();
	}
}

void AFixHimPlayerController::OnPausePressed()
{
	if (SubMenu)
	{
		CloseSubMenu();
		return;
	}
	if (NameWidget)
	{
		CancelNameEntry();
		return;
	}
	switch (State)
	{
	case EFixHimState::FloorPlan:
		ToggleFloorPlan();
		break;
	case EFixHimState::Paused:
		SetPaused(false);
		break;
	case EFixHimState::DoorPrompt:
		CloseDoorPrompt();
		break;
	case EFixHimState::Playing:
	case EFixHimState::Dialogue:
		SetPaused(true);
		break;
	default:
		break;
	}
}

void AFixHimPlayerController::OnMapPressed()
{
	if (State == EFixHimState::Playing || State == EFixHimState::FloorPlan)
	{
		ToggleFloorPlan();
	}
}

void AFixHimPlayerController::OnChoice(int32 Index)
{
	if ((State == EFixHimState::Dialogue || State == EFixHimState::Cutscene) && DialogueWidget && !DialogueWidget->IsBusy())
	{
		if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
		{
			if (Index < D->GetView().Choices.Num())
			{
				DialogueWidget->TryCompleteTyping();
				D->Choose(Index);
			}
		}
	}
}

// ---------------------------------------------------------------------------
// State machine

void AFixHimPlayerController::ShowWidget(UUserWidget* Widget, int32 ZOrder)
{
	if (Widget && !Widget->IsInViewport())
	{
		Widget->AddToViewport(ZOrder);
	}
}

void AFixHimPlayerController::HideWidget(UUserWidget* Widget)
{
	if (Widget && Widget->IsInViewport())
	{
		Widget->RemoveFromParent();
	}
}

void AFixHimPlayerController::EnterState(EFixHimState NewState)
{
	State = NewState;

	const bool bTitle = State == EFixHimState::Title;
	if (bTitle)
	{
		ShowWidget(TitleWidget, 10);
		TitleWidget->RefreshContinue();
		HideWidget(HUDWidget);
		if (TitleCamera)
		{
			SetViewTargetWithBlend(TitleCamera, 0.f);
		}
	}
	else
	{
		HideWidget(TitleWidget);
		ShowWidget(HUDWidget, 0);
	}

	if (HUDWidget)
	{
		HUDWidget->SetReticle(State == EFixHimState::Playing, false, FText::GetEmpty());
	}
	if (State != EFixHimState::Playing)
	{
		SetHovered(nullptr);
	}
	ApplyInputModeForState();
	UpdateMusic();
}

void AFixHimPlayerController::UpdateMusic()
{
	UFixHimMusicSubsystem* Music = UFixHimMusicSubsystem::Get(this);
	if (!Music)
	{
		return;
	}
	// Paused is an overlay: keep the music of whatever was underneath.
	const EFixHimState Effective = State == EFixHimState::Paused ? StateBeforePause : State;
	FName Track = NAME_None; // None = leave the current track alone
	float Fade = 1.5f;
	switch (Effective)
	{
	case EFixHimState::Title:
		Track = TEXT("MainMenu");
		break;
	case EFixHimState::Playing:
	case EFixHimState::FloorPlan:
	case EFixHimState::DoorPrompt:
		Track = TEXT("Explore");
		break;
	case EFixHimState::Encounter:
	case EFixHimState::Dialogue:
	{
		const FString Id = ActiveMalady ? ActiveMalady->HunkId : MusicConvId;
		Track = TEXT("Explore");
		for (const TCHAR* Hunk : { TEXT("lukey"), TEXT("malcolm"), TEXT("tyler"), TEXT("wyatt") })
		{
			if (Id.Equals(Hunk, ESearchCase::IgnoreCase))
			{
				FString Name = Id.ToLower();
				Name[0] = FChar::ToUpper(Name[0]);
				Track = FName(*Name);
			}
		}
		Fade = 1.0f;
		break;
	}
	case EFixHimState::Cutscene: // inspection / podcast / epilogue scenes
	case EFixHimState::Finale:
		Track = TEXT("Finale");
		Fade = 2.5f;
		break;
	default: // Ending, Traveling, Sleeping: unspecified, keep playing
		break;
	}
	if (!Track.IsNone() && !Music->PlayTrack(Track, Fade) && Track != TEXT("Explore"))
	{
		Music->PlayTrack(TEXT("Explore"), Fade); // a missing hunk/finale track falls back to Explore
	}
}

void AFixHimPlayerController::ApplyInputModeForState()
{
	bool bGameOnly = State == EFixHimState::Playing;
#if WITH_EDITOR || !UE_BUILD_SHIPPING
	bGameOnly = bGameOnly && !bDebugPanelOpen;
#endif
	if (bGameOnly)
	{
		bShowMouseCursor = false;
		SetInputMode(FInputModeGameOnly());
	}
	else
	{
		bShowMouseCursor = true;
		FInputModeGameAndUI Mode;
		Mode.SetHideCursorDuringCapture(false);
		Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		SetInputMode(Mode);
	}
	RefreshInteractionShine();
}

void AFixHimPlayerController::RefreshInteractionShine()
{
	bool bAllow = State == EFixHimState::Playing && !bPodcastPlaying;
#if WITH_EDITOR || !UE_BUILD_SHIPPING
	bAllow = bAllow && !bDebugPanelOpen;
#endif
	for (TActorIterator<AFixHimInteractable> It(GetWorld()); It; ++It)
	{
		It->SetInteractionShineEnabled(bAllow);
	}
}

void AFixHimPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);

	if (State != EFixHimState::Title && State != EFixHimState::Paused && State != EFixHimState::DoorPrompt && State != EFixHimState::Sleeping && State != EFixHimState::Finale)
	{
		UpdateDaylight(DeltaTime);
	}
	if (UFixHimMusicSubsystem* Music = UFixHimMusicSubsystem::Get(this))
	{
		// The opening podcast has its own radio audio: keep the music under it.
		Music->SetDuck(bPodcastPlaying ? 0.4f : 1.f, 0.8f);
	}
	if (State == EFixHimState::Playing)
	{
		UpdateHover();
	}
	else if (State == EFixHimState::Title && TitleCamera)
	{
		// Slow dreamy drift on the title screen.
		TitleTime += DeltaTime;
		FTransform T = TitleCameraBase;
		T.AddToTranslation(FVector(0.f, FMath::Sin(TitleTime * 0.15f) * 60.f, FMath::Sin(TitleTime * 0.23f) * 12.f));
		T.ConcatenateRotation(FRotator(0.f, FMath::Sin(TitleTime * 0.11f) * 6.f, 0.f).Quaternion());
		TitleCamera->SetActorTransform(T);
	}
}

void AFixHimPlayerController::UpdateHover()
{
	const APawn* P = GetPawn();
	if (!P || !PlayerCameraManager)
	{
		SetHovered(nullptr);
		return;
	}
	const FVector Start = PlayerCameraManager->GetCameraLocation();
	const FVector Dir = PlayerCameraManager->GetCameraRotation().Vector();
	FCollisionQueryParams Q(SCENE_QUERY_STAT(FixHimHover), false, P);
	FHitResult Hit;
	AFixHimInteractable* Found = nullptr;
	if (GetWorld()->LineTraceSingleByChannel(Hit, Start, Start + Dir * 2500.f, ECC_Visibility, Q))
	{
		AFixHimInteractable* I = Cast<AFixHimInteractable>(Hit.GetActor());
		if (I && I->CanInteract() && FVector::Dist(Hit.ImpactPoint, P->GetActorLocation()) <= (I->InteractRangeOverride > 0.f ? I->InteractRangeOverride : UFixHimSettings::Get()->InteractRange))
		{
			Found = I;
		}
	}
	SetHovered(Found);
}

void AFixHimPlayerController::SetHovered(AFixHimInteractable* NewHovered)
{
	if (Hovered != NewHovered)
	{
		if (Hovered)
		{
			Hovered->SetHovered(false);
		}
		Hovered = NewHovered;
		if (Hovered)
		{
			Hovered->SetHovered(true);
		}
	}
	if (HUDWidget && State == EFixHimState::Playing)
	{
		HUDWidget->SetReticle(true, Hovered != nullptr, Hovered ? Hovered->GetPrompt() : FText::GetEmpty());
	}
}

// ---------------------------------------------------------------------------
// Menus

void AFixHimPlayerController::PlacePlayerAtDoor()
{
	APawn* P = GetPawn();
	if (!P)
	{
		return;
	}
	// A level can mark its own spot just inside the front door with a PlayerStart tagged "DoorStart"
	// (the redesigned apartment's entry is on the east hall wall).
	for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("DoorStart")))
		{
			const FRotator Facing(0.f, It->GetActorRotation().Yaw, 0.f);
			P->TeleportTo(It->GetActorLocation(), Facing);
			SetControlRotation(Facing);
			return;
		}
	}
	// Original apartment: just inside the front door (living room's south wall), looking into the apartment.
	P->TeleportTo(FVector(190.f, 120.f, P->GetActorLocation().Z), FRotator(0.f, 75.f, 0.f));
	SetControlRotation(FRotator(0.f, 75.f, 0.f));
}

void AFixHimPlayerController::BeginPlaying(bool bFromSave)
{
	if (!bFromSave)
	{
		PlacePlayerAtDoor();
	}
	SetViewTargetWithBlend(GetPawn(), bFromSave ? 0.6f : 1.4f, VTBlend_EaseInOut, 2.f);
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		It->RefreshRepairState();
		It->DismissHunk(false);
	}
	FixHim::Sfx(this, "MenuStart");
	EnterState(EFixHimState::Playing);
	RefreshRepairs();
	StartDay(bFromSave);
	// Rooms only fire overlap events on change, so resolve the starting room explicitly.
	if (const APawn* P = GetPawn())
	{
		for (TActorIterator<AFixHimRoom> It(GetWorld()); It; ++It)
		{
			if (It->ContainsPoint(P->GetActorLocation()))
			{
				NotifyEnteredRoom(*It);
				break;
			}
		}
	}
}

void AFixHimPlayerController::StartNewGame()
{
	if (State != EFixHimState::Title)
	{
		return;
	}
	HideWidget(TitleWidget);
	NameWidget = CreateWidget<UFixHimNameEntryWidget>(this, UFixHimNameEntryWidget::StaticClass());
	ShowWidget(NameWidget, 50);
}

void AFixHimPlayerController::CancelNameEntry()
{
	HideWidget(NameWidget);
	NameWidget = nullptr;
	if (State == EFixHimState::Title)
	{
		ShowWidget(TitleWidget, 10);
	}
}

void AFixHimPlayerController::BeginNewGame(const FString& PlayerName)
{
	if (State != EFixHimState::Title)
	{
		return;
	}
	HideWidget(NameWidget);
	NameWidget = nullptr;
	if (UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this))
	{
		Save->NewGame();
		Save->Data().PlayerName = PlayerName.TrimStartAndEnd().Left(16);
		Save->SaveGame();
	}
	BeginPlaying(false);
}

void AFixHimPlayerController::ContinueGame()
{
	if (State != EFixHimState::Title)
	{
		return;
	}
	UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	if (!Save || !Save->LoadGame())
	{
		StartNewGame();
		return;
	}
	if (APawn* P = GetPawn(); P && Save->Data().bHasPlayerTransform)
	{
		// Only restore a position that lies in one of this map's rooms; a save from another layout (or a stale
		// position) falls back to the front door, keeping all story and repair progress.
		// Inclusive with a small tolerance: rooms share edges (doorways), and a position exactly on a shared
		// edge must still count. (AFixHimRoom::ContainsPoint is strict, so it isn't used here.)
		bool bInsideRoom = false;
		const FVector2D Saved2D(Save->Data().PlayerLocation);
		for (TActorIterator<AFixHimRoom> It(GetWorld()); It; ++It)
		{
			const FBox2D Rect = It->GetFloorRect().ExpandBy(2.f);
			if (Saved2D.X >= Rect.Min.X && Saved2D.X <= Rect.Max.X && Saved2D.Y >= Rect.Min.Y && Saved2D.Y <= Rect.Max.Y)
			{
				bInsideRoom = true;
				break;
			}
		}
		// Also require that the pawn actually fits there (a save made in another layout can land inside a wall
		// or furniture even when it is within a room's rectangle). TeleportTo with bIsATest only tests.
		const FRotator SavedFacing(0.f, Save->Data().PlayerYaw, 0.f);
		const bool bFits = bInsideRoom && P->TeleportTo(Save->Data().PlayerLocation, SavedFacing, /*bIsATest*/ true);
		if (bFits)
		{
			P->SetActorLocation(Save->Data().PlayerLocation, false, nullptr, ETeleportType::TeleportPhysics);
			SetControlRotation(FRotator(-10.f, Save->Data().PlayerYaw, 0.f));
			P->SetActorRotation(SavedFacing);
		}
		else
		{
			UE_LOG(LogFixHim, Warning, TEXT("Saved position %s is %s; starting at the front door"),
				*Save->Data().PlayerLocation.ToString(), bInsideRoom ? TEXT("blocked") : TEXT("outside every room"));
			PlacePlayerAtDoor();
		}
	}
	BeginPlaying(true);
}

void AFixHimPlayerController::OpenOptions()
{
	HideWidget(SubMenu);
	OptionsWidget = CreateWidget<UFixHimOptionsWidget>(this, UFixHimOptionsWidget::StaticClass());
	SubMenu = OptionsWidget;
	ShowWidget(SubMenu, 50);
}

void AFixHimPlayerController::OpenCredits()
{
	HideWidget(SubMenu);
	CreditsWidget = CreateWidget<UFixHimCreditsWidget>(this, UFixHimCreditsWidget::StaticClass());
	SubMenu = CreditsWidget;
	ShowWidget(SubMenu, 50);
}

void AFixHimPlayerController::CloseSubMenu()
{
	HideWidget(SubMenu);
	SubMenu = nullptr;
}

void AFixHimPlayerController::SetPaused(bool bPause)
{
	if (bPause)
	{
		if (State != EFixHimState::Playing && State != EFixHimState::Dialogue)
		{
			return;
		}
		StateBeforePause = State;
		if (!PauseWidget)
		{
			PauseWidget = CreateWidget<UFixHimPauseWidget>(this, UFixHimPauseWidget::StaticClass());
		}
		ShowWidget(PauseWidget, 40);
		SetPause(true);
		EnterState(EFixHimState::Paused);
	}
	else if (State == EFixHimState::Paused)
	{
		CloseSubMenu();
		HideWidget(PauseWidget);
		SetPause(false);
		EnterState(StateBeforePause);
	}
}

void AFixHimPlayerController::OpenDoorPrompt()
{
	if (State != EFixHimState::Playing)
	{
		return;
	}
	if (!DoorWidget)
	{
		DoorWidget = CreateWidget<UFixHimDoorPromptWidget>(this, UFixHimDoorPromptWidget::StaticClass());
	}
	ShowWidget(DoorWidget, 40);
	// Widgets build lazily on first show, so refresh afterwards.
	DoorWidget->Refresh();
	SetPause(true);
	EnterState(EFixHimState::DoorPrompt);
}

void AFixHimPlayerController::CloseDoorPrompt()
{
	if (State != EFixHimState::DoorPrompt)
	{
		return;
	}
	HideWidget(DoorWidget);
	SetPause(false);
	EnterState(EFixHimState::Playing);
}

void AFixHimPlayerController::ConfirmEndDay()
{
	if (State != EFixHimState::DoorPrompt || !CanEndDay())
	{
		return;
	}
	// Back to Playing first: RequestEndDay only runs from there (and may bounce with a toast on week 1).
	FixHim::Sfx(this, "DoorLatch");
	CloseDoorPrompt();
	RequestEndDay();
}

void AFixHimPlayerController::ReturnToMainMenu()
{
	if (UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this))
	{
		if (State != EFixHimState::Title)
		{
			Save->SaveGame();
		}
	}
	if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		D->AbortConversation();
	}
	SetPause(false);
	FixHim::Music(this, TEXT("MainMenu"), 1.0f); // start fading now; the reloaded title keeps it going
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}

void AFixHimPlayerController::FinishGame()
{
	if (UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this))
	{
		Save->DeleteSave();
	}
	if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		D->AbortConversation();
	}
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}

void AFixHimPlayerController::QuitToDesktop()
{
	UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false);
}

void AFixHimPlayerController::CloseEndingCard()
{
	HideWidget(EndingWidget);
	EndingWidget = nullptr;
	if (State == EFixHimState::Ending)
	{
		EnterState(EFixHimState::Playing);
	}
}

// ---------------------------------------------------------------------------
// Encounters & dialogue

void AFixHimPlayerController::BeginEncounter(AFixHimMalady* Malady)
{
	if (State != EFixHimState::Playing || !Malady || !Malady->GetHunk())
	{
		return;
	}
	if (bPodcastPlaying)
	{
		if (HUDWidget)
		{
			HUDWidget->ShowToast(TEXT("Shh. The podcast's still on. Let the episode finish first."), 2.5f);
		}
		return;
	}
	UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	const FHunkDefinition* Def = Dialogue ? Dialogue->FindHunk(Malady->HunkId) : nullptr;
	if (!Def)
	{
		UE_LOG(LogFixHim, Warning, TEXT("No dialogue for hunk '%s'"), *Malady->HunkId);
		return;
	}

	ActiveMalady = Malady;
	EnterState(EFixHimState::Encounter);

	// Step Rosie up to the talk spot facing him, then swing the camera to her eye line there.
	if (ACharacter* C = Cast<ACharacter>(GetPawn()))
	{
		C->GetCharacterMovement()->StopMovementImmediately();
		const FVector TalkLoc = Malady->GetTalkLocation(C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
		FVector ToHunk = Malady->HunkSpawn->GetComponentLocation() - TalkLoc;
		ToHunk.Z = 0.f;
		C->SetActorLocationAndRotation(TalkLoc, ToHunk.Rotation(), false, nullptr, ETeleportType::TeleportPhysics);
		SetControlRotation(FRotator(-12.f, ToHunk.Rotation().Yaw, 0.f));
	}
	// He grows gently out of the fixture (a short sparkly beat first) while the camera eases over: no jump scare.
	Malady->SummonHunk();
	SetViewTargetWithBlend(Malady, 1.25f, VTBlend_EaseInOut, 2.6f);
	// Talk (or show the intro card) once he has finished growing in.
	const float Arrived = AFixHimHunk::AppearDelay + AFixHimHunk::AppearGrowSeconds + 0.1f;

	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const FHunkProgress* P = Save ? Save->FindHunk(Malady->HunkId) : nullptr;
	const bool bFirstMeeting = !P || !P->bMet;

	if (bFirstMeeting)
	{
		GetWorldTimerManager().SetTimer(EncounterTimer, [this, Def]()
		{
			if (State != EFixHimState::Encounter || !ActiveMalady)
			{
				return;
			}
			IntroWidget = CreateWidget<UFixHimIntroCardWidget>(this, UFixHimIntroCardWidget::StaticClass());
			ShowWidget(IntroWidget, 30);
			TWeakObjectPtr<AFixHimPlayerController> Self(this);
			IntroWidget->Setup(*Def, ActiveMalady->GetHunk(), [Self]()
			{
				if (Self.IsValid())
				{
					Self->HideWidget(Self->IntroWidget);
					Self->IntroWidget = nullptr;
					Self->StartDialogue();
				}
			});
		}, Arrived, false);
	}
	else
	{
		GetWorldTimerManager().SetTimer(EncounterTimer, [this]() { StartDialogue(); }, Arrived, false);
	}
}

void AFixHimPlayerController::StartDialogue()
{
	if (!ActiveMalady || State != EFixHimState::Encounter)
	{
		return;
	}
	UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	if (!Dialogue)
	{
		return;
	}
	if (!DialogueWidget)
	{
		DialogueWidget = CreateWidget<UFixHimDialogueWidget>(this, UFixHimDialogueWidget::StaticClass());
	}
	ShowWidget(DialogueWidget, 20);
	AFixHimHunk* Hunk = ActiveMalady->GetHunk();
	if (Hunk)
	{
		Hunk->SetPortraitLive(true);
	}
	DialogueWidget->BindHunk(Hunk, ActiveMalady->HunkId);
	EnterState(EFixHimState::Dialogue);

	if (!Dialogue->StartConversation(ActiveMalady->HunkId))
	{
		HandleConversationEnded(ActiveMalady->HunkId, FString());
	}
}

void AFixHimPlayerController::AdvanceDialogue()
{
	if ((State != EFixHimState::Dialogue && State != EFixHimState::Cutscene) || !DialogueWidget)
	{
		return;
	}
	if (DialogueWidget->IsBusy() || DialogueWidget->TryCompleteTyping())
	{
		return;
	}
	FixHim::Sfx(this, "DialogueAdvance");
	if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		D->Advance();
	}
}

void AFixHimPlayerController::HandleDialogueView(const FDialogueView& View)
{
	if (DialogueWidget)
	{
		DialogueWidget->ShowView(View);
	}
}

void AFixHimPlayerController::HandleStatChanged(const FString& HunkId, ERelationshipAxis Axis, int32 Delta)
{
	if (DialogueWidget && DialogueWidget->IsInViewport())
	{
		DialogueWidget->OnStatChanged(HunkId, Axis, Delta);
	}
}

void AFixHimPlayerController::HandleConversationStarted(const FString& HunkId)
{
	MusicConvId = HunkId;
	UpdateMusic();
}

void AFixHimPlayerController::HandleConversationEnded(const FString& HunkId, const FString& EndingId)
{
	MusicConvId.Reset();
	if (!ActiveSceneId.IsEmpty() && HunkId == ActiveSceneId)
	{
		ActiveSceneId.Reset();
		PlayNextScene();
		return;
	}
	HideWidget(DialogueWidget);
	AFixHimMalady* Malady = ActiveMalady;
	ActiveMalady = nullptr;
	if (Malady)
	{
		if (AFixHimHunk* Hunk = Malady->GetHunk())
		{
			Hunk->SetPortraitLive(false);
		}
		Malady->RefreshRepairState();
	}
	SetViewTargetWithBlend(GetPawn(), 0.7f, VTBlend_EaseInOut, 2.f);
	RefreshRepairs();
	if (Malady)
	{
		// Neither he nor his fixture can be clicked while he says goodbye (the pause, the transition and a beat more).
		Malady->LockInteraction(2.4f);
		if (AFixHimHunk* Leaving = Malady->GetHunk())
		{
			Leaving->SetActorEnableCollision(false);
		}
		// He says goodbye once the dialogue box is gone.
		TWeakObjectPtr<AFixHimPlayerController> WeakSelf(this);
		TWeakObjectPtr<AFixHimMalady> WeakMalady(Malady);
		FTimerHandle PopTimer;
		GetWorldTimerManager().SetTimer(PopTimer, [WeakSelf, WeakMalady]()
		{
			if (WeakSelf.IsValid() && WeakMalady.IsValid() && WeakSelf->ActiveMalady != WeakMalady.Get())
			{
				WeakMalady->DismissHunk(true);
			}
		}, 0.35f, false);
	}

	const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	const FHunkDefinition* Def = Dialogue ? Dialogue->FindHunk(HunkId) : nullptr;
	if (!EndingId.IsEmpty() && Def)
	{
		EndingWidget = CreateWidget<UFixHimEndingCardWidget>(this, UFixHimEndingCardWidget::StaticClass());
		ShowWidget(EndingWidget, 35);
		EndingWidget->Setup(*Def, EndingId, Dialogue->CountFixedStoryHunks(), Dialogue->CountStoryHunks());
		EnterState(EFixHimState::Ending);
	}
	else
	{
		EnterState(EFixHimState::Playing);
	}
}

void AFixHimPlayerController::RefreshRepairs()
{
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	if (HUDWidget && Save && Dialogue)
	{
		HUDWidget->SetRepairs(Dialogue->CountFixedStoryHunks(), Dialogue->CountStoryHunks(), Save->Data().Week, UFixHimSettings::Get()->NumWeeks);
	}
}

void AFixHimPlayerController::HandleSaved()
{
	if (HUDWidget && State != EFixHimState::Title)
	{
		HUDWidget->ShowToast(TEXT("Saved"), 1.2f, false);
	}
}

void AFixHimPlayerController::HandlePreSave()
{
	UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const APawn* P = GetPawn();
	if (Save && P && State != EFixHimState::Title)
	{
		Save->Data().PlayerLocation = P->GetActorLocation();
		Save->Data().PlayerYaw = GetControlRotation().Yaw;
		Save->Data().bHasPlayerTransform = true;
		Save->Data().CurrentRoom = CurrentRoomId;
	}
}

// ---------------------------------------------------------------------------
// Rooms & floor plan

void AFixHimPlayerController::NotifyEnteredRoom(AFixHimRoom* Room)
{
	if (!Room || Room->RoomId == CurrentRoomId)
	{
		return;
	}
	CurrentRoomId = Room->RoomId;
	if (HUDWidget)
	{
		HUDWidget->SetRoomName(Room->DisplayName);
	}
}

void AFixHimPlayerController::NotifyLeftRoom(AFixHimRoom* Room)
{
	if (!Room)
	{
		return;
	}
	const APawn* Pawn = GetPawn();
	if (Pawn)
	{
		// Still inside another volume of the same room (e.g. stepping between a bedroom and its walk-in closet):
		// the player hasn't left, so nothing changes.
		for (TActorIterator<AFixHimRoom> It(GetWorld()); It; ++It)
		{
			if (*It != Room && It->RoomId == Room->RoomId && It->ContainsPoint(Pawn->GetActorLocation()))
			{
				return;
			}
		}
	}
	// He only exists while you're in his room: walk out and he's gone until you summon him again.
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		if (It->RoomId == Room->RoomId && It->IsHunkPresent() && *It != ActiveMalady)
		{
			It->DismissHunk();
		}
	}
	if (Room->RoomId == CurrentRoomId)
	{
		// We may already be overlapping a neighbour room (doorways).
		const APawn* P = GetPawn();
		for (TActorIterator<AFixHimRoom> It(GetWorld()); It; ++It)
		{
			if (*It != Room && P && It->ContainsPoint(P->GetActorLocation()))
			{
				CurrentRoomId.Reset();
				NotifyEnteredRoom(*It);
				return;
			}
		}
	}
}

void AFixHimPlayerController::ToggleFloorPlan()
{
	if (State == EFixHimState::FloorPlan)
	{
		HideWidget(FloorPlanWidget);
		FixHim::Sfx(this, "MapClose");
		EnterState(EFixHimState::Playing);
		return;
	}
	if (State != EFixHimState::Playing)
	{
		return;
	}
	if (!FloorPlanWidget)
	{
		FloorPlanWidget = CreateWidget<UFixHimFloorPlanWidget>(this, UFixHimFloorPlanWidget::StaticClass());
	}
	ShowWidget(FloorPlanWidget, 25);
	FixHim::Sfx(this, "MapOpen");
	FloorPlanWidget->Refresh();
	EnterState(EFixHimState::FloorPlan);
}

void AFixHimPlayerController::TravelToRoom(AFixHimRoom* Room)
{
	if (!Room || State != EFixHimState::FloorPlan)
	{
		return;
	}
	HideWidget(FloorPlanWidget);
	EnterState(EFixHimState::Traveling);
	if (PlayerCameraManager)
	{
		PlayerCameraManager->StartCameraFade(0.f, 1.f, 0.25f, FLinearColor(0.12f, 0.f, 0.08f), false, true);
	}
	TWeakObjectPtr<AFixHimRoom> WeakRoom(Room);
	GetWorldTimerManager().SetTimer(TravelTimer, [this, WeakRoom]()
	{
		if (WeakRoom.IsValid())
		{
			if (APawn* P = GetPawn())
			{
				const FTransform T = WeakRoom->GetEntryTransform();
				P->SetActorLocation(T.GetLocation(), false, nullptr, ETeleportType::TeleportPhysics);
				P->SetActorRotation(FRotator(0.f, T.Rotator().Yaw, 0.f));
				SetControlRotation(FRotator(-12.f, T.Rotator().Yaw, 0.f));
			}
		}
		if (PlayerCameraManager)
		{
			PlayerCameraManager->StartCameraFade(1.f, 0.f, 0.35f, FLinearColor(0.12f, 0.f, 0.08f), false, false);
		}
		EnterState(EFixHimState::Playing);
	}, 0.3f, false);
}

// ---------------------------------------------------------------------------
// Days: one playable day per week, a podcast each morning, bed to end the day

int32 AFixHimPlayerController::CurrentWeek() const
{
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	return Save ? Save->Data().Week : 1;
}

void AFixHimPlayerController::StartDay(bool bFromSave)
{
	if (CurrentWeek() > UFixHimSettings::Get()->NumWeeks)
	{
		// Quit during the finale last time: pick it back up.
		RunFinale();
		return;
	}
	DayElapsed = 0.f;
	bLateToastShown = false;
	UpdateDaylight(0.f);
	RefreshRepairs();

	if (!TransitionWidget)
	{
		TransitionWidget = CreateWidget<UFixHimTransitionWidget>(this, UFixHimTransitionWidget::StaticClass());
	}
	ShowWidget(TransitionWidget, 60);
	const int32 Week = CurrentWeek();
	const FString Sub = Week == 1 ? (bFromSave ? TEXT("Welcome back, homeowner.") : TEXT("Moving day. Thirty days until the hearing."))
		: (bFromSave ? TEXT("Welcome back, homeowner.") : TEXT("One week later..."));
	EnterState(EFixHimState::Sleeping);
	TWeakObjectPtr<AFixHimPlayerController> Self(this);
	TransitionWidget->Play(FString::Printf(TEXT("Week %d"), Week), Sub, true, true, nullptr, [Self, bFromSave]()
	{
		if (Self.IsValid())
		{
			Self->EnterState(EFixHimState::Playing);
			if (!bFromSave)
			{
				Self->StartPodcast();
			}
		}
	});
}

void AFixHimPlayerController::StartPodcast()
{
	UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	const FDialogueNode* Episode = Dialogue ? Dialogue->ResolveEntryNode(TEXT("podcast")) : nullptr;
	const FHunkDefinition* Show = Dialogue ? Dialogue->FindHunk(TEXT("podcast")) : nullptr;
	if (!Episode || !Show)
	{
		bPodcastPlaying = false;
		RefreshInteractionShine();
		return;
	}
	if (!RadioWidget)
	{
		RadioWidget = CreateWidget<UFixHimRadioWidget>(this, UFixHimRadioWidget::StaticClass());
	}
	ShowWidget(RadioWidget, 5);
	bPodcastPlaying = true;
	RefreshInteractionShine();
	if (HUDWidget)
	{
		HUDWidget->ShowToast(TEXT("The radio's on. You can explore, but nobody's talking until the episode ends."), 4.f);
	}
	TWeakObjectPtr<AFixHimPlayerController> Self(this);
	RadioWidget->Play(Show->Name + TEXT("  -  ") + Episode->Id.ToUpper().Replace(TEXT("EP"), TEXT("Episode ")), *Episode, [Self]()
	{
		if (Self.IsValid())
		{
			Self->bPodcastPlaying = false;
			Self->RefreshInteractionShine();
			if (Self->HUDWidget)
			{
				Self->HUDWidget->ShowToast(TEXT("That's the episode. Go say hi."), 3.f);
			}
		}
	});
}

void AFixHimPlayerController::UpdateDaylight(float DeltaTime)
{
	const UFixHimSettings* S = UFixHimSettings::Get();
	DayElapsed += DeltaTime;
	const float T = FMath::Clamp(DayElapsed / FMath::Max(1.f, S->DayLengthSeconds), 0.f, 1.f);

	if (Sun)
	{
		// Afternoon -> golden hour -> below the horizon. Interior lamps stay on, so the house gets cosy.
		const float Pitch = FMath::Lerp(SunBaseRotation.Pitch, 8.f, FMath::SmoothStep(0.f, 1.f, T));
		Sun->SetActorRotation(FRotator(Pitch, SunBaseRotation.Yaw + 25.f * T, SunBaseRotation.Roll));
		if (ULightComponent* LC = Sun->GetLightComponent())
		{
			LC->SetIntensity(SunBaseIntensity * FMath::Lerp(1.f, 0.02f, FMath::Pow(T, 1.4f)));
			const FLinearColor Golden(1.f, 0.62f, 0.35f);
			const FLinearColor Dusk(0.45f, 0.4f, 0.8f);
			LC->SetLightColor(T < 0.6f ? FMath::Lerp(SunBaseColor, Golden, T / 0.6f) : FMath::Lerp(Golden, Dusk, (T - 0.6f) / 0.4f));
		}
	}

	const float WindowBrightness = FMath::Lerp(12.f, 0.35f, FMath::Pow(T, 1.4f));
	for (UMaterialInstanceDynamic* View : WindowViews)
	{
		if (View) View->SetScalarParameterValue(TEXT("WindowBrightness"), WindowBrightness);
	}

	const float WindowSunFactor = T >= 1.f ? 0.f : FMath::Clamp((WindowBrightness - 0.35f) / (12.f - 0.35f), 0.f, 1.f);
	for (int32 Index = 0; Index < WindowSunLights.Num(); ++Index)
	{
		if (IsValid(WindowSunLights[Index]))
		{
			WindowSunLights[Index]->SetIntensity(WindowSunBaseIntensities[Index] * WindowSunFactor);
		}
	}

	if (!bLateToastShown && T >= S->LateWarningFraction && State == EFixHimState::Playing && HUDWidget)
	{
		bLateToastShown = true;
		HUDWidget->ShowToast(TEXT("It's getting late. End the day whenever you like by going to bed."), 6.f);
	}
}

bool AFixHimPlayerController::CanEndDay() const
{
	return CurrentWeek() != 1 || HaveMetEveryone();
}

bool AFixHimPlayerController::HaveMetEveryone() const
{
	const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	if (!Dialogue || !Save)
	{
		return true;
	}
	for (const auto& Pair : Dialogue->GetAllHunks())
	{
		if (!Pair.Value.IsHunk())
		{
			continue;
		}
		const FHunkProgress* P = Save->FindHunk(Pair.Key);
		if (!P || P->Visits < 1)
		{
			return false;
		}
	}
	return true;
}

void AFixHimPlayerController::RequestEndDay()
{
	if (State != EFixHimState::Playing)
	{
		return;
	}
	const int32 Week = CurrentWeek();
	if (!CanEndDay())
	{
		if (HUDWidget)
		{
			HUDWidget->ShowToast(TEXT("You feel a presence in the house... someone you still need to meet."), 3.5f);
		}
		return;
	}

	if (RadioWidget)
	{
		RadioWidget->Stop();
	}
	bPodcastPlaying = false;
	UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	const int32 NumWeeks = UFixHimSettings::Get()->NumWeeks;
	if (!TransitionWidget)
	{
		TransitionWidget = CreateWidget<UFixHimTransitionWidget>(this, UFixHimTransitionWidget::StaticClass());
	}
	ShowWidget(TransitionWidget, 60);
	EnterState(EFixHimState::Sleeping);
	TWeakObjectPtr<AFixHimPlayerController> Self(this);

	if (Week >= NumWeeks)
	{
		// Last night: the inspector comes in the morning.
		TransitionWidget->Play(TEXT("Inspection Day"), TEXT("Day 30. Inspector Dan is on his way."), false, true, [Self, Save]()
		{
			if (Save)
			{
				Save->Data().Week = UFixHimSettings::Get()->NumWeeks + 1;
				Save->SaveGame();
			}
			if (Self.IsValid())
			{
				Self->DayElapsed = 0.f;
				Self->UpdateDaylight(0.f);
			}
		}, [Self]()
		{
			if (Self.IsValid())
			{
				Self->RunFinale();
			}
		});
		return;
	}

	TransitionWidget->Play(FString::Printf(TEXT("Week %d"), Week + 1), TEXT("One week later..."), false, true, [Self, Save]()
	{
		if (!Self.IsValid())
		{
			return;
		}
		if (Save)
		{
			Save->Data().Week++;
		}
		// Every morning starts at the front door, with every hunk back in his fixture.
		for (TActorIterator<AFixHimMalady> It(Self->GetWorld()); It; ++It)
		{
			It->DismissHunk(false);
			It->RefreshRepairState();
		}
		Self->PlacePlayerAtDoor();
		Self->DayElapsed = 0.f;
		Self->bLateToastShown = false;
		Self->UpdateDaylight(0.f);
		Self->RefreshRepairs();
		if (Save)
		{
			Save->SaveGame();
		}
	}, [Self]()
	{
		if (Self.IsValid())
		{
			Self->EnterState(EFixHimState::Playing);
			Self->StartPodcast();
		}
	});
}

void AFixHimPlayerController::PlaySceneChain(TArray<FString> SceneIds, TFunction<void()> OnDone)
{
	SceneQueue = MoveTemp(SceneIds);
	SceneChainDone = MoveTemp(OnDone);
	PlayNextScene();
}

void AFixHimPlayerController::PlayNextScene()
{
	UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	while (SceneQueue.Num() > 0 && Dialogue)
	{
		const FString Id = SceneQueue[0];
		SceneQueue.RemoveAt(0);
		const FHunkDefinition* Def = Dialogue->FindHunk(Id);
		if (!Def)
		{
			continue;
		}
		if (!DialogueWidget)
		{
			DialogueWidget = CreateWidget<UFixHimDialogueWidget>(this, UFixHimDialogueWidget::StaticClass());
		}
		ShowWidget(DialogueWidget, 20);
		DialogueWidget->BindScript(Id, Def->Name);
		EnterState(EFixHimState::Cutscene);
		ActiveSceneId = Id;
		if (Dialogue->StartConversation(Id))
		{
			return;
		}
		ActiveSceneId.Reset();
	}
	HideWidget(DialogueWidget);
	TFunction<void()> Done = MoveTemp(SceneChainDone);
	SceneChainDone = nullptr;
	if (Done)
	{
		Done();
	}
}

void AFixHimPlayerController::RunFinale()
{
	// Inspector Dan, then (if the house passed) Bev & Trish live from the porch, then the epilogue.
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		It->DismissHunk(false);
	}
	const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	// The house passes inspection only when every story hunk is fixed.
	const bool bPassed = Dialogue && Dialogue->IsHouseFixed();
	UE_LOG(LogFixHim, Log, TEXT("Finale: %d/%d hunks fixed, inspection %s"), Dialogue ? Dialogue->CountFixedStoryHunks() : 0,
		Dialogue ? Dialogue->CountStoryHunks() : 0, bPassed ? TEXT("passes") : TEXT("fails"));
	TArray<FString> Scenes = { TEXT("inspection") };
	if (bPassed)
	{
		Scenes.Add(TEXT("podcast"));
	}
	Scenes.Add(TEXT("epilogue"));
	TWeakObjectPtr<AFixHimPlayerController> Self(this);
	PlaySceneChain(Scenes, [Self]()
	{
		if (Self.IsValid())
		{
			Self->ShowKeepsake();
		}
	});
}

void AFixHimPlayerController::ShowKeepsake()
{
	const UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	const UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	TArray<FFixHimKeepsakeEntry> Entries;
	if (Dialogue && Save)
	{
		for (const auto& Pair : Dialogue->GetAllHunks())
		{
			const FHunkProgress* P = Save->FindHunk(Pair.Key);
			if (!Pair.Value.IsHunk() || !P || !(P->Ending == TEXT("romance_success") || P->Ending == TEXT("romance_failure")))
			{
				continue;
			}
			FFixHimKeepsakeEntry E;
			E.HunkId = Pair.Key;
			E.Name = Pair.Value.Name;
			const FHunkEnding* Ending = Pair.Value.Endings.Find(P->Ending);
			E.EndingTitle = Ending ? Ending->Title : FString();
			for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
			{
				if (It->HunkId == Pair.Key)
				{
					E.Hunk = It->GetHunk();
				}
			}
			Entries.Add(E);
		}
	}
	if (Entries.IsEmpty())
	{
		FinishGame();
		return;
	}
	KeepsakeWidget = CreateWidget<UFixHimKeepsakeWidget>(this, UFixHimKeepsakeWidget::StaticClass());
	ShowWidget(KeepsakeWidget, 70);
	KeepsakeWidget->Setup(Entries);
	EnterState(EFixHimState::Finale);
}

// ---------------------------------------------------------------------------
// Debug & automation

void AFixHimPlayerController::FixHimNewGame(const FString& PlayerName)
{
	BeginNewGame(PlayerName.IsEmpty() ? FString(TEXT("Rosie")) : PlayerName);
}

void AFixHimPlayerController::FixHimContinue()
{
	ContinueGame();
}

void AFixHimPlayerController::FixHimTalk(const FString& HunkId)
{
	for (TActorIterator<AFixHimMalady> It(GetWorld()); It; ++It)
	{
		if (It->HunkId.Equals(HunkId, ESearchCase::IgnoreCase))
		{
			if (APawn* P = GetPawn())
			{
				P->SetActorLocation(It->GetTalkLocation(90.f), false, nullptr, ETeleportType::TeleportPhysics);
			}
			BeginEncounter(*It);
			return;
		}
	}
}

void AFixHimPlayerController::FixHimAdvance(int32 Times)
{
	if (State == EFixHimState::Encounter && IntroWidget && IntroWidget->IsWaitingForClick())
	{
		IntroWidget->ForceSkip(); // the first-meeting card waits for a click
		return;
	}
	for (int32 i = 0; i < FMath::Max(1, Times); ++i)
	{
		if (DialogueWidget)
		{
			DialogueWidget->TryCompleteTyping();
		}
		if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
		{
			D->Advance();
		}
	}
}

void AFixHimPlayerController::FixHimChoose(int32 OneBasedIndex)
{
	if (DialogueWidget)
	{
		DialogueWidget->TryCompleteTyping();
	}
	if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		D->Choose(OneBasedIndex - 1);
	}
}

void AFixHimPlayerController::FixHimTopic(const FString& Topic)
{
	if (UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this))
	{
		D->ClickTopic(Topic);
	}
}

void AFixHimPlayerController::FixHimAuto(const FString& Choices)
{
	UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this);
	if (!D)
	{
		return;
	}
	if (State == EFixHimState::Encounter && !D->IsActive())
	{
		// Still arriving (he's growing in, or the first-meeting card waits for a click): dismiss the card, then try
		// again until the conversation has started.
		if (IntroWidget && IntroWidget->IsWaitingForClick())
		{
			IntroWidget->ForceSkip();
		}
		FTimerHandle Retry;
		TWeakObjectPtr<AFixHimPlayerController> WeakSelf(this);
		GetWorldTimerManager().SetTimer(Retry, [WeakSelf, Choices]() { if (WeakSelf.IsValid()) { WeakSelf->FixHimAuto(Choices); } }, 0.25f, false);
		return;
	}
	TArray<FString> Picks;
	Choices.ParseIntoArray(Picks, TEXT(","), true);
	int32 PickIndex = 0;
	for (int32 Step = 0; Step < 300 && D->IsActive(); ++Step)
	{
		if (DialogueWidget)
		{
			DialogueWidget->TryCompleteTyping();
		}
		const FDialogueView& V = D->GetView();
		if (V.Choices.Num() > 0)
		{
			const int32 Pick = Picks.IsValidIndex(PickIndex) ? FCString::Atoi(*Picks[PickIndex]) : 1;
			UE_LOG(LogFixHim, Log, TEXT("Auto: '%s' -> choice %d"), *V.Text.Left(60), Pick);
			++PickIndex;
			D->Choose(FMath::Clamp(Pick, 1, V.Choices.Num()) - 1);
		}
		else
		{
			D->Advance();
		}
	}
}

void AFixHimPlayerController::FixHimClick()
{
	if (State == EFixHimState::Ending)
	{
		CloseEndingCard();
		return;
	}
	UpdateHover();
	OnInteract();
}

void AFixHimPlayerController::FixHimClickAt(float X, float Y)
{
	UGameViewportClient* GVC = GetWorld() ? GetWorld()->GetGameViewport() : nullptr;
	TSharedPtr<SViewport> Viewport = GVC ? GVC->GetGameViewportWidget() : nullptr;
	if (!Viewport.IsValid())
	{
		return;
	}
	const FGeometry& Geo = Viewport->GetCachedGeometry();
	const FVector2D Screen = Geo.LocalToAbsolute(Geo.GetLocalSize() * FVector2D(X, Y));
	// The topmost popup gets the click (same stacking as the Z orders used by ShowWidget).
	UFixHimWidget* Target = nullptr;
	for (UUserWidget* W : TArray<UUserWidget*>{ SubMenu.Get(), NameWidget.Get(), DoorWidget.Get(), EndingWidget.Get(), KeepsakeWidget.Get(),
		IntroWidget.Get(), PauseWidget.Get(), FloorPlanWidget.Get(), DialogueWidget.Get(), TitleWidget.Get() })
	{
		if (W && W->IsInViewport())
		{
			Target = Cast<UFixHimWidget>(W);
			break;
		}
	}
	const FString Result = Target ? Target->SimulateClickAt(Screen) : FString(TEXT("no screen to click"));
	UE_LOG(LogFixHim, Log, TEXT("ClickAt %.3f,%.3f on %s: %s"), X, Y, Target ? *Target->GetClass()->GetName() : TEXT("-"), *Result);
}

void AFixHimPlayerController::FixHimReturnToTitle()
{
	ReturnToMainMenu();
}

void AFixHimPlayerController::FixHimPause(bool bPause)
{
	SetPaused(bPause);
}

void AFixHimPlayerController::FixHimOptions()
{
	OpenOptions();
}

void AFixHimPlayerController::FixHimSleep()
{
	RequestEndDay();
}

void AFixHimPlayerController::FixHimSkipTime(float Seconds)
{
	UpdateDaylight(Seconds);
}

void AFixHimPlayerController::FixHimSkipPodcast()
{
	if (RadioWidget)
	{
		RadioWidget->Stop();
	}
	bPodcastPlaying = false;
	RefreshInteractionShine();
}

void AFixHimPlayerController::FixHimNamePrompt()
{
	StartNewGame();
}

void AFixHimPlayerController::FixHimKeepsake(int32 Index)
{
	if (KeepsakeWidget)
	{
		KeepsakeWidget->ShowPortrait(Index);
	}
}

void AFixHimPlayerController::FixHimMap()
{
	ToggleFloorPlan();
}

void AFixHimPlayerController::FixHimGoto(const FString& RoomId)
{
	for (TActorIterator<AFixHimRoom> It(GetWorld()); It; ++It)
	{
		if (!It->bSubVolume && It->RoomId.Equals(RoomId, ESearchCase::IgnoreCase))
		{
			if (State == EFixHimState::Playing)
			{
				ToggleFloorPlan();
			}
			TravelToRoom(*It);
			return;
		}
	}
}

void AFixHimPlayerController::FixHimLook(float Yaw, float Pitch)
{
	SetControlRotation(FRotator(Pitch, Yaw, 0.f));
}

void AFixHimPlayerController::FixHimShot(const FString& Name)
{
	const FString Path = FPaths::ProjectSavedDir() / TEXT("Screenshots") / TEXT("FixHim") / (Name + TEXT(".png"));
	FScreenshotRequest::RequestScreenshot(Path, true, false);
	UE_LOG(LogFixHim, Log, TEXT("Screenshot requested: %s"), *Path);
}

void AFixHimPlayerController::FixHimScene(const FString& SceneIds)
{
	TArray<FString> Ids;
	SceneIds.ParseIntoArray(Ids, TEXT(","), true);
	TWeakObjectPtr<AFixHimPlayerController> Self(this);
	PlaySceneChain(Ids, [Self]()
	{
		if (Self.IsValid())
		{
			Self->EnterState(EFixHimState::Playing);
		}
	});
}

void AFixHimPlayerController::FixHimSetFixed(const FString& HunkId, int32 Fixed)
{
	UFixHimDialogueSubsystem* Dialogue = UFixHimDialogueSubsystem::Get(this);
	UFixHimSaveSubsystem* Save = UFixHimSaveSubsystem::Get(this);
	if (!Dialogue || !Save)
	{
		return;
	}
	for (const auto& Pair : Dialogue->GetAllHunks())
	{
		if (Pair.Value.IsHunk() && (HunkId.Equals(TEXT("all"), ESearchCase::IgnoreCase) || HunkId.Equals(Pair.Key, ESearchCase::IgnoreCase)))
		{
			Save->Hunk(Pair.Key).bFixed = Fixed != 0;
		}
	}
	RefreshRepairs();
	UE_LOG(LogFixHim, Log, TEXT("FixHimSetFixed: fixedcount=%d storycount=%d house %s"), Dialogue->CountFixedStoryHunks(),
		Dialogue->CountStoryHunks(), Dialogue->IsHouseFixed() ? TEXT("passes") : TEXT("fails"));
}

void AFixHimPlayerController::FixHimDump()
{
	const UFixHimDialogueSubsystem* D = UFixHimDialogueSubsystem::Get(this);
	const UFixHimSaveSubsystem* S = UFixHimSaveSubsystem::Get(this);
	UE_LOG(LogFixHim, Log, TEXT("State=%d Room=%s Hovered=%s"), int32(State), *CurrentRoomId, *GetNameSafe(Hovered));
	if (D && D->IsActive())
	{
		const FDialogueView& V = D->GetView();
		UE_LOG(LogFixHim, Log, TEXT("Dialogue %s/%s#%d%s fx=%s: '%s' choices=%d topics=[%s]"), *V.HunkId, *V.NodeId, V.LineIndex,
			V.bIsReturn ? TEXT(" (resumed)") : TEXT(""), *V.Fx, *V.Text, V.Choices.Num(), *FString::Join(V.ActiveTopics, TEXT(",")));
	}
	if (S)
	{
		for (const auto& Pair : S->Data().Hunks)
		{
			UE_LOG(LogFixHim, Log, TEXT("  %s: R%d F%d X%d visits=%d met=%d fixed=%d ending=%s"), *Pair.Key, Pair.Value.Romance, Pair.Value.Friendship, Pair.Value.Friction, Pair.Value.Visits, Pair.Value.bMet, Pair.Value.bFixed, *Pair.Value.Ending);
		}
	}
}

void AFixHimPlayerController::FixHimScript(const FString& Script)
{
	Script.ParseIntoArray(ScriptSteps, TEXT(";"), true);
	for (FString& Step : ScriptSteps)
	{
		Step.TrimStartAndEndInline();
	}
	RunNextScriptStep();
}

void AFixHimPlayerController::RunNextScriptStep()
{
	while (ScriptSteps.Num() > 0)
	{
		const FString Step = ScriptSteps[0];
		ScriptSteps.RemoveAt(0);
		if (Step.StartsWith(TEXT("wait ")))
		{
			const float Seconds = FCString::Atof(*Step.RightChop(5));
			GetWorldTimerManager().SetTimer(ScriptTimer, this, &AFixHimPlayerController::RunNextScriptStep, FMath::Max(0.01f, Seconds), false);
			return;
		}
		UE_LOG(LogFixHim, Log, TEXT("Script: %s"), *Step);
		ConsoleCommand(Step, true);
	}
}
