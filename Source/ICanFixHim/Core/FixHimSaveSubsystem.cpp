// I Can Fix Him - AI Game Jam 2026

#include "Core/FixHimSaveSubsystem.h"
#include "ICanFixHim.h"
#include "JsonObjectConverter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "AudioDevice.h"
#include "GameFramework/GameUserSettings.h"

UFixHimSaveSubsystem* UFixHimSaveSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UFixHimSaveSubsystem>() : nullptr;
}

void UFixHimSaveSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	SessionStartTime = FPlatformTime::Seconds();

	FString Json;
	if (FFileHelper::LoadFileToString(Json, *GetOptionsPath()))
	{
		FJsonObjectConverter::JsonObjectStringToUStruct(Json, &OptionsData);
	}
}

FString UFixHimSaveSubsystem::GetSavePath() const
{
	return FPaths::ProjectSavedDir() / TEXT("SaveGames") / TEXT("ICanFixHim_Save.json");
}

FString UFixHimSaveSubsystem::GetOptionsPath() const
{
	return FPaths::ProjectSavedDir() / TEXT("SaveGames") / TEXT("ICanFixHim_Options.json");
}

bool UFixHimSaveSubsystem::HasSaveFile() const
{
	return IFileManager::Get().FileExists(*GetSavePath());
}

void UFixHimSaveSubsystem::NewGame()
{
	SaveData = FFixHimSaveData();
	SessionStartTime = FPlatformTime::Seconds();
}

bool UFixHimSaveSubsystem::LoadGame()
{
	FString Json;
	if (!FFileHelper::LoadFileToString(Json, *GetSavePath()))
	{
		return false;
	}
	FFixHimSaveData Loaded;
	if (!FJsonObjectConverter::JsonObjectStringToUStruct(Json, &Loaded))
	{
		UE_LOG(LogFixHim, Warning, TEXT("Save file is corrupt: %s"), *GetSavePath());
		return false;
	}
	SaveData = MoveTemp(Loaded);
	SessionStartTime = FPlatformTime::Seconds();
	return true;
}

bool UFixHimSaveSubsystem::SaveGame()
{
	OnPreSave.Broadcast();
	const double Now = FPlatformTime::Seconds();
	SaveData.PlaySeconds += float(Now - SessionStartTime);
	SessionStartTime = Now;
	SaveData.SavedAt = FDateTime::Now().ToIso8601();

	FString Json;
	if (!FJsonObjectConverter::UStructToJsonObjectString(SaveData, Json))
	{
		return false;
	}
	const bool bOk = FFileHelper::SaveStringToFile(Json, *GetSavePath(), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
	if (bOk)
	{
		OnSaved.Broadcast();
	}
	return bOk;
}

void UFixHimSaveSubsystem::DeleteSave()
{
	IFileManager::Get().Delete(*GetSavePath());
}

int32 UFixHimSaveSubsystem::GetFlag(const FString& Name) const
{
	const int32* V = SaveData.Flags.Find(Name);
	return V ? *V : 0;
}

void UFixHimSaveSubsystem::AddFlag(const FString& Name, int32 Delta)
{
	SaveData.Flags.FindOrAdd(Name) += Delta;
}

void UFixHimSaveSubsystem::AddStat(const FString& HunkId, ERelationshipAxis Axis, int32 Delta)
{
	if (Delta == 0)
	{
		return;
	}
	FHunkProgress& P = Hunk(HunkId);
	switch (Axis)
	{
	case ERelationshipAxis::Romance: P.Romance += Delta; break;
	case ERelationshipAxis::Friendship: P.Friendship += Delta; break;
	case ERelationshipAxis::Friction: P.Friction += Delta; break;
	}
	OnStatChanged.Broadcast(HunkId, Axis, Delta);
}

int32 UFixHimSaveSubsystem::CountFixed() const
{
	int32 N = 0;
	for (const auto& Pair : SaveData.Hunks)
	{
		N += Pair.Value.bFixed ? 1 : 0;
	}
	return N;
}

void UFixHimSaveSubsystem::SaveOptions()
{
	FString Json;
	if (FJsonObjectConverter::UStructToJsonObjectString(OptionsData, Json))
	{
		FFileHelper::SaveStringToFile(Json, *GetOptionsPath(), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
	}
}

void UFixHimSaveSubsystem::ApplyOptions()
{
	if (const UWorld* World = GetWorld())
	{
		if (FAudioDeviceHandle Audio = World->GetAudioDevice())
		{
			Audio->SetTransientPrimaryVolume(OptionsData.MasterVolume);
		}
	}

#if !WITH_EDITOR
	if (UGameUserSettings* GUS = GEngine ? GEngine->GetGameUserSettings() : nullptr)
	{
		const EWindowMode::Type Wanted = OptionsData.bFullscreen ? EWindowMode::WindowedFullscreen : EWindowMode::Windowed;
		if (GUS->GetFullscreenMode() != Wanted)
		{
			GUS->SetFullscreenMode(Wanted);
			GUS->ApplySettings(false);
		}
	}
#endif
}
