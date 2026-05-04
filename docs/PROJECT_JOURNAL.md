# Project Journal

## 2026-05-04

- Raspberry Pi Zero 2 W 向けのモーター単体テスト用プロジェクトを作成。
- DRV8835-S と gpiozero を使う構成にした。
- GPIO割り当てを `GPIO5/AIN1`, `GPIO6/AIN2`, `GPIO13/BIN1`, `GPIO19/BIN2` に設定。
- 初期テスト速度を `0.2` に設定。
- `KeyboardInterrupt` と例外発生時に必ず `stop()` するテストスクリプトを追加。

## 2026-05-04 実機テスト結果

- Phase 1: GPIO直接出力でA/B正転・逆転確認。
- Phase 2: PWMスイープでA/Bともに0.2から回転確認。
- 次の課題：motor_test.pyの動作時間を2秒にして再確認。

## 2026-05-04 PS3 Controller Phase Plan

- Phase 3は無線Bluetooth接続を前提に進める。
  - 初回ペアリングだけUSBを使う可能性がある。
  - 操作用入力はBluetooth接続後に作成される `/dev/input/event*` を `evdev` で読む。
  - Phase 3A: Bluetooth環境確認として `scripts/check_bluetooth.sh` でBlueZ、bluetoothサービス、入力デバイス、Piモデルを確認する。
  - Phase 3B: PS3コントローラー初回ペアリングではUSB接続をペアリング用途として扱う。
  - Phase 3C: 無線接続後の入力確認として `scripts/run_ps3_event_test.sh` でボタン入力とスティック入力をログ表示する。
- Phase 4: 無線PS3コントローラーによる低速モーター制御
  - `scripts/run_ps3_motor_drive.sh` でBluetooth接続後のevdev入力を読み、左スティックから低速走行制御する。
  - 初期最大速度は `0.3` とし、L1/R1で速度上限を調整する。
  - ×ボタン、Select、Start、入力タイムアウト、Ctrl+C、例外発生時は必ず `stop()` する。
  - 最初のテストでは必ず車輪を浮かせる。

## 2026-05-04 モーター方向補正

- Aモーターは取り付け方向の都合で前後が逆。
- 物理配線は維持し、config.py の `A_MOTOR_REVERSED = True` で補正。
- Bモーターは現状維持。
