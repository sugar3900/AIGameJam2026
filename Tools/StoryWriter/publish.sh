#!/usr/bin/env bash
# Builds self-contained single-file StoryWriter executables into Tools/StoryWriter/dist/<rid>/.
# Usage: ./publish.sh [rid ...]   (default: win-x64 linux-x64 osx-arm64 osx-x64)
set -euo pipefail
cd "$(dirname "$0")"

rids=("$@")
[ ${#rids[@]} -eq 0 ] && rids=(win-x64 linux-x64 osx-arm64 osx-x64)

for rid in "${rids[@]}"; do
	echo "== $rid =="
	dotnet publish StoryWriter.csproj -c Release -r "$rid" --self-contained true \
		-p:PublishSingleFile=true \
		-p:IncludeNativeLibrariesForSelfExtract=true \
		-p:EnableCompressionInSingleFile=true \
		-p:DebugType=None -p:DebugSymbols=false \
		-o "dist/$rid"
	rm -f "dist/$rid"/*.pdb
done
echo "Done. Executables are in $(pwd)/dist"
