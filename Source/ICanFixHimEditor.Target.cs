// I Can Fix Him - AI Game Jam 2026

using UnrealBuildTool;

public class ICanFixHimEditorTarget : TargetRules
{
	public ICanFixHimEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
		ExtraModuleNames.Add("ICanFixHim");
	}
}
