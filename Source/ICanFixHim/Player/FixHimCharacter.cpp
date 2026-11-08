// I Can Fix Him - AI Game Jam 2026

#include "Player/FixHimCharacter.h"
#include "Audio/FixHimSfxSubsystem.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

AFixHimCharacter::AFixHimCharacter()
{
	GetCapsuleComponent()->InitCapsuleSize(38.f, 90.f);

	// First person: the body always faces where the camera looks; there is no mesh to turn.
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = true;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Move = GetCharacterMovement();
	Move->bOrientRotationToMovement = false;
	Move->MaxWalkSpeed = 360.f;
	Move->MinAnalogWalkSpeed = 20.f;
	Move->BrakingDecelerationWalking = 2000.f;
	Move->JumpZVelocity = 0.f;

	// Always at floor height: never step up onto props or climb slopes.
	Move->MaxStepHeight = 0.f;
	Move->SetWalkableFloorAngle(5.f);
	Move->bUseFlatBaseForFloorChecks = true;

	// Nobody sees Rosie; the inherited mesh component stays empty.
	GetMesh()->SetVisibility(false);
	GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -90.f));

	// Eye height: ~160cm above the floor (capsule centre is 90cm up).
	FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
	FirstPersonCamera->SetupAttachment(GetCapsuleComponent());
	FirstPersonCamera->SetRelativeLocation(FVector(0.f, 0.f, 70.f));
	FirstPersonCamera->bUsePawnControlRotation = true;
	FirstPersonCamera->SetFieldOfView(80.f);
}

void AFixHimCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Soft footsteps timed by distance walked, so they follow her speed (and stop when she does).
	const UCharacterMovementComponent* Move = GetCharacterMovement();
	const float Speed = GetVelocity().Size2D();
	if (!Move->IsMovingOnGround() || Speed < 40.f)
	{
		StepDistance = FMath::Min(StepDistance, NextStepDistance * 0.5f);
		return;
	}
	StepDistance += Speed * DeltaSeconds;
	if (StepDistance >= NextStepDistance)
	{
		StepDistance = 0.f;
		NextStepDistance = FMath::FRandRange(125.f, 155.f);
		FixHim::Sfx(this, "Footstep", FMath::FRandRange(0.35f, 0.5f), 0.08f);
	}
}

void AFixHimCharacter::DoMove(float Right, float Forward)
{
	if (Controller)
	{
		const FRotator YawRotation(0.f, Controller->GetControlRotation().Yaw, 0.f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Forward);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Right);
	}
}

void AFixHimCharacter::DoLook(float Yaw, float Pitch)
{
	if (Controller)
	{
		AddControllerYawInput(Yaw);
		AddControllerPitchInput(Pitch);
	}
}
