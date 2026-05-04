"""Run PWM sweep tests for each motor."""

from time import sleep

from config import (
    LEFT_MOTOR_BACKWARD_PIN,
    LEFT_MOTOR_FORWARD_PIN,
    RIGHT_MOTOR_BACKWARD_PIN,
    RIGHT_MOTOR_FORWARD_PIN,
    STOP_DURATION_SECONDS,
)
from motor_driver import MotorDriver

SWEEP_SPEEDS = (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)
SWEEP_DURATION_SECONDS = 2.0


def stop_pause(driver: MotorDriver) -> None:
    print(f"Stop for {STOP_DURATION_SECONDS} seconds")
    driver.stop()
    sleep(STOP_DURATION_SECONDS)


def print_test_config() -> None:
    print("GPIO map:")
    print(f"  Left forward  GPIO{LEFT_MOTOR_FORWARD_PIN} -> AIN1")
    print(f"  Left backward GPIO{LEFT_MOTOR_BACKWARD_PIN} -> AIN2")
    print(f"  Right forward GPIO{RIGHT_MOTOR_FORWARD_PIN} -> BIN1")
    print(f"  Right backward GPIO{RIGHT_MOTOR_BACKWARD_PIN} -> BIN2")
    print(f"Speeds: {', '.join(str(speed) for speed in SWEEP_SPEEDS)}")
    print(f"Move duration: {SWEEP_DURATION_SECONDS} seconds")
    print(f"Stop duration: {STOP_DURATION_SECONDS} seconds")


def sweep_motor(driver: MotorDriver, motor_name: str) -> None:
    for speed in SWEEP_SPEEDS:
        print(f"{motor_name} motor forward at speed {speed} for {SWEEP_DURATION_SECONDS} seconds")
        if motor_name == "Left":
            driver.left_forward(speed)
        else:
            driver.right_forward(speed)
        sleep(SWEEP_DURATION_SECONDS)
        stop_pause(driver)


def run_test() -> None:
    driver = MotorDriver()

    try:
        print_test_config()
        sweep_motor(driver, "Left")
        sweep_motor(driver, "Right")

    except KeyboardInterrupt:
        print("Interrupted. Stopping motors.")
        raise
    except Exception:
        print("Error occurred. Stopping motors.")
        raise
    finally:
        driver.stop()
        print("Motors stopped.")


if __name__ == "__main__":
    run_test()
