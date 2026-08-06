# Raspberry Pi GPIO / Vision Test Scripts

This folder is a progression of test scripts building up from basic GPIO blink tests
to a full MediaPipe hand-tracking + color-detection + servo-pointer project
(`test12.py`). Files are numbered roughly in the order they were built.

---

## Hardware

- Raspberry Pi 4 (BCM2835/2711 GPIO, `/dev/gpiochip0`)
- USB webcam (UVC), shows up as `/dev/video0` once plugged in
- Various: LEDs, push buttons, HC-SR04 ultrasonic sensor, DC motor + driver (L298N-style,
  IN1/IN2/ENA), SG90-class servo

## Environment

| Component | Version |
|---|---|
| OS | Debian GNU/Linux 13 (trixie), Raspberry Pi reference build |
| Architecture | aarch64 (64-bit) |
| Python | 3.11.9 (managed via `pyenv`, pinned by `.python-version` in this folder) |
| pip | 24.0+ (run `pip install --upgrade pip` if older) |
| opencv-python | 5.0.0 |
| mediapipe | 0.10.9 |
| numpy | 2.4.6 |
| RPi.GPIO | 0.7.1 |

Compatibility note: `mediapipe==0.10.9` is confirmed to have a prebuilt wheel for
`cp311` + `manylinux_aarch64`, which is why Python 3.11 is the target version here
(pip will fall back to building from source, or fail, on other Python versions —
stick to 3.11.x unless you've separately confirmed a mediapipe wheel exists for it).

### Setup from a clean Pi

```bash
# 1. Confirm/install Python 3.11.9 via pyenv (skip if already set up)
pyenv install 3.11.9
pyenv local 3.11.9      # writes .python-version in this folder

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install dependencies
pip install numpy opencv-python mediapipe==0.10.9 RPi.GPIO

# 4. Download the hand landmark model (test12.py needs this file present
#    in the same folder — already included here as hand_landmarker.task)
#    Source: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

Verify the install:

```bash
python3 -c "import cv2, mediapipe, numpy, RPi.GPIO; print('all good')"
```

### Using the project venv (recommended, isolates deps from the global pyenv env)

A venv already exists at `Documents/venv`, built from pyenv's Python 3.11.9,
with the same packages installed (opencv-python 5.0.0, mediapipe 0.10.9,
numpy 2.4.6, RPi.GPIO). Activate it before running any script:

```bash
source /home/prayut/Documents/venv/bin/activate
# prompt should now show (venv) at the start of the line
python3 test12.py
```

When you're done:

```bash
deactivate
```

To rebuild it from scratch (e.g. it gets corrupted or deps drift):

```bash
cd /home/prayut/Documents
rm -rf venv                              # only if you're sure you want to wipe it
python3 -m venv venv                     # uses whatever `python3` currently resolves to — make sure pyenv has 3.11.9 active first
source venv/bin/activate
pip install --upgrade pip
pip install numpy opencv-python mediapipe==0.10.9 RPi.GPIO
```

Note: there's also an `env/` folder in this directory — that one was built against
the **system** Python 3.13.5 with `--system-site-packages` (a different, older
setup, not the pyenv 3.11.9 one this README targets). Don't mix the two;
use `venv/` for anything in this project.

## SSH / remote access

Connect from your computer:

```bash
ssh <pi-username>@<pi-ip-or-hostname>.local
```

If running headless (no monitor attached) and you need a GUI window (`cv.imshow`,
used in `test12.py`), the desktop session still runs virtually on `:0` even
without a monitor plugged in. Two ways to see it:

1. **Raspberry Pi Connect** (already set up on this Pi) — go to
   https://connect.raspberrypi.com in a browser, sign in, select this Pi,
   click "Screen sharing". Then run scripts with `DISPLAY=:0` prefixed:
   ```bash
   DISPLAY=:0 python3 test12.py
   ```
2. **VNC** — `wayvnc` is installed (this Pi runs the `labwc` Wayland compositor,
   so `wayvnc`, not RealVNC's X11 server, is the correct one).

Without a display at all, GUI calls like `cv.imshow()` will throw
`qt.qpa.xcb: could not connect to display` — either attach a display (real or
virtual, per above) or strip the `imshow` calls for headless operation.

## Common errors seen & fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'cv2'` / `'mediapipe'` | Active Python env had no packages installed at all | `pip install opencv-python mediapipe==0.10.9 numpy` into the active pyenv env |
| `qt.qpa.xcb: could not connect to display` | No `DISPLAY` env var set (e.g. running from an SSH/VS Code Remote terminal) | Prefix the command with `DISPLAY=:0`, and ensure a screen-share (Pi Connect) or VNC session is open so the window is actually visible |
| `Could not open camera device at index 0` / `getStreamChannelGroup Camera index out of range` | No `/dev/video0` present — either no camera plugged in, or another process already has it open | Check `lsusb` / `ls /dev/video*`; if a previous script instance is still running, `fuser /dev/video0` shows the PID holding it, `kill <pid>` frees it |
| `No cameras available!` (`rpicam-hello --list-cameras`) | No CSI ribbon camera and no USB webcam detected | Plug in a USB webcam (`lsusb` should show a "Web Camera" / UVC device) or reseat the CSI ribbon cable |
| `ImportError: No module named 'RPi'` | `RPi.GPIO` not installed in the active env | `pip install RPi.GPIO` |
| Servo has no holding torque after script exits | `servo.stop()` + `GPIO.cleanup()` stops PWM pulses; the horn drifts passively with no signal driving it | Expected behavior for GPIO.PWM servos — remove the final `stop()`/`cleanup()` if you want it to hold the last position after the script ends |
| `TypeError: unsupported operand type(s) for &: 'NoneType' and 'int'` during interpreter shutdown, after "Done, GPIO cleaned up" | Harmless double-cleanup: the `PWM` object's `__del__` tries to stop the channel again after `GPIO.cleanup()` already tore it down | Cosmetic only, safe to ignore |
| Ambiguous / flickering color match in `test12.py` | Two entries in `COLOR_TARGETS` are closer to each other (Euclidean RGB distance) than `MATCH_THRESHOLD`, so noisy lighting can flip the match between them | Either widen the gap between the two target RGB values, or lower `MATCH_THRESHOLD`; best fix is calibrating `COLOR_TARGETS` from the real camera (see `calibrate_colors.py`) instead of guessing RGB values |
| `Aborted` / `Fatal Python error: Aborted (core dumped)` right after a Qt plugin error | Same root cause as the `qt.qpa.xcb` display error above — Qt fails to initialize a platform plugin and the whole process aborts instead of raising a normal Python exception | Fix the display issue first (`DISPLAY=:0` + an active screen-share/VNC session); this isn't a separate bug, just how Qt fails when it truly can't find a screen |
| `cv2` underlined red / "Import \"cv2\" could not be resolved" in VS Code, even though `python3 -c "import cv2"` works fine in the terminal | VS Code/Pylance is pointed at a different Python interpreter than the one you installed packages into (e.g. system Python, or a different venv than `Documents/venv`) | In VS Code: Ctrl+Shift+P → "Python: Select Interpreter" → pick the interpreter matching `Documents/venv/bin/python3` (or wherever you actually installed the packages) |
| `fatal error: Python.h: No such file or directory` during `pip install` | pip couldn't find a prebuilt wheel for your exact Python version/architecture and fell back to compiling the package from source, which needs Python's C headers | Usually means your Python version doesn't match an available wheel — double check you're on Python 3.11.x (matches the confirmed `mediapipe==0.10.9` aarch64 wheel); if you really need to build from source, install headers first: `sudo apt install python3-dev` |
| `error: externally-managed-environment` when running `pip install <name>` directly on the system Python (not inside a venv/pyenv env) | Debian 12+/trixie's system Python blocks `pip install` outside a venv by default (PEP 668), to stop you from breaking apt-managed packages | **Prefer fixing the root cause, not this flag**: activate `Documents/venv` (or `pyenv local 3.11.9`) first, then `pip install` normally — it won't hit this error inside an isolated env. Only if you deliberately want to install into the system Python anyway, add `--break-system-packages` (e.g. `pip install <name> --break-system-packages`) — this disables the safety check, so double-check you're not about to clobber a package apt/other tools depend on |

All the try/except patterns across these scripts follow the same shape:

```python
try:
    ...main loop...
except KeyboardInterrupt:
    print("\nProgram interrupted/stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    GPIO.cleanup()   # always release GPIO pins, even on crash/Ctrl+C
```

`GPIO.cleanup()` in `finally` is the important part — it releases pin state so
the next script run doesn't hit "channel already in use" warnings.

---

## File-by-file summary

### `test1.py`
Broken import stub — `from gpiopzero import LED` (typo: should be `gpiozero`, and
the rest of the file is empty). Not runnable as-is; earliest scratch file in the series.

### `test2.py`
Simplest possible GPIO test: blinks a single LED wired to **board pin 8** on a
1-second on/off loop forever. Uses `GPIO.setmode(GPIO.BOARD)` (physical pin
numbering, not BCM) — the odd one out since every later script switches to BCM.
No cleanup, no exit handling — has to be killed with Ctrl+C, which won't
clean up the pin state.

### `test3.py`
First button-to-LED script. One LED (BCM pin 13) mirrors the state of one button
(BCM pin 12) wired with a **pull-down** resistor: LED is on only while the button
is held (`GPIO.PUD_DOWN`, active-high). Introduces the standard
`try/except KeyboardInterrupt/except Exception/finally: GPIO.cleanup()` pattern
used throughout the rest of the series.

### `test4.py`
Two-button, one-LED logic test (BCM: LED=12, buttons=23/24, both **pull-up**,
active-low). Button 1 turns the LED on; while it's held, button 2 can turn it
back off. Mostly a logic-branching exercise, not a real end-product circuit.

### `test5.py`
5 LEDs (BCM 12/25/18/17/4) in a row plus two buttons: **Step** button advances
a single lit LED through the row one press at a time (wraps around after the
5th), **Auto** button starts a self-cycling chase sequence through all 5.
Pressing both buttons at once resets to all-off. This is a Knight Rider /
LED chaser build.

### `test6.py`
Same 5-LED-chaser concept as `test5.py`, rewritten with `elif` branching
(mutually exclusive button checks) instead of independent `if`s, and a manual
`count` index instead of the wraparound modulo trick. Functionally a cleaner
rewrite/variant of `test5.py`.

### `test7.py`
Introduces the **HC-SR04 ultrasonic distance sensor** (TRIG=BCM26, ECHO=BCM5).
Also sets up 8 LED pins but never actually uses them in the loop — this file
just continuously measures and prints distance in cm, with pulse-timeout
detection if the echo pulse never returns.

### `test8.py`
Builds directly on `test7.py`: uses the same ultrasonic sensor to drive 8 LEDs
(BCM 12/25/18/17/4/22/23/24) through **distance-banded light patterns** —
blink-all for near range, "outside-in" chase, alternating blink, and sequential
turn-off, each triggered by which 50cm-ish band the measured distance falls
into. This is the most complete LED+sensor "installation piece" before the
project moves on to motors/servos.

### `test9.py`
First DC motor driver test (H-bridge style, IN1=BCM18, IN2=BCM12, ENA=BCM13 for
PWM speed) with two buttons for forward/backward. **Has known bugs left in**:
`motor_forward()`/`motor_backward()`/`motor_stop()` only ever toggle `IN1`
(never touch `IN2`), so direction control doesn't actually work as intended,
and the `finally` block references `pwm_forward`/`pwm_backward` objects that
were never created (only `pwm_motor` exists) — this file will crash on exit.
Superseded by `test10.py`.

### `test10.py`
Fixed version of `test9.py`: motor functions now correctly drive both `IN1`
and `IN2` for direction, PWM speed is applied via `pwm_motor.ChangeDutyCycle()`,
and cleanup correctly stops `pwm_motor`. Forward/backward driven at a fixed
40% speed for 3 seconds per button press.

### `test11.py`
Same motor driver wiring as `test10.py`, but control moves from GPIO buttons to
**interactive terminal input** — type `F`/`B`/`S` to drive forward/backward/stop,
and `+`/`-` to adjust speed in 10% steps (clamped 0–100%), with speed changes
applied live if the motor is currently running.

### `test12.py` — the main project
Hand-tracking + color-matching + servo-pointer:
1. Opens the webcam (`cv.VideoCapture(0)`) and MediaPipe's **HandLandmarker**
   task (needs `hand_landmarker.task` in the same folder).
2. Each frame (every 3rd frame, via `SKIP_FACTOR`), detects hand landmarks and
   reads the **index fingertip** position (landmark 8).
3. Samples a small pixel patch near the fingertip and averages its RGB color.
4. Matches that color against `COLOR_TARGETS` — a list of
   `(name, (r,g,b), servo_angle)` tuples — by nearest Euclidean RGB distance,
   accepting the match only if it's within `MATCH_THRESHOLD` (currently 60).
5. Moves a servo on **BCM pin 18** to the angle associated with the matched
   color, via `GPIO.PWM` (`duty = 2 + angle/18`, standard SG90-range mapping).
6. Shows two windows: the camera feed with a marker at the sample point, and
   a solid-color swatch of what was sampled (`cv.imshow`, needs a display —
   see SSH/remote access section above).
7. Falls back to "simulation mode" (prints instead of moving anything) if
   `RPi.GPIO` isn't installed, so the vision logic can still be tested off-Pi.

`COLOR_TARGETS` currently encodes an 8-color paper dial (green, coral, pink,
sky_blue, orange, black, steel_blue, yellow) mapped across a 180° servo sweep,
angles inverted from the original assignment so the sweep direction matches
the physical mounting, with steel_blue/sky_blue nudged apart in RGB space to
reduce misdetection between the two blues.

### `calibrate_colors.py`
Standalone helper for tuning `COLOR_TARGETS` — no GUI/display required, works
purely over SSH. Prompts you, one color at a time, to hold that paper square
centered in front of the camera and press Enter; samples a 60×60px patch from
the center of the live frame and averages it. After all 8 colors, prints a
ready-to-paste `COLOR_TARGETS` block using the webcam's real observed RGB
values (with the same angle assignments as `test12.py`) instead of guessed
values — meant to replace the hand-picked RGB constants with ones calibrated
to the actual camera and lighting conditions.
