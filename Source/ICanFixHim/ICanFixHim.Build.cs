// I Can Fix Him - AI Game Jam 2026

using UnrealBuildTool;

public class ICanFixHim : ModuleRules
{
	public ICanFixHim(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"DeveloperSettings",
			"UMG",
			"Slate",
			"SlateCore",
			"Json",
			"JsonUtilities"
		});

		// Feature folders are include roots, e.g. #include "Dialogue/DialogueTypes.h"
		PublicIncludePaths.Add(ModuleDirectory);
	}
}
