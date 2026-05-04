#!/usr/bin/env bash
set -euo pipefail

echo "== Raspberry Pi model =="
cat /proc/device-tree/model || true
echo

echo "== Bluetooth controller =="
bluetoothctl show || true
echo

echo "== Bluetooth service =="
systemctl status bluetooth --no-pager || true
echo

echo "== Input devices =="
ls /dev/input/ || true
