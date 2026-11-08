// I Can Fix Him - AI Game Jam 2026

#include "Dialogue/FixHimVoiceSubsystem.h"
#include "Dialogue/FixHimDialogueSubsystem.h"
#include "ICanFixHim.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Components/AudioComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"

namespace
{
	const TCHAR* VoiceRoot = TEXT("/Game/ICanFixHim/Audio/VO");

	FAutoConsoleCommandWithWorld GReindexVoice(
		TEXT("FixHim.ReloadVoice"),
		TEXT("Rescan /Game/ICanFixHim/Audio/VO for voice-over clips."),
		FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
		{
			if (UFixHimVoiceSubsystem* Voice = UFixHimVoiceSubsystem::Get(World))
			{
				Voice->RebuildIndex();
			}
		}));
}

UFixHimVoiceSubsystem* UFixHimVoiceSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UFixHimVoiceSubsystem>() : nullptr;
}

void UFixHimVoiceSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	UFixHimDialogueSubsystem* Dialogue = Collection.InitializeDependency<UFixHimDialogueSubsystem>();
	Super::Initialize(Collection);

	RebuildIndex();
	if (Dialogue)
	{
		ViewHandle = Dialogue->OnView.AddUObject(this, &UFixHimVoiceSubsystem::HandleView);
		EndHandle = Dialogue->OnConversationEnded.AddUObject(this, &UFixHimVoiceSubsystem::HandleEnded);
		AbortHandle = Dialogue->OnConversationAborted.AddWeakLambda(this, [this]() { Stop(); });
	}
}

void UFixHimVoiceSubsystem::Deinitialize()
{
	if (UFixHimDialogueSubsystem* Dialogue = GetGameInstance()->GetSubsystem<UFixHimDialogueSubsystem>())
	{
		Dialogue->OnView.Remove(ViewHandle);
		Dialogue->OnConversationEnded.Remove(EndHandle);
		Dialogue->OnConversationAborted.Remove(AbortHandle);
	}
	Stop(0.f);
	Super::Deinitialize();
}

FString UFixHimVoiceSubsystem::MakeKey(const FString& ScriptId, const FString& NodeId, int32 LineIndex)
{
	return FString::Printf(TEXT("VO_%s_%s_%d"), *ScriptId, *NodeId, LineIndex);
}

void UFixHimVoiceSubsystem::RebuildIndex()
{
	Index.Reset();
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
#if WITH_EDITOR
	// In the editor the background scan may not have reached the folder yet.
	Registry.ScanPathsSynchronous({ VoiceRoot }, /*bForceRescan*/ false);
#endif
	FARFilter Filter;
	Filter.PackagePaths.Add(VoiceRoot);
	Filter.bRecursivePaths = true;
	Filter.ClassPaths.Add(USoundWave::StaticClass()->GetClassPathName());
	TArray<FAssetData> Assets;
	Registry.GetAssets(Filter, Assets);
	for (const FAssetData& Asset : Assets)
	{
		Index.Add(Asset.AssetName.ToString(), Asset.GetSoftObjectPath());
	}
	UE_LOG(LogFixHim, Log, TEXT("Voice: %d voice-over clips indexed under %s"), Index.Num(), VoiceRoot);
}

bool UFixHimVoiceSubsystem::HasLine(const FString& ScriptId, const FString& NodeId, int32 LineIndex) const
{
	return Index.Contains(MakeKey(ScriptId, NodeId, LineIndex));
}

bool UFixHimVoiceSubsystem::IsPlaying() const
{
	const UAudioComponent* Comp = Playing.Get();
	return Comp && Comp->IsPlaying();
}

void UFixHimVoiceSubsystem::Stop(float FadeSeconds)
{
	if (UAudioComponent* Comp = Playing.Get())
	{
		if (FadeSeconds > 0.f && Comp->IsPlaying())
		{
			Comp->FadeOut(FadeSeconds, 0.f);
		}
		else
		{
			Comp->Stop();
		}
	}
	Playing.Reset();
	PlayingKey.Reset();
}

void UFixHimVoiceSubsystem::HandleView(const FDialogueView& View)
{
	const FString Key = MakeKey(View.HunkId, View.NodeId, View.LineIndex);
	// The same line can be re-broadcast (e.g. after a stat change); don't restart it.
	if (Key == PlayingKey && Playing.IsValid())
	{
		return;
	}
	Stop();
	if (View.bIsReturn)
	{
		// Back from an aside or hypertext tangent to a line the player already heard (or clicked through):
		// don't restart it from the top. Remember the key so a re-broadcast stays quiet too.
		PlayingKey = Key;
		return;
	}

	const FSoftObjectPath* Path = Index.Find(Key);
	USoundBase* Sound = Path ? Cast<USoundBase>(Path->TryLoad()) : nullptr;
	UWorld* World = GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
	if (!Sound || !World)
	{
		return;
	}
	if (UAudioComponent* Comp = UGameplayStatics::CreateSound2D(World, Sound, 1.f, 1.f, 0.f, nullptr, /*bPersistAcrossLevelTransition*/ false, /*bAutoDestroy*/ true))
	{
		Comp->bIsUISound = true; // keeps talking while the game is paused
		Comp->Play();
		Playing = Comp;
		PlayingKey = Key;
	}
}

void UFixHimVoiceSubsystem::HandleEnded(const FString& HunkId, const FString& EndingId)
{
	// The player clicked past the last line.
	Stop();
}
