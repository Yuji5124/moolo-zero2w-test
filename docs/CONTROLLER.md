# PS3 Controller

PS3コントローラーの通常操作はBluetooth無線接続を前提にします。
USB接続は操作用ではなく、初回ペアリング時に必要になる可能性がある接続として扱います。

モーター操作コードは、Bluetooth接続後に作成される `/dev/input/event*` を `evdev` で読みます。

## Phase 3A: Bluetooth環境確認

Raspberry Pi Zero 2 W 上で依存パッケージを導入します。

```bash
bash scripts/install_pi.sh
```

Bluetoothサービス、Piのモデル、入力デバイスの状態を確認します。

```bash
bash scripts/check_bluetooth.sh
```

確認するポイント:

- `bluetoothctl show` でBluetoothコントローラー情報が表示される
- `systemctl status bluetooth --no-pager` でBluetoothサービスが動作している
- `/dev/input/` に入力デバイスが表示される
- `/proc/device-tree/model` が Raspberry Pi Zero 2 W である

## Phase 3B: PS3コントローラー初回ペアリング

PS3コントローラーは初回ペアリング時だけUSB接続が必要になる可能性があります。
このUSB接続は操作確認用ではなく、Pi側へペアリング情報を登録するためのものです。

初回ペアリングの流れ:

1. PS3コントローラーをUSBでPiに接続する。
2. `bluetoothctl` やBlueZ系ツールでペアリング状態を確認する。
3. ペアリング後、USBを外す。
4. PSボタンでBluetooth接続できるか確認する。
5. Bluetooth接続後に `/dev/input/event*` が増えるか確認する。

接続状態の確認には次を使います。

```bash
bash scripts/check_bluetooth.sh
```

## Phase 3C: 無線接続後の入力確認

PS3コントローラーをBluetooth接続した後、入力確認スクリプトを実行します。
この段階ではモーターは動きません。

```bash
bash scripts/run_ps3_event_test.sh
```

スクリプトは `/dev/input/event*` からPS3コントローラーらしいデバイスを探し、検出したデバイス名、ボタン入力、スティック入力をログ表示します。

入力デバイスを開けない場合は、ユーザーが input グループに入っているか確認してください。切り分け時だけ `sudo` で実行して権限問題かどうかを確認します。

## Phase 4: 無線PS3コントローラーによる低速走行テスト

入力確認でボタンとスティックが読めることを確認してから、必ず車輪を浮かせた状態で低速走行テストを実行します。

```bash
bash scripts/run_ps3_motor_drive.sh
```

操作:

- 左スティック上: 前進
- 左スティック下: 後退
- 左スティック左: 左旋回
- 左スティック右: 右旋回
- ×ボタン: 停止
- Select/Start: 停止
- L1: 最大速度を下げる
- R1: 最大速度を上げる

初期最大速度は `0.3` です。スティック中央付近にはデッドゾーンを設けています。
一定時間入力がない場合、Ctrl+C、例外発生時は必ず `stop()` します。
