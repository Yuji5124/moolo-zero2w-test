# Project Journal

## 2026-05-04

- Raspberry Pi Zero 2 W 向けのモーター単体テスト用プロジェクトを作成。
- DRV8835-S と gpiozero を使う構成にした。
- GPIO割り当てを `GPIO5/AIN1`, `GPIO6/AIN2`, `GPIO13/BIN1`, `GPIO19/BIN2` に設定。
- 初期テスト速度を `0.2` に設定。
- `KeyboardInterrupt` と例外発生時に必ず `stop()` するテストスクリプトを追加。
