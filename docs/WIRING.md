# Wiring

Moolo の初期モーター単体テスト用の配線メモです。

## Power

- Pi本体の電源はモバイルバッテリー5Vを使います。
- 単三電池4本はDRV8835-SのVMへ接続し、Piの5Vには絶対接続しないでください。
- PiのGND、DRV8835-SのGND、電池マイナスは共通にしてください。

## Motor Driver

DRV8835-S の入力ピンを Raspberry Pi の GPIO に接続します。

| Raspberry Pi GPIO | DRV8835-S |
| --- | --- |
| GPIO5 | AIN1 |
| GPIO6 | AIN2 |
| GPIO13 | BIN1 |
| GPIO19 | BIN2 |

## Motors

- 左モーターを DRV8835-S の AOUT 側に接続します。
- 右モーターを DRV8835-S の BOUT 側に接続します。

モーターの回転方向が想定と逆の場合は、該当モーターの端子を入れ替えるか、[src/config.py](../src/config.py) のピン定義を入れ替えて確認してください。

## First Test

最初は車輪を浮かせた状態で [src/motor_test.py](../src/motor_test.py) を実行し、低速で左右の回転方向を確認してください。
