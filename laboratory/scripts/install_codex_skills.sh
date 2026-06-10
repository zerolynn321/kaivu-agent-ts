#!/usr/bin/env bash
set -euo pipefail

repo_url="${SKILLS_REPO_URL:-https://github.com/openai/skills.git}"
ref="${SKILLS_REPO_REF:-main}"
workdir="${SKILLS_CLONE_DIR:-/tmp/openai-skills}"
dest="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"

if [ "$#" -gt 0 ]; then
  skills=("$@")
else
  # Useful for paper repos that keep exploratory notebooks or PDFs.
  # AutoSOTA's dataset/model acquisition remains implemented in this repo.
  skills=("jupyter-notebook" "pdf")
fi

case "$workdir" in
  ""|"/"|"$HOME"|"$dest")
    echo "refusing unsafe SKILLS_CLONE_DIR: $workdir" >&2
    exit 2
    ;;
esac

if [ ! -d "$workdir/.git" ]; then
  rm -rf "$workdir"
  git clone --depth 1 --branch "$ref" "$repo_url" "$workdir"
else
  git -C "$workdir" fetch --depth 1 origin "$ref"
  git -C "$workdir" checkout "$ref"
  git -C "$workdir" pull --ff-only origin "$ref"
fi

mkdir -p "$dest"

installed=0
for skill in "${skills[@]}"; do
  src=""
  for base in "$workdir/skills/.curated" "$workdir/skills/.experimental"; do
    if [ -d "$base/$skill" ]; then
      src="$base/$skill"
      break
    fi
  done

  if [ -z "$src" ]; then
    echo "skip: skill not found: $skill"
    continue
  fi

  if [ -e "$dest/$skill" ]; then
    echo "skip: already installed: $dest/$skill"
    continue
  fi

  cp -R "$src" "$dest/$skill"
  echo "installed: $skill -> $dest/$skill"
  installed=$((installed + 1))
done

echo "done: installed=$installed dest=$dest"
echo "Restart Codex or start a new codex exec session to pick up new skills."
