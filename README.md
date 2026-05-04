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

初期テスト速度は `0.2` です。変更する場合は [src/config.py](src/config.py) の `DEFAULT_TEST_SPEED` を編集してください。

## Test Sequence

1. 左モーター前進 0.5秒
2. 停止 1秒
3. 左モーター後退 0.5秒
4. 停止 1秒
5. 右モーター前進 0.5秒
6. 停止 1秒
7. 右モーター後退 0.5秒
8. 完全停止
