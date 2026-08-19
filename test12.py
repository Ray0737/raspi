import sys
import time
import cv2 as cv
import mediapipe as mp
import numpy as np

# Try importing Raspberry Pi GPIO
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    print("Warning: RPi.GPIO not found. Running in simulation mode (no servo).")

# Setup MediaPipe Tasks imports (v1.0.0+)
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

OFFSET = (15, 15)  # Offset from index tip
MATCH_THRESHOLD = 60
SERVO_PIN = 18
MODEL_PATH = "hand_landmarker.task"

COLOR_TARGETS = [
    ("yellow",     (240, 210, 60),   22.5),
    ("steel_blue", (74, 127, 190),   45.0),
    ("black",      (40, 40, 40),     67.5),
    ("orange",     (230, 150, 70),   90.0),
    ("sky_blue",   (21, 129, 210),  112.5),
    ("pink",       (220, 100, 160), 135.0),
    ("coral",      (230, 110, 90),  157.5),
    ("green",      (90, 170, 80),   180.0),
]

# Servo initialization
servo = None
if HAS_GPIO:
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # Silences the 'channel already in use' warning
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        servo = GPIO.PWM(SERVO_PIN, 50)
        servo.start(0)
    except Exception as e:
        print(f"GPIO Initialization Error: {e}")

def set_servo_angle(angle):
    if servo is not None:
        try:
            duty = 2 + (angle / 18.0)
            servo.ChangeDutyCycle(duty)
        except Exception as e:
            print(f"Error moving servo to {angle}°: {e}")

def match_color(r, g, b):
    best_name, best_angle, best_dist = None, None, float("inf")
    for name, (cr, cg, cb), angle in COLOR_TARGETS:
        dist = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
        if dist < best_dist:
            best_name, best_angle, best_dist = name, angle, dist
    if best_dist <= MATCH_THRESHOLD:
        return best_name, best_angle
    return None, None

def main():
    try:
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera device at index 0.")
        
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    except Exception as e:
        print(f"Camera Initialization Error: {e}")
        return

    # Configure HandLandmarker Options
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    frame_count = 0
    SKIP_FACTOR = 2
    last_results = None
    last_color = None
    start_time = time.time()

    print("Starting video feed. Press 'q' or Ctrl+C to quit.")

    try:
        with HandLandmarker.create_from_options(options) as landmarker:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Warning: Failed to grab frame from camera.")
                    break

                h, w, c = frame.shape
                frame = cv.flip(frame, 1)

                try:
                    if frame_count % (SKIP_FACTOR + 1) == 0:
                        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                        
                        frame_timestamp_ms = int((time.time() - start_time) * 1000)
                        last_results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

                    if last_results and last_results.hand_landmarks:
                        for hand_landmarks in last_results.hand_landmarks:
                            # Landmark 8 = Index Finger Tip
                            tip = hand_landmarks[8]
                            x8, y8 = int(tip.x * w), int(tip.y * h)

                            sx = min(max(x8 + OFFSET[0], 2), w - 3)
                            sy = min(max(y8 + OFFSET[1], 2), h - 3)

                            patch = frame[sy-2:sy+3, sx-2:sx+3]
                            b, g, r = np.mean(patch, axis=(0, 1)).astype(int)

                            cv.circle(frame, (sx, sy), 5, (0, 255, 0), 2)
                            swatch = np.full((100, 100, 3), (b, g, r), dtype=np.uint8)
                            cv.imshow('Sampled Color', swatch)

                            name, angle = match_color(r, g, b)
                            if name is not None and name != last_color:
                                set_servo_angle(angle)
                                last_color = name
                                print(f"Pointing at {name}, servo -> {angle}°")

                except Exception as frame_err:
                    print(f"Error processing frame {frame_count}: {frame_err}")

                frame_count += 1
                cv.imshow('Optimized Hand Tracking', frame)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting on user request...")
                    break

    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"Unexpected Runtime Error: {e}")

    finally:
        print("Cleaning up resources...")
        try:
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            cv.destroyAllWindows()
        except Exception as e:
            print(f"Error releasing OpenCV resources: {e}")

        if HAS_GPIO:
            try:
                if servo is not None:
                    servo.stop()
                GPIO.cleanup()
                print("GPIO cleanup completed.")
            except Exception as e:
                print(f"Error during GPIO cleanup: {e}")

if __name__ == "__main__":
    main()
