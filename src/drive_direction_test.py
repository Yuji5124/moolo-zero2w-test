"""Drive direction verification test for Moolo.

Runs forward / backward / turn_left / turn_right in sequence and logs
which motors are logically driven in each step.  Use this to verify that
the physical robot motion matches the expected direction before operating
the web controller.

Safety:
  - Lift the wheels off the ground before running.
  - Ctrl+C or any exception stops all motors immediately.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor_driver import MotorDriver  # noqa: E402

TEST_SPEED = 0.3
DRIVE_DURATION = 2.0
STOP_DURATION = 1.0

# (label, motor-intent description, callable)
STEPS = [
    (
        "forward",
        "Left  motor: FORWARD  |  Right motor: FORWARD  → robot should go straight ahead",
        lambda m: m.forward(TEST_SPEED),
    ),
    (
        "backward",
        "Left  motor: BACKWARD |  Right motor: BACKWARD → robot should go straight back",
        lambda m: m.backward(TEST_SPEED),
    ),
    (
        "turn_left",
        "Left  motor: BACKWARD |  Right motor: FORWARD  → robot should spin LEFT in place",
        lambda m: m.turn_left(TEST_SPEED),
    ),
    (
        "turn_right",
        "Left  motor: FORWARD  |  Right motor: BACKWARD → robot should spin RIGHT in place",
        lambda m: m.turn_right(TEST_SPEED),
    ),
]


def run_steps(motor: MotorDriver) -> None:
    for name, description, action in STEPS:
        print()
        print(f"  [{name.upper()}]")
        print(f"  {description}")
        print(f"  Running {DRIVE_DURATION:.1f} s ...", flush=True)
        action(motor)
        time.sleep(DRIVE_DURATION)
        motor.stop()
        print(f"  Stopped. Waiting {STOP_DURATION:.1f} s ...", flush=True)
        time.sleep(STOP_DURATION)


def main() -> None:
    motor = MotorDriver()
    print()
    print("=" * 58)
    print("  Moolo Drive Direction Test")
    print(f"  Speed : {TEST_SPEED}")
    print(f"  Steps : forward → backward → turn_left → turn_right")
    print()
    print("  !!! Lift wheels off the ground before running !!!")
    print("=" * 58)

    try:
        run_steps(motor)
        print()
        print("  All steps complete.")
        print()
        print("  If turn_left / turn_right produce unexpected motion,")
        print("  swap left_backward ↔ left_forward inside motor_driver.py")
        print("  turn_left() / turn_right(), or swap A_MOTOR_REVERSED flag.")
    except KeyboardInterrupt:
        print("\n  [INTERRUPTED] Stopping motors.")
    except Exception as exc:
        print(f"\n  [ERROR] {exc}")
    finally:
        motor.stop()
        print("  Motors stopped.")


if __name__ == "__main__":
    main()
