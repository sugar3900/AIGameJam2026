// I Can Fix Him - AI Game Jam 2026

using UnrealBuildTool;

public class ICanFixHimTarget : TargetRules
{
	public ICanFixHimTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
		ExtraModuleNames.Add("ICanFixHim");
	}
}
