"""Motor driver wrapper for DRV8835-S using gpiozero."""

from gpiozero import Motor

from config import (
    LEFT_MOTOR_BACKWARD_PIN,
    LEFT_MOTOR_FORWARD_PIN,
    RIGHT_MOTOR_BACKWARD_PIN,
    RIGHT_MOTOR_FORWARD_PIN,
)


class MotorDriver:
    """Control left and right motors through a DRV8835-S driver."""

    def __init__(self) -> None:
        self.left_motor = Motor(
            forward=LEFT_MOTOR_FORWARD_PIN,
            backward=LEFT_MOTOR_BACKWARD_PIN,
            pwm=True,
        )
        self.right_motor = Motor(
            forward=RIGHT_MOTOR_FORWARD_PIN,
            backward=RIGHT_MOTOR_BACKWARD_PIN,
            pwm=True,
        )

    def forward(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_motor.forward(speed)
        self.right_motor.forward(speed)

    def backward(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_motor.backward(speed)
        self.right_motor.backward(speed)

    def turn_left(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_motor.backward(speed)
        self.right_motor.forward(speed)

    def turn_right(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_motor.forward(speed)
        self.right_motor.backward(speed)

    def left_forward(self, speed: float) -> None:
        self.left_motor.forward(self._normalize_speed(speed))

    def left_backward(self, speed: float) -> None:
        self.left_motor.backward(self._normalize_speed(speed))

    def right_forward(self, speed: float) -> None:
        self.right_motor.forward(self._normalize_speed(speed))

    def right_backward(self, speed: float) -> None:
        self.right_motor.backward(self._normalize_speed(speed))

    def stop(self) -> None:
        self.left_motor.stop()
        self.right_motor.stop()

    @staticmethod
    def _normalize_speed(speed: float) -> float:
        if speed < 0.0:
            return 0.0
        if speed > 1.0:
            return 1.0
        return speed
