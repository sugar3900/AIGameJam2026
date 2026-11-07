// I Can Fix Him - AI Game Jam 2026

#include "Player/FixHimCharacter.h"
#include "Core/FixHimAssets.h"
#include "Core/FixHimSettings.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

AFixHimCharacter::AFixHimCharacter()
{
	GetCapsuleComponent()->InitCapsuleSize(38.f, 90.f);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Move = GetCharacterMovement();
	Move->bOrientRotationToMovement = true;
	Move->RotationRate = FRotator(0.f, 540.f, 0.f);
	Move->MaxWalkSpeed = 360.f;
	Move->MinAnalogWalkSpeed = 20.f;
	Move->BrakingDecelerationWalking = 2000.f;
	Move->JumpZVelocity = 420.f;

	GetMesh()->SetRelativeLocation(FVector(0.f, 0.f, -90.f));
	GetMesh()->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 290.f;
	CameraBoom->SocketOffset = FVector(0.f, 55.f, 45.f);
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->ProbeSize = 14.f;
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 12.f;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;
	FollowCamera->SetFieldOfView(80.f);
}

void AFixHimCharacter::BeginPlay()
{
	Super::BeginPlay();

	const UFixHimSettings* S = UFixHimSettings::Get();
	if (USkeletalMesh* Mesh = S->PlayerMesh.LoadSynchronous())
	{
		GetMesh()->SetSkeletalMesh(Mesh);
	}
	if (UClass* Anim = S->LocomotionAnimClass.LoadSynchronous())
	{
		GetMesh()->SetAnimInstanceClass(Anim);
	}
	GetMesh()->RefreshBoneTransforms();
	DressUp();
}

void AFixHimCharacter::DressUp()
{
	// Rosie the renovator: denim work shirt, rolled jeans, red bandana with a bow, tool belt.
	FixHim::Assets::FOutfit Outfit;
	Outfit.Skin = SkinColor;
	Outfit.Shirt = ShirtColor;
	Outfit.Pants = PantsColor;
	Outfit.Shoes = FLinearColor(0.85f, 0.85f, 0.82f);
	FixHim::Assets::ApplyOutfit(GetMesh(), Outfit);
	FixHim::Assets::AddEyes(this);

	const FLinearColor Red(0.75f, 0.05f, 0.08f);
	using FixHim::Assets::AddBodyProp;
	AddBodyProp(this, TEXT("sphere"), FVector(-1.f, 0.f, 172.f), FVector(22.f, 21.f, 10.f), Red, TEXT("head"));
	AddBodyProp(this, TEXT("sphere"), FVector(-2.f, -4.f, 178.f), FVector(6.f, 6.f, 6.f), Red, TEXT("head"));
	AddBodyProp(this, TEXT("sphere"), FVector(-2.f, -9.f, 180.f), FVector(5.f, 8.f, 5.f), Red, TEXT("head"), FRotator(0.f, 0.f, 25.f));
	AddBodyProp(this, TEXT("sphere"), FVector(-2.f, 1.f, 180.f), FVector(5.f, 8.f, 5.f), Red, TEXT("head"), FRotator(0.f, 0.f, -25.f));
	AddBodyProp(this, TEXT("sphere"), FVector(-3.f, 0.f, 166.f), FVector(20.f, 20.f, 22.f), HairColor, TEXT("head"));
	AddBodyProp(this, TEXT("cylinder"), FVector(0.f, 0.f, 99.f), FVector(32.f, 28.f, 6.f), FLinearColor(0.35f, 0.2f, 0.1f), TEXT("pelvis"));
	AddBodyProp(this, TEXT("cube"), FVector(3.f, 14.f, 94.f), FVector(4.f, 7.f, 12.f), FLinearColor(0.6f, 0.6f, 0.65f), TEXT("pelvis"));
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
