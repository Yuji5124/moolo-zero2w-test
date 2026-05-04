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

## 2026-05-04 モーター方向補正

- Aモーターは取り付け方向の都合で前後が逆。
- 物理配線は維持し、config.py の `A_MOTOR_REVERSED = True` で補正。
- Bモーターは現状維持。
