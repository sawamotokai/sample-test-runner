#!/bin/bash
set -euo pipefail
install_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
bin_dir="$HOME/.local/bin"
uv venv --python 3.12 --allow-existing "$install_dir/.venv"
uv pip sync --python "$install_dir/.venv/bin/python" "$install_dir/requirements.txt"
mkdir -p "$bin_dir"
for command in cprun cpget; do
  destination="$bin_dir/$command"
  if [[ -e "$destination" || -L "$destination" ]]; then
    if [[ ! -L "$destination" || "$(readlink "$destination")" != "$install_dir/src/$command" ]]; then
      echo "Refusing to replace existing command: $destination" >&2
      exit 1
    fi
  else
    ln -s "$install_dir/src/$command" "$destination"
  fi
  chmod +x "$install_dir/src/$command"
done
printf 'Installed cprun and cpget in %s\n' "$bin_dir"

if command -v fish >/dev/null 2>&1; then
  fish_dir="${XDG_CONFIG_HOME:-$HOME/.config}/fish/conf.d"
  fish_config="$fish_dir/sample-test-runner.fish"
  mkdir -p "$fish_dir"
  if [[ -e "$fish_config" ]] && ! cmp -s "$fish_config" "$install_dir/integrations/fish/sample-test-runner.fish"; then
    echo "Existing fish integration kept: $fish_config"
  else
    cp "$install_dir/integrations/fish/sample-test-runner.fish" "$fish_config"
  fi
fi
