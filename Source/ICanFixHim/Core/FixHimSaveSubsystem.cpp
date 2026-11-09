// I Can Fix Him - AI Game Jam 2026

#include "Core/FixHimSaveSubsystem.h"
#include "ICanFixHim.h"
#include "Core/FixHimSettings.h"
#include "JsonObjectConverter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/PackageName.h"
#include "HAL/FileManager.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "AudioDevice.h"
#include "Audio/FixHimMusicSubsystem.h"
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
		// A file without "Version" predates versioning (version 1).
		OptionsData.Version = 1;
		FJsonObjectConverter::JsonObjectStringToUStruct(Json, &OptionsData);
		if (OptionsData.Version < 2)
		{
			// Version 2 doubled the default mouse sensitivity. Players still on the old default (1.0) move to the new
			// one; anyone who picked their own value keeps it.
			if (FMath::IsNearlyEqual(OptionsData.MouseSensitivity, 1.f, 0.01f))
			{
				OptionsData.MouseSensitivity = FFixHimOptions::DefaultMouseSensitivity;
			}
		}
		if (OptionsData.Version != FFixHimOptions::CurrentVersion)
		{
			OptionsData.Version = FFixHimOptions::CurrentVersion;
			SaveOptions();
		}
	}
}

FString UFixHimSaveSubsystem::GetSavePath() const
{
	// The game's default map keeps the original file. Any other map (e.g. the apartment redesign) gets its own file,
	// so it never restores world positions saved in a different layout or overwrites the shipping map's progress.
	FString FileName = TEXT("ICanFixHim_Save");
	const UGameInstance* GI = GetGameInstance();
	const UWorld* World = GI ? GI->GetWorld() : nullptr;
	if (World)
	{
		const FString MapName = UWorld::RemovePIEPrefix(World->GetMapName());
		FString DefaultMap;
		GConfig->GetString(TEXT("/Script/EngineSettings.GameMapsSettings"), TEXT("GameDefaultMap"), DefaultMap, GEngineIni);
		const FString DefaultMapName = FPackageName::GetShortName(FPackageName::ObjectPathToPackageName(DefaultMap));
		if (!MapName.IsEmpty() && !DefaultMapName.IsEmpty() && MapName != DefaultMapName)
		{
			FileName += TEXT("_") + MapName;
		}
	}
	return FPaths::ProjectSavedDir() / TEXT("SaveGames") / (FileName + TEXT(".json"));
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
	int32* Stat = Axis == ERelationshipAxis::Romance ? &P.Romance : Axis == ERelationshipAxis::Friendship ? &P.Friendship : &P.Friction;
	const int32 Before = *Stat;
	*Stat = FMath::Clamp(*Stat + Delta, 0, FixHimStatMax);
	if (*Stat != Before)
	{
		OnStatChanged.Broadcast(HunkId, Axis, *Stat - Before);
	}
}

FString UFixHimSaveSubsystem::GetPlayerName() const
{
	return SaveData.PlayerName.IsEmpty() ? UFixHimSettings::Get()->PlayerName : SaveData.PlayerName;
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
	if (const UGameInstance* GI = GetGameInstance())
	{
		if (UFixHimMusicSubsystem* Music = GI->GetSubsystem<UFixHimMusicSubsystem>())
		{
			Music->SetMusicVolume(OptionsData.MusicVolume);
		}
	}
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
