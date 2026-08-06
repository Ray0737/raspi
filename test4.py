import RPi.GPIO as GPIO
import time
# if not press value = 0 | if press value = 1 

GPIO.setmode(GPIO.BCM)
LED_PIN1 = 12
LED_PIN2 = 23
LED_PIN3 = 24
GPIO.setup(LED_PIN1, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(LED_PIN1, GPIO.LOW)
try:
    while True: 
        button_state1 = GPIO.input(LED_PIN2)
        button_state2 = GPIO.input(LED_PIN3)    
        if button_state1 == GPIO.LOW:
            GPIO.output(LED_PIN1, GPIO.HIGH)
            time.sleep(1)
            # 3. REVERSED: Pressing Button 2 now turns the LED ON
            if button_state2 == GPIO.LOW:
                GPIO.output(LED_PIN1, GPIO.LOW)
                time.sleep(1)
except KeyboardInterrupt:
    print("\nProgram interrupted by user.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    GPIO.cleanup()
    print("GPIO pins have been safely cleaned up!")