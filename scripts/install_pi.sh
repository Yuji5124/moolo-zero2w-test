#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

sudo apt-get update
sudo apt-get install -y \
  bluez \
  bluetooth \
  joystick \
  evtest \
  python3-evdev

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install gpiozero lgpio evdev

echo "Install complete. Activate with: source .venv/bin/activate"
