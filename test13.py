import cv2 as cv
from ultralytics import YOLO

MODEL_PATH = "best.pt"
CONF_THRESHOLD = 0.5


def main():
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"Model Load Error: {e}")
        return

    try:
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera device at index 0.")

        cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    except Exception as e:
        print(f"Camera Initialization Error: {e}")
        return

    print("Starting video feed. Press 'q' or Ctrl+C to quit.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Warning: Failed to grab frame from camera.")
                break

            try:
                results = model(frame, conf=CONF_THRESHOLD, verbose=False)
                annotated = results[0].plot()

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    name = model.names[cls_id]
                    conf = float(box.conf[0])
                    print(f"Detected {name} ({conf:.2f})")

            except Exception as frame_err:
                print(f"Error processing frame: {frame_err}")
                annotated = frame

            cv.imshow('YOLO Detection', annotated)

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


if __name__ == "__main__":
    main()
