"""Run the initial single-motor test sequence."""

from time import sleep

from config import DEFAULT_TEST_SPEED, STEP_DURATION_SECONDS, STOP_DURATION_SECONDS
from motor_driver import MotorDriver


def stop_pause(driver: MotorDriver) -> None:
    driver.stop()
    sleep(STOP_DURATION_SECONDS)


def run_test() -> None:
    driver = MotorDriver()

    try:
        print(f"Starting motor test at speed {DEFAULT_TEST_SPEED}")

        print("Left motor forward")
        driver.left_forward(DEFAULT_TEST_SPEED)
        sleep(STEP_DURATION_SECONDS)
        stop_pause(driver)

        print("Left motor backward")
        driver.left_backward(DEFAULT_TEST_SPEED)
        sleep(STEP_DURATION_SECONDS)
        stop_pause(driver)

        print("Right motor forward")
        driver.right_forward(DEFAULT_TEST_SPEED)
        sleep(STEP_DURATION_SECONDS)
        stop_pause(driver)

        print("Right motor backward")
        driver.right_backward(DEFAULT_TEST_SPEED)
        sleep(STEP_DURATION_SECONDS)

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
