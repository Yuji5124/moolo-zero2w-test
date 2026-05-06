# moolo-zero2w-test

Raspberry Pi Zero 2 W で Moolo の走行系を確認するための Python プロジェクトです。

現在の対象は DRV8835-S モータードライバーと左右2個のタミヤミニモーターの単体テスト、およびPS3コントローラーによるBluetooth無線走行制御です。現時点では左スティック操作によるモーター制御に成功済みです。

## Safety

- 最初は車輪を浮かせてテストしてください。
- Pi本体の電源はモバイルバッテリー5V、モーター用電源は単三電池4本を使います。
- PiのGND、DRV8835-SのGND、電池マイナスは共通にしてください。
- モーター用の単三電池4本は DRV8835-S の VM に接続し、Pi の 5V には接続しないでください。

## GPIO Pin Map

| Raspberry Pi GPIO | DRV8835-S |
| --- | --- |
| GPIO5 | AIN1 |
| GPIO6 | AIN2 |
| GPIO13 | BIN1 |
| GPIO19 | BIN2 |

詳細は [docs/WIRING.md](docs/WIRING.md) と [docs/PIN_MAP.md](docs/PIN_MAP.md) を参照してください。

## Setup On Raspberry Pi

```bash
cd moolo-zero2w-test
bash scripts/install_pi.sh
```

## Run Motor Test

```bash
bash scripts/run_motor_test.sh
```

まず `scripts/run_motor_test.sh` を実行してください。動きが見えにくい場合は `scripts/run_pwm_sweep.sh` で最低動作PWMを確認してください。

```bash
bash scripts/run_pwm_sweep.sh
```

今回の実機ではA/BともにPWM 0.2から回転確認済みです。

初期テスト速度は `0.2` です。変更する場合は [src/config.py](src/config.py) の `DEFAULT_TEST_SPEED` を編集してください。

前後方向が逆の場合は [src/config.py](src/config.py) の `A_MOTOR_REVERSED` / `B_MOTOR_REVERSED` で調整してください。現在はAモーターのみ取り付け向き補正のため `A_MOTOR_REVERSED = True` です。

## Smartphone Web Controller

Bluetooth 接続が不安定な場合は、Wi-Fi 経由のスマホ Web コントローラーを使用できます。

> **最初は必ず車輪を浮かせてテストしてください。**

### 起動方法

```bash
bash scripts/run_web_controller.sh
```

### アクセス方法

1. Pi とスマホを同じ Wi-Fi に接続します。
2. Pi 側で IP アドレスを確認します。

```bash
hostname -I
```

3. スマホのブラウザで次の URL を開きます。

```
http://<Pi の IP アドレス>:8080
```

例：`http://192.168.128.193:8080`

### 操作

- ▲ / ▼ / ◄ / ► ボタンを**押している間**だけ動きます。
- 指を離すと停止します。
- STOP ボタンで即時停止します。
- 速度スライダーで速度を調整できます（0.5〜1.0）。
- ページを閉じたり通信が途切れた場合も自動停止します。

### 走行確認状況

スマホ Web コントローラーによる Moolo の走行は成功済みです（Wi-Fi 経由・球体ケース収納状態）。

ただし、**左右旋回の方向は実機テストで必ず確認してください**。球体ロボットの内部機構の向きによっては、`turn_left` / `turn_right` の物理的な挙動が期待と異なる場合があります。必要に応じて `src/motor_driver.py` の `turn_left()` / `turn_right()` 内のモーター指示を入れ替えるか、`config.py` の `A_MOTOR_REVERSED` / `B_MOTOR_REVERSED` を調整してください。

方向確認には専用テストスクリプトを使用してください。

```bash
bash scripts/run_drive_direction_test.sh
```

詳しくは [docs/WEB_CONTROLLER.md](docs/WEB_CONTROLLER.md) を参照してください。

## PS3 Controller

PS3コントローラーはBluetooth無線接続後に操作します。初回ペアリング時のみUSB接続が必要になる場合がありますが、有線USBは操作用ではなくペアリング用として扱います。

実機テストでは `scripts/run_ps3_motor_drive.sh` により、左スティック操作でMooloのモーター制御に成功済みです。現在の成功範囲は左スティック操作のみで、右スティックや追加ボタン操作は今後のPhaseで拡張します。

まずBluetooth環境と入力デバイスの状態を確認します。

```bash
bash scripts/check_bluetooth.sh
```

PS3コントローラーをBluetooth接続した後、入力確認だけを実行します。この段階ではモーターは動きません。

```bash
bash scripts/run_ps3_event_test.sh
```

ボタン入力とスティック入力が確認できたら、必ず車輪を浮かせた状態でBluetooth接続後の低速モーター制御を実行します。

```bash
bash scripts/run_ps3_motor_drive.sh
```

詳しい操作と注意点は [docs/CONTROLLER.md](docs/CONTROLLER.md) を参照してください。

## Test Sequence

1. 左モーター前進 2.0秒
2. 停止 1秒
3. 左モーター後退 2.0秒
4. 停止 1秒
5. 右モーター前進 2.0秒
6. 停止 1秒
7. 右モーター後退 2.0秒
8. 完全停止
