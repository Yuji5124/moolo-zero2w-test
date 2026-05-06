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

## 2026-05-05 Phase 4 実機テスト結果

- Phase 4結果：左スティックによるPS3無線走行制御成功。
- PS3コントローラーのBluetooth接続に成功。
- `run_ps3_motor_drive.sh` で左スティック操作が効いた。
- 左スティックのみでMooloのモーター制御に成功。
- Bluetooth → evdev → MotorDriver → DRV8835-S → モーター の制御経路が動作確認できた。
- 現在の成功範囲：左スティック操作。
- 現時点では左スティック操作のみ成功。
- 右スティックや追加ボタン操作は今後のPhaseで拡張する。

次の課題：

1. 速度調整ボタン L1/R1 の確認
2. 停止ボタンの確認
3. 操作方向の微調整
4. 床置き低速テスト
5. 右スティックや追加ボタンへの機能割り当て

## 2026-05-06 Phase 5: スマホ Web コントローラー追加

- PS3/PS4 Bluetooth コントローラーの接続が不安定だったため、Wi-Fi 経由のブラウザ操作方式に切り替えることにした。
- Flask を使い、Raspberry Pi Zero 2 W 上で HTTP サーバー（0.0.0.0:8080）を起動する構成にした。
- スマホブラウザから大きなボタンで前進・後退・左右旋回・停止を操作できる UI を実装した。
- ボタンを押している間だけ走行し、指を離したら必ず停止する設計にした。
- ページクローズ / 非表示 / 通信断に対応する多重安全停止を実装した（JS の sendBeacon + サーバー側ウォッチドッグ 0.5 秒）。
- 速度上限を 0.5 に制限し、初期速度を 0.2 に設定した。

### 追加・変更ファイル

| ファイル | 変更内容 |
|---------|----------|
| `src/web_controller.py` | Flask サーバー新規作成 |
| `scripts/run_web_controller.sh` | 起動スクリプト新規作成 |
| `docs/WEB_CONTROLLER.md` | ドキュメント新規作成 |
| `scripts/install_pi.sh` | flask を pip install 対象に追加 |
| `README.md` | スマホ Web コントローラーセクション追加 |

### 次の確認項目

1. スマホから画面が開ける
2. 前進・後退・左右旋回が効く
3. 指を離すと停止する
4. ページを閉じると停止する
5. 床置き低速テスト

## 2026-05-06 Phase 5 実機テスト結果

### 成功

- スマホ Web コントローラーによる Moolo 走行成功。
- Wi-Fi 経由でスマホブラウザから操作できた。
- Raspberry Pi Zero 2 W → DRV8835-S → 左右モーター制御の経路が動作確認できた。
- 球体ケース内に電子部品と電池を収めた状態で走行確認できた。
- Bluetooth コントローラー方式ではなく、Web コントローラー方式が有効と判断。

### 実機で確認した問題

| 操作 | 期待する挙動 | 実際の挙動 |
|------|-------------|-----------|
| 左ボタン | 左旋回 | まっすぐ進む |
| 右ボタン | 右旋回 | 後ろに進む |

### 原因分析

コードのマッピングを確認した結果、以下はすべて正しく実装済みだった。

- `web_controller.py`: `"left"` → `motor.turn_left()`, `"right"` → `motor.turn_right()` ✓
- `motor_driver.py`: `turn_left` = left_backward + right_forward ✓
- `motor_driver.py`: `turn_right` = left_forward + right_backward ✓

GPIO ピンレベルでの出力は以下の通り。

| 動作 | AIN1(GPIO5) | AIN2(GPIO6) | BIN1(GPIO13) | BIN2(GPIO19) |
|------|-------------|-------------|--------------|--------------|
| forward | 0 | speed | speed | 0 |
| backward | speed | 0 | 0 | speed |
| turn_left | speed | 0 | speed | 0 |
| turn_right | 0 | speed | 0 | speed |

`turn_left` は AIN1・BIN1 が同時に ON になる組み合わせであり、球体内部の物理的な機構（モーター配置・ケース形状）によっては、内部の差動回転が球体の直進方向への転がりとして現れる可能性がある。コード自体にバグはない。

### 対応

- `src/drive_direction_test.py` を追加し、各方向の意図とモーター論理を明示したうえで実機で挙動を確認できるようにした。
- `scripts/run_drive_direction_test.sh` を追加した。
- 物理挙動が期待と異なる場合は `motor_driver.py` の `turn_left` / `turn_right` 内のモーター指示を入れ替えることで調整できる。

### 次の確認項目

1. `bash scripts/run_drive_direction_test.sh` で各方向の実機挙動を確認する
2. 左右旋回が期待通りかチェックし、必要なら `turn_left` / `turn_right` のモーター割り当てを入れ替える
3. 方向が確定したら床置き低速テストを実施する
