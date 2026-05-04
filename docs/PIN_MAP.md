# Pin Map

GPIO番号は BCM 番号です。

| Name | Raspberry Pi GPIO | DRV8835-S Pin | Purpose |
| --- | ---: | --- | --- |
| LEFT_MOTOR_FORWARD_PIN | 5 | AIN1 | 左モーター前進側 |
| LEFT_MOTOR_BACKWARD_PIN | 6 | AIN2 | 左モーター後退側 |
| RIGHT_MOTOR_FORWARD_PIN | 13 | BIN1 | 右モーター前進側 |
| RIGHT_MOTOR_BACKWARD_PIN | 19 | BIN2 | 右モーター後退側 |

Python側の定義は [src/config.py](../src/config.py) にまとめています。
