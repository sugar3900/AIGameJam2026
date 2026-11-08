// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimPuffFx.h"
#include "Core/FixHimAssets.h"
#include "Core/FixHimSettings.h"
#include "Components/MaterialBillboardComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"

AFixHimPuffFx::AFixHimPuffFx()
{
	PrimaryActorTick.bCanEverTick = true;
	// Real-time feel even if something pauses the world mid-burst (it's only a second long).
	PrimaryActorTick.bTickEvenWhenPaused = true;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	SetActorEnableCollision(false);
}

AFixHimPuffFx* AFixHimPuffFx::Spawn(UWorld* World, const FVector& Location, const FLinearColor& Color, EFixHimPuffStyle Style, float Size)
{
	if (!World)
	{
		return nullptr;
	}
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AFixHimPuffFx* Fx = World->SpawnActor<AFixHimPuffFx>(AFixHimPuffFx::StaticClass(), FTransform(Location), Params);
	if (Fx)
	{
		Fx->Build(Color, Style, Size);
	}
	return Fx;
}

void AFixHimPuffFx::Build(const FLinearColor& Color, EFixHimPuffStyle InStyle, float Size)
{
	Style = InStyle;
	if (Style == EFixHimPuffStyle::SurgeIn || Style == EFixHimPuffStyle::SurgeOut)
	{
		BuildSurge(Color, Size);
		return;
	}
	if (Style == EFixHimPuffStyle::SporesIn || Style == EFixHimPuffStyle::SporesOut)
	{
		BuildSpores(Style == EFixHimPuffStyle::SporesIn, Size);
		return;
	}
	// Burst (ring flying outward) when leaving, spiral (rising out of the fixture) when arriving.
	const bool bPop = Style == EFixHimPuffStyle::BubblePop || Style == EFixHimPuffStyle::SparkleOut;
	const bool bGlitterOnly = Style == EFixHimPuffStyle::SparkleIn || Style == EFixHimPuffStyle::SparkleOut;
	Lifetime = bPop ? 1.4f : 1.9f;
	FRandomStream Rng(FMath::Rand());

	UMaterialInterface* SparkleMat = UFixHimSettings::Get()->SparkleMaterial.LoadSynchronous();
	const FLinearColor SparkleColor = FMath::Lerp(Color, FLinearColor::White, 0.45f);

	// Sparkles: additive twinkle sprites. Each gets its own instance so it can fade on its own.
	const int32 NumSparkles = bGlitterOnly ? (bPop ? 36 : 34) : (bPop ? 20 : 18);
	for (int32 i = 0; SparkleMat && i < NumSparkles; ++i)
	{
		UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(SparkleMat, this);
		MID->SetVectorParameterValue(TEXT("Color"), i % 3 == 0 ? FLinearColor(1.f, 0.95f, 0.8f) : SparkleColor);
		UMaterialBillboardComponent* Sprite = NewObject<UMaterialBillboardComponent>(this);
		Sprite->SetupAttachment(GetRootComponent());
		Sprite->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Sprite->SetCastShadow(false);
		FParticle P;
		P.BaseSize = (bPop ? Rng.FRandRange(14.f, 26.f) : Rng.FRandRange(16.f, 30.f)) * Size;
		Sprite->AddElement(MID, nullptr, false, P.BaseSize, P.BaseSize, nullptr);
		Sprite->RegisterComponent();
		P.Comp = Sprite;
		if (bPop)
		{
			// A ring bursting outward around the body, a touch upward, slowing with drag.
			const FVector Dir = FVector(Rng.FRandRange(-1.f, 1.f), Rng.FRandRange(-1.f, 1.f), Rng.FRandRange(-0.4f, 1.f)).GetSafeNormal();
			P.Velocity = Dir * Rng.FRandRange(160.f, 300.f) * Size;
			P.Life = Rng.FRandRange(0.55f, 0.95f);
			P.Delay = Rng.FRandRange(0.f, 0.06f);
			Sprite->SetRelativeLocation(Dir * 20.f * Size);
		}
		else
		{
			// A slow upward spiral out of the fixture.
			const float Angle = (i / float(NumSparkles)) * 2.f * PI * 2.f;
			const float Radius = Rng.FRandRange(18.f, 40.f) * Size;
			Sprite->SetRelativeLocation(FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, Rng.FRandRange(-20.f, 20.f) * Size));
			P.Velocity = FVector(0.f, 0.f, Rng.FRandRange(50.f, 110.f) * Size);
			P.Spin = Rng.FRandRange(1.6f, 2.6f) * (Rng.FRand() < 0.5f ? -1.f : 1.f);
			P.Life = Rng.FRandRange(0.9f, 1.4f);
			P.Delay = Rng.FRandRange(0.f, 0.45f);
			P.Phase = Angle;
		}
		Sprite->SetVisibility(P.Delay <= 0.f);
		Parts.Add(Sprite);
		Particles.Add(P);
	}

	// Bubbles: glassy pink spheres that drift up, wobble, swell and pop.
	// Glossy candy-pink bubbles with a soft glow (an unlit translucent sphere reads as a grey smudge under this scene's
	// exposure and painterly post-process), each with a bright white glint.
	// His glow colour, softened towards bubblegum pink so every hunk's bubbles stay cute.
	const FLinearColor BubbleColor = FMath::Lerp(FMath::Lerp(Color, FLinearColor::White, 0.45f), FLinearColor(1.f, 0.62f, 0.82f), 0.5f);
	// Transparent, like soap film: a bright tint at low opacity (the glint below carries the highlight).
	BubbleMID = FixHim::Assets::MakeTranslucent(this, BubbleColor * 2.4f, 0.26f);
	UMaterialInstanceDynamic* GlintMID = FixHim::Assets::MakeFlat(this, FLinearColor::White, FLinearColor::White * 3.f, 0.1f);
	UStaticMesh* Sphere = FixHim::Assets::ShapeMesh(TEXT("sphere"));
	const int32 NumBubbles = bGlitterOnly ? 0 : (bPop ? 9 : 5);
	for (int32 i = 0; Sphere && i < NumBubbles; ++i)
	{
		UStaticMeshComponent* Bubble = NewObject<UStaticMeshComponent>(this);
		Bubble->SetupAttachment(GetRootComponent());
		Bubble->SetStaticMesh(Sphere);
		Bubble->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Bubble->SetCastShadow(false);
		Bubble->SetMaterial(0, BubbleMID);
		Bubble->RegisterComponent();
		FParticle P;
		P.Comp = Bubble;
		P.bBubble = true;
		P.BaseSize = Rng.FRandRange(6.f, 13.f) * Size;
		const FVector Offset(Rng.FRandRange(-35.f, 35.f), Rng.FRandRange(-35.f, 35.f), Rng.FRandRange(-50.f, 40.f));
		Bubble->SetRelativeLocation(Offset * Size);
		P.Velocity = FVector(Offset.X * 0.6f, Offset.Y * 0.6f, Rng.FRandRange(45.f, 95.f)) * Size;
		P.Delay = bPop ? Rng.FRandRange(0.f, 0.12f) : Rng.FRandRange(0.2f, 0.6f);
		P.PopAt = Rng.FRandRange(0.55f, 1.15f);
		P.Life = P.PopAt + 0.09f;
		P.Phase = Rng.FRandRange(0.f, 2.f * PI);
		Bubble->SetRelativeScale3D(FVector(0.001f));
		// A little white glint up and to one side, so it reads as a soap bubble rather than a disc.
		UStaticMeshComponent* Glint = NewObject<UStaticMeshComponent>(this);
		Glint->SetupAttachment(Bubble);
		Glint->SetStaticMesh(Sphere);
		Glint->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Glint->SetCastShadow(false);
		Glint->SetMaterial(0, GlintMID);
		Glint->SetRelativeLocation(FVector(-30.f, -22.f, 26.f));
		Glint->SetRelativeScale3D(FVector(0.22f));
		Glint->RegisterComponent();
		Parts.Add(Glint);
		Parts.Add(Bubble);
		Particles.Add(P);
	}
}

void AFixHimPuffFx::BuildSurge(const FLinearColor& Color, float Size)
{
	Lifetime = 1.0f;
	SurgeSize = Size;
	FRandomStream Rng(FMath::Rand());
	UStaticMesh* Cube = FixHim::Assets::ShapeMesh(TEXT("cube"));
	// Bright blue-white bolts with the odd one in the character's own colour (yellow for wiring).
	const FLinearColor Electric(0.55f, 0.8f, 1.f);
	UMaterialInstanceDynamic* BlueMID = FixHim::Assets::MakeFlat(this, Electric, Electric * 40.f, 0.2f);
	UMaterialInstanceDynamic* WarmMID = FixHim::Assets::MakeFlat(this, FMath::Lerp(Color, FLinearColor::White, 0.5f), FMath::Lerp(Color, FLinearColor::White, 0.5f) * 40.f, 0.2f);
	const int32 NumBolts = 34;
	for (int32 i = 0; Cube && i < NumBolts; ++i)
	{
		UStaticMeshComponent* Bolt = NewObject<UStaticMeshComponent>(this);
		Bolt->SetupAttachment(GetRootComponent());
		Bolt->SetStaticMesh(Cube);
		Bolt->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Bolt->SetCastShadow(false);
		Bolt->SetMaterial(0, i % 4 == 0 ? WarmMID : BlueMID);
		Bolt->RegisterComponent();
		FParticle P;
		P.Comp = Bolt;
		P.bSurge = true;
		P.Delay = Rng.FRandRange(0.f, 0.35f);
		P.Life = Lifetime - P.Delay - 0.05f;
		P.NextStrike = 0.f;
		Bolt->SetRelativeScale3D(FVector(0.001f));
		Parts.Add(Bolt);
		Particles.Add(P);
	}
	SurgeLight = NewObject<UPointLightComponent>(this);
	SurgeLight->SetupAttachment(GetRootComponent());
	SurgeLight->SetLightColor(Electric);
	SurgeLight->SetAttenuationRadius(420.f * Size);
	SurgeLight->SetCastShadows(false);
	SurgeLight->SetIntensity(0.f);
	SurgeLight->RegisterComponent();
	Parts.Add(SurgeLight);
}

void AFixHimPuffFx::BuildSpores(bool bIn, float Size)
{
	Lifetime = bIn ? 2.9f : 2.5f;
	FRandomStream Rng(FMath::Rand());
	UStaticMesh* Sphere = FixHim::Assets::ShapeMesh(TEXT("sphere"));
	if (!Sphere)
	{
		return;
	}
	// Near-black with a sickly green cast, matte so lighting can't make it glossy or pretty.
	UMaterialInstanceDynamic* SporeMID = FixHim::Assets::MakeFlat(this, FLinearColor(0.012f, 0.018f, 0.012f), FLinearColor::Black, 1.f);
	UMaterialInstanceDynamic* SmokeMID = FixHim::Assets::MakeTranslucent(this, FLinearColor(0.004f, 0.007f, 0.004f), 0.55f);

	// Soft smoky blobs that swell, giving the cloud its body.
	const int32 NumBlobs = bIn ? 26 : 22;
	for (int32 i = 0; SmokeMID && i < NumBlobs; ++i)
	{
		UStaticMeshComponent* Blob = NewObject<UStaticMeshComponent>(this);
		Blob->SetupAttachment(GetRootComponent());
		Blob->SetStaticMesh(Sphere);
		Blob->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Blob->SetCastShadow(false);
		Blob->SetMaterial(0, SmokeMID);
		Blob->RegisterComponent();
		FParticle P;
		P.Comp = Blob;
		P.bSpore = P.bBlob = true;
		P.BaseSize = Rng.FRandRange(24.f, 52.f) * Size;
		const FVector Dir = FVector(Rng.FRandRange(-1.f, 1.f), Rng.FRandRange(-1.f, 1.f), Rng.FRandRange(-0.3f, 0.6f)).GetSafeNormal();
		// Spread up and down his whole body so he is wrapped in cloud, not just puffed at the middle.
		Blob->SetRelativeLocation(FVector(Dir.X * 20.f, Dir.Y * 20.f, Rng.FRandRange(-85.f, 100.f)) * Size);
		P.Velocity = Dir * Rng.FRandRange(30.f, 80.f) * Size;
		P.Rise = Rng.FRandRange(8.f, 22.f) * Size;
		P.Delay = Rng.FRandRange(0.f, bIn ? 0.5f : 0.25f);
		P.Life = Rng.FRandRange(1.5f, 2.2f);
		P.Phase = Rng.FRandRange(0.f, 2.f * PI);
		Blob->SetRelativeScale3D(FVector(0.001f));
		Parts.Add(Blob);
		Particles.Add(P);
	}

	// The spores themselves: lots of small dark specks flung out and left hanging in the air.
	const int32 NumSpores = bIn ? 110 : 120;
	for (int32 i = 0; SporeMID && i < NumSpores; ++i)
	{
		UStaticMeshComponent* Spore = NewObject<UStaticMeshComponent>(this);
		Spore->SetupAttachment(GetRootComponent());
		Spore->SetStaticMesh(Sphere);
		Spore->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Spore->SetCastShadow(false);
		Spore->SetMaterial(0, SporeMID);
		Spore->RegisterComponent();
		FParticle P;
		P.Comp = Spore;
		P.bSpore = true;
		P.BaseSize = Rng.FRandRange(1.6f, 5.5f) * Size;
		const FVector Dir = FVector(Rng.FRandRange(-1.f, 1.f), Rng.FRandRange(-1.f, 1.f), Rng.FRandRange(-0.6f, 1.f)).GetSafeNormal();
		Spore->SetRelativeLocation(FVector(Dir.X * 14.f, Dir.Y * 14.f, Rng.FRandRange(-85.f, 100.f)) * Size);
		P.Velocity = Dir * Rng.FRandRange(60.f, 190.f) * Size;
		P.Rise = Rng.FRandRange(6.f, 26.f) * Size;
		P.Delay = Rng.FRandRange(0.f, bIn ? 0.6f : 0.15f);
		P.Life = Rng.FRandRange(1.1f, 2.0f);
		P.Phase = Rng.FRandRange(0.f, 2.f * PI);
		Spore->SetRelativeScale3D(FVector(0.001f));
		Parts.Add(Spore);
		Particles.Add(P);
	}
}

void AFixHimPuffFx::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Age += DeltaSeconds;
	const bool bPop = Style == EFixHimPuffStyle::BubblePop || Style == EFixHimPuffStyle::SparkleOut;

	for (FParticle& P : Particles)
	{
		USceneComponent* C = P.Comp;
		if (!C)
		{
			continue;
		}
		const float T = Age - P.Delay;
		if (T < 0.f)
		{
			continue;
		}
		const float U = T / P.Life;
		if (U >= 1.f)
		{
			if (C->IsVisible())
			{
				C->SetVisibility(false, true);
			}
			continue;
		}
		if (!P.bSurge && !C->IsVisible())
		{
			C->SetVisibility(true, true);
		}

		FVector Loc = C->GetRelativeLocation();
		if (P.bSurge)
		{
			// A bolt that keeps re-striking somewhere new, flickering, and is gone as the surge ends.
			if (T >= P.NextStrike)
			{
				P.NextStrike = T + FMath::FRandRange(0.03f, 0.09f);
				const float S = SurgeSize;
				C->SetRelativeLocation(FVector(FMath::FRandRange(-42.f, 42.f), FMath::FRandRange(-42.f, 42.f), FMath::FRandRange(-88.f, 95.f)) * S);
				C->SetRelativeRotation(FRotator(FMath::FRandRange(0.f, 360.f), FMath::FRandRange(0.f, 360.f), FMath::FRandRange(0.f, 360.f)));
				const float Len = FMath::FRandRange(0.25f, 1.1f) * S;
				C->SetRelativeScale3D(FVector(0.012f, 0.012f, Len));
				C->SetVisibility(FMath::FRand() < 0.78f, true);
			}
			continue;
		}
		if (P.bSpore)
		{
			// Billow out, slow right down, then hang and drift up while shrinking away.
			P.Velocity *= FMath::Exp(-1.9f * DeltaSeconds);
			P.Velocity.Z += P.Rise * DeltaSeconds;
			Loc += P.Velocity * DeltaSeconds + FVector(FMath::Sin(T * 3.1f + P.Phase), FMath::Cos(T * 2.7f + P.Phase), 0.f) * 9.f * DeltaSeconds;
			C->SetRelativeLocation(Loc);
			const float Grow = FMath::Sin(FMath::Clamp(T / 0.22f, 0.f, 1.f) * HALF_PI);
			const float Fade = 1.f - FMath::Clamp((U - 0.45f) / 0.55f, 0.f, 1.f);
			const float Swell = P.bBlob ? 1.f + 0.9f * U : 1.f;
			C->SetRelativeScale3D(FVector(FMath::Max(0.001f, P.BaseSize / 100.f * Grow * Fade * Swell)));
			continue;
		}
		if (P.bBubble)
		{
			// Rise with a lazy side-to-side wobble, slowing down.
			P.Velocity *= FMath::Exp(-1.2f * DeltaSeconds);
			Loc += P.Velocity * DeltaSeconds + FVector(FMath::Sin(T * 7.f + P.Phase), FMath::Cos(T * 6.f + P.Phase), 0.f) * 12.f * DeltaSeconds;
			C->SetRelativeLocation(Loc);
			// Grow in, then at PopAt swell quickly and vanish.
			const float Grow = FMath::Clamp(T / 0.18f, 0.f, 1.f);
			const float Swell = T > P.PopAt ? 1.f + 0.7f * ((T - P.PopAt) / 0.09f) : 1.f + 0.05f * FMath::Sin(T * 11.f + P.Phase);
			const float Scale = P.BaseSize / 100.f * FMath::Sin(Grow * HALF_PI) * Swell;
			C->SetRelativeScale3D(FVector(FMath::Max(0.001f, Scale)));
		}
		else
		{
			if (bPop)
			{
				P.Velocity *= FMath::Exp(-4.f * DeltaSeconds);
				P.Velocity.Z -= 60.f * DeltaSeconds; // a little float back down
				Loc += P.Velocity * DeltaSeconds;
			}
			else
			{
				// Spiral: rotate around the vertical axis while rising.
				const FVector2D XY(Loc.X, Loc.Y);
				const float Radius = XY.Size() * (1.f + 0.25f * DeltaSeconds);
				const float Angle = FMath::Atan2(XY.Y, XY.X) + P.Spin * DeltaSeconds;
				Loc = FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, Loc.Z + P.Velocity.Z * DeltaSeconds);
			}
			C->SetRelativeLocation(Loc);
			// Twinkle in fast, shrink out.
			const float In = FMath::Clamp(U / 0.15f, 0.f, 1.f);
			const float Out = 1.f - FMath::Clamp((U - 0.45f) / 0.55f, 0.f, 1.f);
			const float Size = P.BaseSize * FMath::Max(0.05f, In * Out * (1.f + 0.25f * FMath::Sin(T * 18.f + P.Phase)));
			if (UMaterialBillboardComponent* Sprite = Cast<UMaterialBillboardComponent>(C))
			{
				TArray<FMaterialSpriteElement> Elements = Sprite->Elements;
				if (Elements.Num() > 0)
				{
					Elements[0].BaseSizeX = Elements[0].BaseSizeY = Size;
					Sprite->SetElements(Elements);
				}
			}
		}
	}

	if (SurgeLight)
	{
		const float Fade = 1.f - FMath::Clamp((Age - 0.55f) / 0.45f, 0.f, 1.f);
		SurgeLight->SetIntensity(FMath::FRand() < 0.7f ? FMath::FRandRange(2500.f, 9000.f) * Fade : 0.f);
	}
	if (Age >= Lifetime)
	{
		Destroy();
	}
}
