# moolo-zero2w-test

Raspberry Pi Zero 2 W で Moolo の走行系を確認するための Python プロジェクトです。

現在の対象は DRV8835-S モータードライバーと左右2個のタミヤミニモーターの単体テストです。PS3コントローラー対応は後で追加します。

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

## PS3 Controller

PS3コントローラーはBluetooth無線接続後に操作します。初回ペアリング時のみUSB接続が必要になる場合がありますが、有線USBは操作用ではなくペアリング用として扱います。

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
