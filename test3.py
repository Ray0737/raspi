import RPi.GPIO as GPIO
import time
# if not press value = 0 | if press value = 1 
GPIO.setmode(GPIO.BCM)
LED_PIN1 = 13
LED_PIN2 = 12
GPIO.setup(LED_PIN1, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
try:
    while True:
        button_state = GPIO.input(LED_PIN2)
        if button_state == GPIO.HIGH: #if its
            GPIO.output(LED_PIN1, GPIO.HIGH)
            time.sleep(1)
        else:
            GPIO.output(LED_PIN1, GPIO.LOW)
            time.sleep(1)              
except KeyboardInterrupt:
    print("\nProgram interrupted by user.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    GPIO.cleanup()
    print("GPIO pins have been safely cleaned up!")