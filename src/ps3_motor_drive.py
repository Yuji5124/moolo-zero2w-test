"""Drive motors from a Bluetooth-connected PS3 controller using evdev."""

from __future__ import annotations

import select
import time

from evdev import InputDevice, ecodes

from motor_driver import MotorDriver
from ps3_event_test import find_controller


DEAD_ZONE = 0.12
INITIAL_MAX_SPEED = 0.3
MIN_MAX_SPEED = 0.1
MAX_MAX_SPEED = 0.6
SPEED_STEP = 0.05
INPUT_TIMEOUT_SECONDS = 0.5
LOOP_SLEEP_SECONDS = 0.02

STOP_BUTTON_CODES = {
    code
    for code in (
        getattr(ecodes, "BTN_SOUTH", None),  # Cross on common PS3 mappings.
        getattr(ecodes, "BTN_A", None),
        getattr(ecodes, "BTN_SELECT", None),
        getattr(ecodes, "BTN_START", None),
    )
    if code is not None
}
SPEED_DOWN_BUTTON_CODES = {code for code in (getattr(ecodes, "BTN_TL", None),) if code is not None}
SPEED_UP_BUTTON_CODES = {code for code in (getattr(ecodes, "BTN_TR", None),) if code is not None}


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def normalize_axis(device: InputDevice, code: int, value: int, invert: bool = False) -> float:
    absinfo = device.absinfo(code)
    center = (absinfo.max + absinfo.min) / 2.0
    span = max(absinfo.max - center, center - absinfo.min, 1.0)
    normalized = (value - center) / span
    normalized = clamp(normalized, -1.0, 1.0)
    if invert:
        normalized = -normalized
    if abs(normalized) < DEAD_ZONE:
        return 0.0
    return normalized


def set_motor(driver: MotorDriver, left: float, right: float) -> None:
    if left > 0:
        driver.left_forward(left)
    elif left < 0:
        driver.left_backward(abs(left))
    else:
        driver.left_forward(0)

    if right > 0:
        driver.right_forward(right)
    elif right < 0:
        driver.right_backward(abs(right))
    else:
        driver.right_forward(0)


def drive_from_stick(driver: MotorDriver, throttle: float, turn: float, max_speed: float) -> None:
    left = clamp(throttle + turn, -1.0, 1.0) * max_speed
    right = clamp(throttle - turn, -1.0, 1.0) * max_speed
    if left == 0.0 and right == 0.0:
        driver.stop()
    else:
        set_motor(driver, left, right)


def run_drive() -> None:
    controller = find_controller()
    if controller is None:
        raise RuntimeError("No controller-like /dev/input/event* device found.")

    driver = MotorDriver()
    throttle = 0.0
    turn = 0.0
    max_speed = INITIAL_MAX_SPEED
    last_input_time = time.monotonic()
    stopped_by_timeout = False

    try:
        print(f"Using input device: {controller.path}")
        print(f"Device name: {controller.name}")
        print("Reading the PS3 controller event device created after Bluetooth connection.")
        print(f"Max speed: {max_speed:.2f}")
        print("Controls: left stick to drive, Cross/Select/Start to stop, L1/R1 speed down/up.")
        print("Keep the wheels lifted for the first test. Ctrl+C to exit.")

        while True:
            readable, _, _ = select.select([controller.fd], [], [], LOOP_SLEEP_SECONDS)
            now = time.monotonic()

            if not readable:
                if now - last_input_time > INPUT_TIMEOUT_SECONDS and not stopped_by_timeout:
                    driver.stop()
                    stopped_by_timeout = True
                    print("Input timeout. Motors stopped.")
                continue

            for event in controller.read():
                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_Y:
                        throttle = normalize_axis(controller, event.code, event.value, invert=True)
                    elif event.code == ecodes.ABS_X:
                        turn = normalize_axis(controller, event.code, event.value)
                    else:
                        continue

                    last_input_time = now
                    stopped_by_timeout = False
                    drive_from_stick(driver, throttle, turn, max_speed)
                    print(f"drive throttle={throttle:+.2f} turn={turn:+.2f} max_speed={max_speed:.2f}")

                elif event.type == ecodes.EV_KEY and event.value == 1:
                    last_input_time = now
                    stopped_by_timeout = False

                    if event.code in STOP_BUTTON_CODES:
                        throttle = 0.0
                        turn = 0.0
                        driver.stop()
                        print("Stop button pressed. Motors stopped.")
                    elif event.code in SPEED_DOWN_BUTTON_CODES:
                        max_speed = clamp(max_speed - SPEED_STEP, MIN_MAX_SPEED, MAX_MAX_SPEED)
                        print(f"Max speed: {max_speed:.2f}")
                    elif event.code in SPEED_UP_BUTTON_CODES:
                        max_speed = clamp(max_speed + SPEED_STEP, MIN_MAX_SPEED, MAX_MAX_SPEED)
                        print(f"Max speed: {max_speed:.2f}")

    except KeyboardInterrupt:
        print("\nInterrupted. Stopping motors.")
        raise
    except Exception:
        print("Error occurred. Stopping motors.")
        raise
    finally:
        driver.stop()
        controller.close()
        print("Motors stopped.")


if __name__ == "__main__":
    run_drive()
