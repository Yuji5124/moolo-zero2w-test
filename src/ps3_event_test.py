"""Log Bluetooth-connected PS3 controller events without driving motors."""

from __future__ import annotations

import sys

from evdev import InputDevice, ecodes, list_devices


PRIORITY_CONTROLLER_NAME_HINTS = (
    "playstation",
    "sony",
    "sixaxis",
    "dualshock",
    "controller",
    "gamepad",
)

CONTROLLER_NAME_HINTS = (
    "playstation",
    "dualshock",
    "sony",
    "sixaxis",
    "ps3",
    "controller",
    "gamepad",
    "joystick",
)

AXIS_CODES = {
    ecodes.ABS_X: "ABS_X left stick horizontal",
    ecodes.ABS_Y: "ABS_Y left stick vertical",
}
for optional_code_name, label in (
    ("ABS_RX", "ABS_RX right stick horizontal"),
    ("ABS_RY", "ABS_RY right stick vertical"),
    ("ABS_Z", "ABS_Z"),
    ("ABS_RZ", "ABS_RZ"),
    ("ABS_HAT0X", "ABS_HAT0X d-pad horizontal"),
    ("ABS_HAT0Y", "ABS_HAT0Y d-pad vertical"),
):
    optional_code = getattr(ecodes, optional_code_name, None)
    if optional_code is not None:
        AXIS_CODES[optional_code] = label


def device_score(device: InputDevice) -> int:
    name = device.name.lower()
    capabilities = device.capabilities()
    keys = set(capabilities.get(ecodes.EV_KEY, []))
    axes = set(capabilities.get(ecodes.EV_ABS, []))

    score = 0
    if any(hint in name for hint in PRIORITY_CONTROLLER_NAME_HINTS):
        score += 5
    if any(hint in name for hint in CONTROLLER_NAME_HINTS):
        score += 3
    if ecodes.ABS_X in axes and ecodes.ABS_Y in axes:
        score += 3
    button_hints = tuple(
        code
        for code in (
            getattr(ecodes, "BTN_SOUTH", None),
            getattr(ecodes, "BTN_A", None),
            getattr(ecodes, "BTN_TL", None),
            getattr(ecodes, "BTN_TR", None),
        )
        if code is not None
    )
    if any(code in keys for code in button_hints):
        score += 2
    if axes:
        score += 1
    return score


def find_controller() -> InputDevice | None:
    candidates = []
    for path in list_devices():
        try:
            device = InputDevice(path)
            score = device_score(device)
        except OSError as exc:
            print(f"Skip {path}: {exc}")
            continue

        if score > 0:
            candidates.append((score, device))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def code_name(event_type: int, code: int) -> str:
    names = ecodes.bytype.get(event_type, {})
    name = names.get(code)
    if isinstance(name, list):
        return "/".join(name)
    if name:
        return name
    return f"type={event_type} code={code}"


def describe_abs(device: InputDevice, code: int, value: int) -> str:
    try:
        absinfo = device.absinfo(code)
        return (
            f"value={value} min={absinfo.min} max={absinfo.max} "
            f"flat={absinfo.flat} fuzz={absinfo.fuzz}"
        )
    except OSError:
        return f"value={value}"


def log_events(device: InputDevice) -> None:
    print(f"Using input device: {device.path}")
    print(f"Device name: {device.name}")
    print("Reading the PS3 controller event device created after Bluetooth connection.")
    print("Press buttons and move sticks. Ctrl+C to exit.")

    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            state = "pressed" if event.value else "released"
            print(f"button {code_name(event.type, event.code)} {state}")
        elif event.type == ecodes.EV_ABS:
            label = AXIS_CODES.get(event.code, code_name(event.type, event.code))
            print(f"axis {label}: {describe_abs(device, event.code, event.value)}")


def main() -> int:
    controller = find_controller()
    if controller is None:
        print("No controller-like /dev/input/event* device found.", file=sys.stderr)
        print("Connect the PS3 controller by Bluetooth and check permissions for /dev/input/event*.", file=sys.stderr)
        return 1

    try:
        log_events(controller)
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    finally:
        controller.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
