// I Can Fix Him - AI Game Jam 2026

#include "Dialogue/FixHimDialogueSubsystem.h"
#include "Dialogue/DialogueCondition.h"
#include "Core/FixHimSaveSubsystem.h"
#include "Core/FixHimSettings.h"
#include "ICanFixHim.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Engine/Engine.h"

namespace
{
	FLinearColor ParseColor(const TSharedPtr<FJsonValue>& Value, const FLinearColor& Default)
	{
		if (!Value.IsValid())
		{
			return Default;
		}
		FString Hex;
		if (Value->TryGetString(Hex))
		{
			return FLinearColor::FromSRGBColor(FColor::FromHex(Hex));
		}
		const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
		if (Value->TryGetArray(Arr) && Arr->Num() >= 3)
		{
			return FLinearColor((*Arr)[0]->AsNumber(), (*Arr)[1]->AsNumber(), (*Arr)[2]->AsNumber(), Arr->Num() > 3 ? (*Arr)[3]->AsNumber() : 1.0);
		}
		return Default;
	}

	FVector ParseVector(const TSharedPtr<FJsonObject>& Obj, const FString& Field, const FVector& Default)
	{
		const TArray<TSharedPtr<FJsonValue>>* Arr = nullptr;
		if (Obj->TryGetArrayField(Field, Arr) && Arr->Num() >= 3)
		{
			return FVector((*Arr)[0]->AsNumber(), (*Arr)[1]->AsNumber(), (*Arr)[2]->AsNumber());
		}
		double Uniform = 0.0;
		if (Obj->TryGetNumberField(Field, Uniform))
		{
			return FVector(Uniform);
		}
		return Default;
	}

	TArray<FDialogueEffect> ParseEffects(const TSharedPtr<FJsonObject>& Obj)
	{
		TArray<FDialogueEffect> Out;
		const TSharedPtr<FJsonObject>* Do = nullptr;
		if (Obj.IsValid() && Obj->TryGetObjectField(TEXT("do"), Do))
		{
			for (const auto& Pair : (*Do)->Values)
			{
				FDialogueEffect E;
				E.Key = FString(Pair.Key).ToLower();
				double Num = 0.0;
				bool bBool = false;
				if (Pair.Value->TryGetNumber(Num))
				{
					E.Value = FMath::RoundToInt(Num);
				}
				else if (Pair.Value->TryGetBool(bBool))
				{
					E.Value = bBool ? 1 : 0;
				}
				Out.Add(E);
			}
		}
		return Out;
	}

	FDialogueLine ParseLine(const FString& Raw, const TArray<FString>& Speakers)
	{
		FDialogueLine Line;
		FString Text = Raw.TrimStartAndEnd();
		if (Text.StartsWith(TEXT("You:"), ESearchCase::IgnoreCase))
		{
			Line.Speaker = EDialogueSpeaker::Player;
			Text = Text.RightChop(4).TrimStart();
			Line.Text = Text;
			return Line;
		}
		for (const FString& Name : Speakers)
		{
			if (Text.StartsWith(Name + TEXT(":"), ESearchCase::IgnoreCase))
			{
				Line.Speaker = EDialogueSpeaker::Named;
				Line.SpeakerName = Name;
				Line.Text = Text.RightChop(Name.Len() + 1).TrimStart();
				return Line;
			}
		}
		if (Text.Len() > 1 && Text.StartsWith(TEXT("*")) && Text.EndsWith(TEXT("*")))
		{
			Line.Speaker = EDialogueSpeaker::Narration;
			Text = Text.Mid(1, Text.Len() - 2);
		}
		Line.Text = Text;
		return Line;
	}

	/** Extract topic ids referenced as [word] or [shown|topic] in a line. */
	void CollectTopicRefs(const FString& Text, TArray<FString>& Out)
	{
		int32 Open = INDEX_NONE;
		for (int32 i = 0; i < Text.Len(); ++i)
		{
			if (Text[i] == TEXT('['))
			{
				Open = i;
			}
			else if (Text[i] == TEXT(']') && Open != INDEX_NONE)
			{
				FString Inner = Text.Mid(Open + 1, i - Open - 1);
				FString Shown, Topic;
				if (!Inner.Split(TEXT("|"), &Shown, &Topic))
				{
					Topic = Inner;
				}
				Out.AddUnique(Topic.TrimStartAndEnd().ToLower());
				Open = INDEX_NONE;
			}
		}
	}

	FAutoConsoleCommandWithWorld ReloadCmd(
		TEXT("FixHim.ReloadDialogue"),
		TEXT("Reload all dialogue JSON files from disk."),
		FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World)
		{
			if (UFixHimDialogueSubsystem* Sub = UFixHimDialogueSubsystem::Get(World))
			{
				Sub->ReloadDefinitions();
			}
		}));
}

UFixHimDialogueSubsystem* UFixHimDialogueSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UFixHimDialogueSubsystem>() : nullptr;
}

void UFixHimDialogueSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Collection.InitializeDependency<UFixHimSaveSubsystem>();
	Super::Initialize(Collection);
	ReloadDefinitions();
}

void UFixHimDialogueSubsystem::ReloadDefinitions()
{
	Hunks.Reset();
	LoadErrors.Reset();

	const FString Dir = FPaths::ProjectContentDir() / UFixHimSettings::Get()->DialogueDirectory;
	TArray<FString> Files;
	IFileManager::Get().FindFiles(Files, *(Dir / TEXT("*.json")), true, false);
	Files.Sort();
	for (const FString& File : Files)
	{
		LoadHunkFile(Dir / File);
	}

	for (const auto& Pair : Hunks)
	{
		Validate(Pair.Value);
	}
	for (const FString& Err : LoadErrors)
	{
		UE_LOG(LogFixHim, Warning, TEXT("Dialogue: %s"), *Err);
	}
	UE_LOG(LogFixHim, Log, TEXT("Loaded %d hunks from %s (%d warnings)"), Hunks.Num(), *Dir, LoadErrors.Num());
}

bool UFixHimDialogueSubsystem::LoadHunkFile(const FString& Path)
{
	FString Json;
	if (!FFileHelper::LoadFileToString(Json, *Path))
	{
		LoadErrors.Add(FString::Printf(TEXT("Could not read %s"), *Path));
		return false;
	}

	TSharedPtr<FJsonObject> Root;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Json);
	if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
	{
		LoadErrors.Add(FString::Printf(TEXT("%s: invalid JSON (%s)"), *FPaths::GetCleanFilename(Path), *Reader->GetErrorMessage()));
		return false;
	}

	FHunkDefinition Def;
	Def.Id = Root->GetStringField(TEXT("id")).ToLower();
	if (Def.Id.IsEmpty())
	{
		Def.Id = FPaths::GetBaseFilename(Path).ToLower();
	}
	Root->TryGetStringField(TEXT("name"), Def.Name);
	Root->TryGetStringField(TEXT("kind"), Def.Kind);
	Def.Kind = Def.Kind.IsEmpty() ? FString(TEXT("hunk")) : Def.Kind.ToLower();
	Root->TryGetStringArrayField(TEXT("speakers"), Def.Speakers);
	Root->TryGetStringField(TEXT("malady"), Def.Malady);
	Root->TryGetStringField(TEXT("room"), Def.Room);
	Root->TryGetStringField(TEXT("tagline"), Def.Tagline);
	Def.Room = Def.Room.ToLower();

	if (const TSharedPtr<FJsonObject>* Look = nullptr; Root->TryGetObjectField(TEXT("look"), Look))
	{
		(*Look)->TryGetStringField(TEXT("mesh"), Def.Mesh);
		(*Look)->TryGetStringField(TEXT("idle"), Def.Idle);
		Def.Shirt = ParseColor((*Look)->TryGetField(TEXT("shirt")), Def.Shirt);
		Def.Skin = ParseColor((*Look)->TryGetField(TEXT("skin")), Def.Skin);
		Def.Pants = ParseColor((*Look)->TryGetField(TEXT("pants")), Def.Pants);
		Def.Shoes = ParseColor((*Look)->TryGetField(TEXT("shoes")), Def.Shoes);
		double Pattern = 0.0;
		if ((*Look)->TryGetNumberField(TEXT("pattern"), Pattern))
		{
			Def.Pattern = float(Pattern);
		}
		Def.GlowColor = ParseColor((*Look)->TryGetField(TEXT("glow")), Def.GlowColor);
		double Scale = 1.0;
		if ((*Look)->TryGetNumberField(TEXT("scale"), Scale))
		{
			Def.Scale = float(Scale);
		}
		const TArray<TSharedPtr<FJsonValue>>* Props = nullptr;
		if ((*Look)->TryGetArrayField(TEXT("props"), Props))
		{
			for (const TSharedPtr<FJsonValue>& PV : *Props)
			{
				const TSharedPtr<FJsonObject> PO = PV->AsObject();
				if (!PO.IsValid())
				{
					continue;
				}
				FHunkProp Prop;
				PO->TryGetStringField(TEXT("shape"), Prop.Shape);
				FString Socket;
				if (PO->TryGetStringField(TEXT("socket"), Socket))
				{
					Prop.Socket = FName(*Socket);
				}
				Prop.Location = ParseVector(PO, TEXT("loc"), FVector::ZeroVector);
				const FVector Rot = ParseVector(PO, TEXT("rot"), FVector::ZeroVector);
				Prop.Rotation = FRotator(Rot.Y, Rot.Z, Rot.X); // [roll, pitch, yaw] in JSON
				Prop.Scale = ParseVector(PO, TEXT("scale"), FVector::OneVector);
				Prop.Color = ParseColor(PO->TryGetField(TEXT("color")), Prop.Color);
				double Emissive = 0.0;
				if (PO->TryGetNumberField(TEXT("emissive"), Emissive))
				{
					Prop.Emissive = float(Emissive);
				}
				Def.Props.Add(Prop);
			}
		}
	}

	const TArray<TSharedPtr<FJsonValue>>* Entries = nullptr;
	if (Root->TryGetArrayField(TEXT("entries"), Entries))
	{
		for (const TSharedPtr<FJsonValue>& EV : *Entries)
		{
			const TSharedPtr<FJsonObject> EO = EV->AsObject();
			if (!EO.IsValid())
			{
				continue;
			}
			FDialogueEntry Entry;
			EO->TryGetStringField(TEXT("if"), Entry.Condition);
			EO->TryGetStringField(TEXT("node"), Entry.Node);
			EO->TryGetBoolField(TEXT("counts"), Entry.bCounts);
			Def.Entries.Add(Entry);
		}
	}

	if (const TSharedPtr<FJsonObject>* Endings = nullptr; Root->TryGetObjectField(TEXT("endings"), Endings))
	{
		for (const auto& Pair : (*Endings)->Values)
		{
			const TSharedPtr<FJsonObject> EO = Pair.Value->AsObject();
			if (EO.IsValid())
			{
				FHunkEnding Ending;
				EO->TryGetStringField(TEXT("title"), Ending.Title);
				EO->TryGetStringField(TEXT("text"), Ending.Text);
				Def.Endings.Add(FString(Pair.Key), Ending);
			}
		}
	}

	if (const TSharedPtr<FJsonObject>* Nodes = nullptr; Root->TryGetObjectField(TEXT("nodes"), Nodes))
	{
		for (const auto& Pair : (*Nodes)->Values)
		{
			const TSharedPtr<FJsonObject> NO = Pair.Value->AsObject();
			if (!NO.IsValid())
			{
				continue;
			}
			FDialogueNode Node;
			Node.Id = FString(Pair.Key);

			const TArray<TSharedPtr<FJsonValue>>* Lines = nullptr;
			if (NO->TryGetArrayField(TEXT("lines"), Lines))
			{
				for (const TSharedPtr<FJsonValue>& LV : *Lines)
				{
					Node.Lines.Add(ParseLine(LV->AsString(), Def.Speakers));
				}
			}
			FString Single;
			if (NO->TryGetStringField(TEXT("say"), Single))
			{
				Node.Lines.Add(ParseLine(Single, Def.Speakers));
			}

			const TArray<TSharedPtr<FJsonValue>>* Choices = nullptr;
			if (NO->TryGetArrayField(TEXT("choices"), Choices))
			{
				for (const TSharedPtr<FJsonValue>& CV : *Choices)
				{
					const TSharedPtr<FJsonObject> CO = CV->AsObject();
					if (!CO.IsValid())
					{
						continue;
					}
					FDialogueChoice Choice;
					CO->TryGetStringField(TEXT("text"), Choice.Text);
					CO->TryGetStringField(TEXT("if"), Choice.Condition);
					CO->TryGetStringField(TEXT("goto"), Choice.Goto);
					Choice.Effects = ParseEffects(CO);
					Node.Choices.Add(Choice);
				}
			}

			if (const TSharedPtr<FJsonObject>* Topics = nullptr; NO->TryGetObjectField(TEXT("topics"), Topics))
			{
				for (const auto& TP : (*Topics)->Values)
				{
					FDialogueTopic Topic;
					FString GotoOnly;
					if (TP.Value->TryGetString(GotoOnly))
					{
						Topic.Goto = GotoOnly;
					}
					else if (const TSharedPtr<FJsonObject> TO = TP.Value->AsObject())
					{
						TO->TryGetStringField(TEXT("goto"), Topic.Goto);
						TO->TryGetStringField(TEXT("if"), Topic.Condition);
						Topic.Effects = ParseEffects(TO);
					}
					Node.Topics.Add(FString(TP.Key).ToLower(), Topic);
				}
			}

			Node.Effects = ParseEffects(NO);
			NO->TryGetStringField(TEXT("goto"), Node.Goto);
			NO->TryGetBoolField(TEXT("end"), Node.bEnd);
			NO->TryGetStringField(TEXT("ending"), Node.Ending);
			NO->TryGetStringField(TEXT("fx"), Node.Fx);
			NO->TryGetStringField(TEXT("fxText"), Node.FxText);
			if (!Node.Ending.IsEmpty())
			{
				Node.bEnd = true;
			}
			Def.Nodes.Add(Node.Id, MoveTemp(Node));
		}
	}

	Hunks.Add(Def.Id, MoveTemp(Def));
	return true;
}

void UFixHimDialogueSubsystem::Validate(const FHunkDefinition& Def)
{
	auto Check = [&](const FString& Where, const FString& Target)
	{
		if (!Target.IsEmpty() && !Def.Nodes.Contains(Target))
		{
			LoadErrors.Add(FString::Printf(TEXT("%s: %s -> missing node '%s'"), *Def.Id, *Where, *Target));
		}
	};
	auto CheckCond = [&](const FString& Where, const FString& Cond)
	{
		FString Err;
		FixHim::Condition::Evaluate(Cond, [](const FString&) { return 0; }, &Err);
		if (!Err.IsEmpty())
		{
			LoadErrors.Add(FString::Printf(TEXT("%s: %s condition '%s': %s"), *Def.Id, *Where, *Cond, *Err));
		}
	};

	if (Def.Entries.IsEmpty())
	{
		LoadErrors.Add(FString::Printf(TEXT("%s: no entries"), *Def.Id));
	}
	for (const FDialogueEntry& E : Def.Entries)
	{
		Check(TEXT("entry"), E.Node);
		CheckCond(TEXT("entry"), E.Condition);
	}
	for (const auto& Pair : Def.Nodes)
	{
		const FDialogueNode& N = Pair.Value;
		Check(N.Id + TEXT(".goto"), N.Goto);
		if (N.Lines.IsEmpty())
		{
			LoadErrors.Add(FString::Printf(TEXT("%s: node '%s' has no lines"), *Def.Id, *N.Id));
		}
		if (N.Choices.IsEmpty() && N.Goto.IsEmpty() && !N.bEnd)
		{
			LoadErrors.Add(FString::Printf(TEXT("%s: node '%s' is a dead end (no choices, goto or end)"), *Def.Id, *N.Id));
		}
		for (const FDialogueChoice& C : N.Choices)
		{
			Check(N.Id + TEXT(" choice"), C.Goto);
			CheckCond(N.Id + TEXT(" choice"), C.Condition);
		}
		TArray<FString> Refs;
		for (const FDialogueLine& L : N.Lines)
		{
			CollectTopicRefs(L.Text, Refs);
		}
		for (const FString& Ref : Refs)
		{
			if (!N.Topics.Contains(Ref))
			{
				LoadErrors.Add(FString::Printf(TEXT("%s: node '%s' highlights [%s] but has no matching topic"), *Def.Id, *N.Id, *Ref));
			}
		}
		for (const auto& TP : N.Topics)
		{
			Check(N.Id + TEXT(" topic ") + TP.Key, TP.Value.Goto);
		}
		if (!N.Ending.IsEmpty() && N.Ending != TEXT("auto") && !Def.Endings.Contains(N.Ending))
		{
			LoadErrors.Add(FString::Printf(TEXT("%s: node '%s' ending '%s' has no ending card"), *Def.Id, *N.Id, *N.Ending));
		}
	}
}

int32 UFixHimDialogueSubsystem::CountStoryHunks() const
{
	int32 N = 0;
	for (const auto& Pair : Hunks)
	{
		N += Pair.Value.IsHunk() ? 1 : 0;
	}
	return N;
}

const FHunkDefinition* UFixHimDialogueSubsystem::FindHunkForRoom(const FString& RoomId) const
{
	for (const auto& Pair : Hunks)
	{
		if (Pair.Value.IsHunk() && Pair.Value.Room.Equals(RoomId, ESearchCase::IgnoreCase))
		{
			return &Pair.Value;
		}
	}
	return nullptr;
}

int32 UFixHimDialogueSubsystem::ResolveVariable(const FString& HunkId, const FString& Identifier) const
{
	const UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>();
	if (!Save)
	{
		return 0;
	}

	FString Scope, Name;
	if (!Identifier.Split(TEXT("."), &Scope, &Name))
	{
		Scope = HunkId;
		Name = Identifier;
	}

	if (Scope == TEXT("flag"))
	{
		return Save->GetFlag(Name);
	}
	if (Scope == TEXT("seen"))
	{
		const FHunkProgress* P = Save->FindHunk(HunkId);
		return (P && P->SeenNodes.Contains(Name)) ? 1 : 0;
	}
	if (Name == TEXT("fixedcount") || Identifier == TEXT("fixedcount"))
	{
		return Save->CountFixed();
	}
	if (Identifier == TEXT("week"))
	{
		return Save->Data().Week;
	}

	const FHunkProgress* P = Save->FindHunk(Scope);
	if (!P)
	{
		return 0;
	}
	if (Name == TEXT("romance")) { return P->Romance; }
	if (Name == TEXT("friendship")) { return P->Friendship; }
	if (Name == TEXT("friction")) { return P->Friction; }
	if (Name == TEXT("visits")) { return P->Visits; }
	if (Name == TEXT("met")) { return P->bMet ? 1 : 0; }
	if (Name == TEXT("fixed")) { return P->bFixed ? 1 : 0; }
	if (Name == TEXT("talkedtoday")) { return P->LastTalkWeek == Save->Data().Week ? 1 : 0; }
	if (Name.StartsWith(TEXT("ending_"))) { return P->Ending == Name.RightChop(7) ? 1 : 0; }
	return 0;
}

bool UFixHimDialogueSubsystem::IsTrue(const FString& Condition) const
{
	return FixHim::Condition::IsTrue(Condition, [this](const FString& Ident) { return ResolveVariable(ActiveHunkId, Ident); });
}

const FDialogueNode* UFixHimDialogueSubsystem::ResolveEntryNode(const FString& DefinitionId) const
{
	const FHunkDefinition* Def = FindHunk(DefinitionId);
	if (!Def)
	{
		return nullptr;
	}
	for (const FDialogueEntry& Entry : Def->Entries)
	{
		if (FixHim::Condition::IsTrue(Entry.Condition, [this, &DefinitionId](const FString& Ident) { return ResolveVariable(DefinitionId, Ident); }))
		{
			return Def->FindNode(Entry.Node);
		}
	}
	return nullptr;
}

FString UFixHimDialogueSubsystem::ResolveAutoEnding(const FString& HunkId) const
{
	const UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>();
	const FHunkProgress* P = Save ? Save->FindHunk(HunkId) : nullptr;
	if (!P)
	{
		return TEXT("friend_failure");
	}
	// Ties (including 0/0) fall on the friendship track: romance has to be earned.
	const bool bRomantic = P->Romance > P->Friendship;
	const bool bSour = P->Friction >= FMath::Max(P->Romance, P->Friendship);
	if (bRomantic)
	{
		return bSour ? TEXT("romance_failure") : TEXT("romance_success");
	}
	return bSour ? TEXT("friend_failure") : TEXT("friend_success");
}

bool UFixHimDialogueSubsystem::StartConversation(const FString& HunkId)
{
	const FHunkDefinition* Def = FindHunk(HunkId);
	if (!Def || IsActive())
	{
		return false;
	}
	ActiveHunkId = HunkId;
	PendingEnding.Reset();
	JumpsWithoutLines = 0;
	Tangents.Reset();

	FString StartNode;
	bCountVisit = true;
	for (const FDialogueEntry& Entry : Def->Entries)
	{
		if (IsTrue(Entry.Condition))
		{
			StartNode = Entry.Node;
			bCountVisit = Entry.bCounts;
			break;
		}
	}
	if (!Def->Nodes.Contains(StartNode))
	{
		UE_LOG(LogFixHim, Warning, TEXT("No valid entry node for %s"), *HunkId);
		ActiveHunkId.Reset();
		return false;
	}

	if (UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>())
	{
		Save->Hunk(HunkId).bMet = true;
	}

	OnConversationStarted.Broadcast(HunkId);
	EnterNode(StartNode);
	return true;
}

void UFixHimDialogueSubsystem::EnterNode(const FString& NodeId)
{
	const FHunkDefinition* Def = FindHunk(ActiveHunkId);
	const FDialogueNode* Node = Def ? Def->FindNode(NodeId) : nullptr;
	if (!Node)
	{
		UE_LOG(LogFixHim, Warning, TEXT("%s: missing node '%s', ending conversation"), *ActiveHunkId, *NodeId);
		FinishConversation();
		return;
	}

	ActiveNodeId = NodeId;
	LineIndex = 0;

	if (UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>())
	{
		Save->Hunk(ActiveHunkId).SeenNodes.AddUnique(NodeId);
	}
	ApplyEffects(Node->Effects);

	if (!Node->Ending.IsEmpty())
	{
		PendingEnding = Node->Ending == TEXT("auto") ? ResolveAutoEnding(ActiveHunkId) : Node->Ending;
	}

	if (Node->Lines.IsEmpty())
	{
		// Pure routing node (a hypertext node with no text just rewinds).
		if (InTangent())
		{
			ReturnFromTangent();
			return;
		}
		if (++JumpsWithoutLines > 32)
		{
			UE_LOG(LogFixHim, Error, TEXT("%s: goto loop near '%s'"), *ActiveHunkId, *NodeId);
			FinishConversation();
			return;
		}
		if (!Node->Goto.IsEmpty())
		{
			EnterNode(Node->Goto);
		}
		else
		{
			FinishConversation();
		}
		return;
	}
	JumpsWithoutLines = 0;
	RebuildView();
}

void UFixHimDialogueSubsystem::Advance()
{
	if (!IsActive())
	{
		return;
	}
	const FDialogueNode* Node = FindHunk(ActiveHunkId)->FindNode(ActiveNodeId);
	if (!Node)
	{
		FinishConversation();
		return;
	}
	if (LineIndex < Node->Lines.Num() - 1)
	{
		++LineIndex;
		View.Fx.Reset(); // fx only plays on node entry
		RebuildView();
		return;
	}
	if (InTangent())
	{
		ReturnFromTangent();
		return;
	}
	if (!GetVisibleChoiceIndices().IsEmpty())
	{
		return; // waiting on a choice
	}
	if (!Node->Goto.IsEmpty() && !Node->bEnd)
	{
		EnterNode(Node->Goto);
		return;
	}
	FinishConversation();
}

void UFixHimDialogueSubsystem::Choose(int32 VisibleChoiceIndex)
{
	if (!IsActive())
	{
		return;
	}
	const FDialogueNode* Node = FindHunk(ActiveHunkId)->FindNode(ActiveNodeId);
	const TArray<int32> Visible = GetVisibleChoiceIndices();
	if (!Node || !Visible.IsValidIndex(VisibleChoiceIndex))
	{
		return;
	}
	const FDialogueChoice& Choice = Node->Choices[Visible[VisibleChoiceIndex]];
	ApplyEffects(Choice.Effects);
	if (Choice.Goto.IsEmpty())
	{
		FinishConversation();
	}
	else
	{
		EnterNode(Choice.Goto);
	}
}

void UFixHimDialogueSubsystem::ClickTopic(const FString& TopicId)
{
	if (!IsActive())
	{
		return;
	}
	const FDialogueNode* Node = FindHunk(ActiveHunkId)->FindNode(ActiveNodeId);
	const FDialogueTopic* Topic = Node ? Node->Topics.Find(TopicId.ToLower()) : nullptr;
	if (!Topic || !IsTrue(Topic->Condition))
	{
		return;
	}
	ApplyEffects(Topic->Effects);
	const FHunkDefinition* Def = FindHunk(ActiveHunkId);
	if (Def && Def->FindNode(Topic->Goto) && (InTangent() || IsHypertextNode(*Def, Topic->Goto)))
	{
		Tangents.Emplace(ActiveNodeId, LineIndex);
	}
	EnterNode(Topic->Goto);
}

bool UFixHimDialogueSubsystem::IsHypertextNode(const FHunkDefinition& Def, const FString& NodeId) const
{
	const FDialogueNode* Target = Def.FindNode(NodeId);
	if (!Target || !Target->Ending.IsEmpty())
	{
		return false;
	}
	bool bViaTopic = false;
	for (const FDialogueEntry& Entry : Def.Entries)
	{
		if (Entry.Node == NodeId)
		{
			return false;
		}
	}
	for (const auto& Pair : Def.Nodes)
	{
		const FDialogueNode& N = Pair.Value;
		if (N.Goto == NodeId)
		{
			return false;
		}
		for (const FDialogueChoice& Choice : N.Choices)
		{
			if (Choice.Goto == NodeId)
			{
				return false;
			}
		}
		for (const auto& TP : N.Topics)
		{
			bViaTopic |= TP.Value.Goto == NodeId;
		}
	}
	return bViaTopic;
}

void UFixHimDialogueSubsystem::ReturnFromTangent()
{
	const TPair<FString, int32> Back = Tangents.Pop();
	ActiveNodeId = Back.Key;
	LineIndex = Back.Value;
	RebuildView(true);
}

void UFixHimDialogueSubsystem::AbortConversation()
{
	ActiveHunkId.Reset();
	ActiveNodeId.Reset();
	PendingEnding.Reset();
	Tangents.Reset();
	View = FDialogueView();
}

void UFixHimDialogueSubsystem::FinishConversation()
{
	if (!IsActive())
	{
		return;
	}
	const FString HunkId = ActiveHunkId;
	const FString Ending = PendingEnding;

	if (UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>())
	{
		FHunkProgress& P = Save->Hunk(HunkId);
		if (bCountVisit)
		{
			P.Visits++;
			P.LastTalkWeek = Save->Data().Week;
		}
		if (!Ending.IsEmpty())
		{
			P.Ending = Ending;
			P.bFixed = true;
		}
	}

	AbortConversation();
	OnConversationEnded.Broadcast(HunkId, Ending);
}

void UFixHimDialogueSubsystem::ApplyEffects(const TArray<FDialogueEffect>& Effects)
{
	UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>();
	if (!Save)
	{
		return;
	}
	for (const FDialogueEffect& E : Effects)
	{
		FString Scope, Name;
		if (!E.Key.Split(TEXT("."), &Scope, &Name))
		{
			Scope = ActiveHunkId;
			Name = E.Key;
		}
		if (Scope == TEXT("flag"))
		{
			Save->AddFlag(Name, E.Value);
		}
		else if (Name == TEXT("romance"))
		{
			Save->AddStat(Scope, ERelationshipAxis::Romance, E.Value);
		}
		else if (Name == TEXT("friendship"))
		{
			Save->AddStat(Scope, ERelationshipAxis::Friendship, E.Value);
		}
		else if (Name == TEXT("friction"))
		{
			Save->AddStat(Scope, ERelationshipAxis::Friction, E.Value);
		}
		else
		{
			UE_LOG(LogFixHim, Warning, TEXT("Unknown effect key '%s'"), *E.Key);
		}
	}
}

TArray<int32> UFixHimDialogueSubsystem::GetVisibleChoiceIndices() const
{
	TArray<int32> Out;
	const FHunkDefinition* Def = FindHunk(ActiveHunkId);
	const FDialogueNode* Node = Def ? Def->FindNode(ActiveNodeId) : nullptr;
	if (Node && LineIndex >= Node->Lines.Num() - 1)
	{
		for (int32 i = 0; i < Node->Choices.Num(); ++i)
		{
			if (IsTrue(Node->Choices[i].Condition))
			{
				Out.Add(i);
			}
		}
	}
	return Out;
}

FString UFixHimDialogueSubsystem::Substitute(const FString& In) const
{
	const UFixHimSaveSubsystem* Save = GetGameInstance()->GetSubsystem<UFixHimSaveSubsystem>();
	FString Out = In.Replace(TEXT("{player}"), *(Save ? Save->GetPlayerName() : UFixHimSettings::Get()->PlayerName));
	if (const FHunkDefinition* Def = FindHunk(ActiveHunkId))
	{
		Out = Out.Replace(TEXT("{name}"), *Def->Name);
	}
	return Out;
}

void UFixHimDialogueSubsystem::RebuildView(bool bIsReturn)
{
	const FHunkDefinition* Def = FindHunk(ActiveHunkId);
	const FDialogueNode* Node = Def ? Def->FindNode(ActiveNodeId) : nullptr;
	if (!Node || !Node->Lines.IsValidIndex(LineIndex))
	{
		return;
	}

	const FDialogueLine& Line = Node->Lines[LineIndex];
	View = FDialogueView();
	View.HunkId = ActiveHunkId;
	View.HunkName = Def->Name;
	View.Speaker = Line.Speaker;
	View.SpeakerName = Line.SpeakerName;
	View.Text = Substitute(Line.Text);
	View.bIsLastLine = LineIndex == Node->Lines.Num() - 1;
	View.bIsReturn = bIsReturn;
	View.bInTangent = InTangent();
	if (LineIndex == 0 && !bIsReturn)
	{
		View.Fx = Node->Fx;
		View.FxText = Substitute(Node->FxText);
	}

	if (!InTangent())
	{
		for (const int32 Index : GetVisibleChoiceIndices())
		{
			View.Choices.Add(Substitute(Node->Choices[Index].Text));
		}
	}
	for (const auto& TP : Node->Topics)
	{
		if (IsTrue(TP.Value.Condition))
		{
			View.ActiveTopics.Add(TP.Key);
		}
	}
	View.bWillEnd = View.bIsLastLine && !InTangent() && View.Choices.IsEmpty() && (Node->bEnd || Node->Goto.IsEmpty());

	OnView.Broadcast(View);
}
