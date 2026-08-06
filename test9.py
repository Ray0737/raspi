import RPi.GPIO as GPIO
from time import sleep

# 1. Tell the Pi we are using BCM (GPIO labels), not physical board numbers
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 2. Define the pins based on your T-Cobbler labels
# Adjust these numbers to match the exact 'G' labels on your breadboard
IN1 = 18  # Connects to Orange wire
IN2 = 12  # Connects to Red wire (Changed from 28 to a valid BCM pin)
BTN_PIN1 = 19
BTN_PIN2 = 26
ENA = 13
# 3. Configure the pins as outputs
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(BTN_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# 4. Initialize Software PWM at 100Hz frequency
pwm_motor = GPIO.PWM(ENA,1000)
pwm_motor.start(0)
pwm_motor.ChangeDutyCycle(0)

# 5. Define Motor Control Functions
def motor_forward():
    GPIO.output(IN1,GPIO.HIGH)
    GPIO.output(IN1,GPIO.LOW)
def motor_backward():
    GPIO.output(IN1,GPIO.LOW)
    GPIO.output(IN1,GPIO.HIGH)
def motor_stop():
    GPIO.output(IN1,GPIO.HIGH)
    GPIO.output(IN1,GPIO.HIGH)

# 6. Main Execution Loop
try:
    print("Starting full motor test sequence...")
    
    while True:
        button_state1 = GPIO.input(BTN_PIN1)
        button_state2 = GPIO.input(BTN_PIN2)    
        if button_state1 == GPIO.LOW:
            print("F")
            motor_forward()
        elif button_state2 == GPIO.LOW:
            print("B")
            motor_backward()
        else:
            motor_stop()
     

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    # Always clean up when you exit to protect the pins
    print("Cleaning up GPIO resources...")
    pwm_forward.stop()
    pwm_backward.stop()
    GPIO.cleanup()
    print("Done!")