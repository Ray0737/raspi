import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
LED_PIN1 = 12
LED_PIN2 = 25
LED_PIN3 = 18
LED_PIN4 = 17
LED_PIN5 = 4
LED_PIN6 = 18
LED_PIN7 = 17
LED_PIN8 = 4
TRIG_PIN = 26
ECHO_PIN = 5

GPIO.setup(LED_PIN1, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.OUT)
GPIO.setup(LED_PIN3, GPIO.OUT)
GPIO.setup(LED_PIN4, GPIO.OUT)
GPIO.setup(LED_PIN5, GPIO.OUT)
GPIO.setup(LED_PIN6, GPIO.OUT)
GPIO.setup(LED_PIN7, GPIO.OUT)
GPIO.setup(LED_PIN8, GPIO.OUT)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

GPIO.output(TRIG_PIN, False)
time.sleep(0.5)

try:
    while True:
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001) # 10 microsecond pulse
        GPIO.output(TRIG_PIN, False)

        pulse_start = time.time()
        pulse_end = time.time()
        
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        if pulse_duration <= 0.00001:
            print("Sensor Error: Pulse timed out. Check hardware/wiring.")
        else:
            speed_of_sound_cm = (331 + 0.6 * 25)*100 
            distance = (pulse_duration * speed_of_sound_cm) // 2
            print(f"Distance: {distance} cm")
    
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram stopped.")
finally:
    GPIO.cleanup()


