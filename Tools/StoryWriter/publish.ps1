# Builds self-contained single-file StoryWriter executables into Tools/StoryWriter/dist/<rid>/.
# Usage: ./publish.ps1 [rid ...]   (default: win-x64 linux-x64 osx-arm64 osx-x64)
param([string[]]$Rids = @('win-x64', 'linux-x64', 'osx-arm64', 'osx-x64'))
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

foreach ($rid in $Rids) {
	Write-Host "== $rid =="
	dotnet publish StoryWriter.csproj -c Release -r $rid --self-contained true `
		-p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true `
		-p:EnableCompressionInSingleFile=true -p:DebugType=None -p:DebugSymbols=false `
		-o "dist/$rid"
	Remove-Item "dist/$rid/*.pdb" -ErrorAction SilentlyContinue
	if ($LASTEXITCODE -ne 0) { throw "publish failed for $rid" }
}
Write-Host "Done. Executables are in $PSScriptRoot/dist"
