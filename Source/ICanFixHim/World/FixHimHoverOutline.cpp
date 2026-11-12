// I Can Fix Him - AI Game Jam 2026

#include "World/FixHimHoverOutline.h"
#include "ICanFixHim.h"
#include "World/FixHimInteractable.h"
#include "Core/FixHimSettings.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"

UFixHimHoverOutlineSubsystem* UFixHimHoverOutlineSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	return World ? World->GetSubsystem<UFixHimHoverOutlineSubsystem>() : nullptr;
}

bool UFixHimHoverOutlineSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

bool UFixHimHoverOutlineSubsystem::EnsureVolume()
{
	if (Volume && MID)
	{
		return true;
	}
	if (bMissingMaterial)
	{
		return false;
	}
	const UFixHimSettings* Settings = UFixHimSettings::Get();
	UMaterialInterface* Material = Settings->HoverOutlineMaterial.LoadSynchronous();
	if (!Material)
	{
		bMissingMaterial = true;
		UE_LOG(LogFixHim, Warning, TEXT("[FixHim] HoverOutlineMaterial is not set or failed to load; hover outlines are off."));
		return false;
	}

	MID = UMaterialInstanceDynamic::Create(Material, this);
	MID->SetScalarParameterValue(TEXT("WidthPx"), Settings->HoverOutlineWidthPixels);
	MID->SetScalarParameterValue(TEXT("Intensity"), Settings->HoverOutlineIntensity);
	MID->SetScalarParameterValue(TEXT("Inside"), Settings->bHoverOutlineInside ? 1.f : 0.f);
	MID->SetScalarParameterValue(TEXT("StencilRef"), float(Settings->OutlineStencilValue));

	FActorSpawnParameters Params;
	Params.Name = TEXT("FixHimHoverOutlineVolume");
	Params.NameMode = FActorSpawnParameters::ESpawnActorNameMode::Requested;
	Params.ObjectFlags |= RF_Transient;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	Volume = GetWorld()->SpawnActor<APostProcessVolume>(Params);
	if (!Volume)
	{
		return false;
	}
	// Unbound: applies to whichever camera is active (first person, title, dialogue).
	Volume->bUnbound = true;
	Volume->bEnabled = false;
	Volume->BlendWeight = 1.f;
	Volume->Priority = 1000.f;
	Volume->Settings.AddBlendable(MID, 1.f);
	return true;
}

void UFixHimHoverOutlineSubsystem::Show(const AFixHimInteractable* Target, const FLinearColor& Color)
{
	if (!Target || !EnsureVolume())
	{
		return;
	}
	Current = Target;
	MID->SetVectorParameterValue(TEXT("Color"), Color);
	Volume->bEnabled = true;
}

void UFixHimHoverOutlineSubsystem::Hide(const AFixHimInteractable* Target)
{
	if (Current.Get() != Target && Current.IsValid())
	{
		return;
	}
	Current.Reset();
	if (Volume)
	{
		Volume->bEnabled = false;
	}
}
