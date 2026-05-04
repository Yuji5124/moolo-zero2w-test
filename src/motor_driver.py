"""Motor driver wrapper for DRV8835-S IN/IN mode using gpiozero."""

from gpiozero import PWMOutputDevice

from config import (
    A_MOTOR_REVERSED,
    B_MOTOR_REVERSED,
    LEFT_MOTOR_BACKWARD_PIN,
    LEFT_MOTOR_FORWARD_PIN,
    RIGHT_MOTOR_BACKWARD_PIN,
    RIGHT_MOTOR_FORWARD_PIN,
)


class MotorDriver:
    """Control left and right motors through a DRV8835-S driver."""

    def __init__(self) -> None:
        self.left_forward_pin = PWMOutputDevice(LEFT_MOTOR_FORWARD_PIN, initial_value=0)
        self.left_backward_pin = PWMOutputDevice(LEFT_MOTOR_BACKWARD_PIN, initial_value=0)
        self.right_forward_pin = PWMOutputDevice(RIGHT_MOTOR_FORWARD_PIN, initial_value=0)
        self.right_backward_pin = PWMOutputDevice(RIGHT_MOTOR_BACKWARD_PIN, initial_value=0)

    def forward(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_forward(speed)
        self.right_forward(speed)

    def backward(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_backward(speed)
        self.right_backward(speed)

    def turn_left(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_backward(speed)
        self.right_forward(speed)

    def turn_right(self, speed: float) -> None:
        speed = self._normalize_speed(speed)
        self.left_forward(speed)
        self.right_backward(speed)

    def left_forward(self, speed: float) -> None:
        self._set_left_motor(speed, forward=True)

    def left_backward(self, speed: float) -> None:
        self._set_left_motor(speed, forward=False)

    def right_forward(self, speed: float) -> None:
        self._set_right_motor(speed, forward=True)

    def right_backward(self, speed: float) -> None:
        self._set_right_motor(speed, forward=False)

    def _set_left_motor(self, speed: float, forward: bool) -> None:
        speed = self._normalize_speed(speed)
        physical_forward = forward != A_MOTOR_REVERSED
        self.left_forward_pin.value = speed if physical_forward else 0
        self.left_backward_pin.value = 0 if physical_forward else speed

    def _set_right_motor(self, speed: float, forward: bool) -> None:
        speed = self._normalize_speed(speed)
        physical_forward = forward != B_MOTOR_REVERSED
        self.right_forward_pin.value = speed if physical_forward else 0
        self.right_backward_pin.value = 0 if physical_forward else speed

    def stop(self) -> None:
        self.left_forward_pin.value = 0
        self.left_backward_pin.value = 0
        self.right_forward_pin.value = 0
        self.right_backward_pin.value = 0

    @staticmethod
    def _normalize_speed(speed: float) -> float:
        if speed < 0.0:
            return 0.0
        if speed > 1.0:
            return 1.0
        return speed
