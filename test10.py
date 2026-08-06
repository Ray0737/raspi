import RPi.GPIO as GPIO
from time import sleep

# 1. Tell the Pi we are using BCM (GPIO labels)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 2. Define the pins based on your T-Cobbler labels
IN1 = 18   # Connects to Orange wire
IN2 = 12   # Connects to Red wire
BTN_PIN1 = 19
BTN_PIN2 = 26
ENA = 13   # Speed Control Pin (Enable A)

# 3. Configure the pins
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(BTN_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 4. Initialize Software PWM on ENA pin at 1000Hz frequency
pwm_motor = GPIO.PWM(ENA, 1000)
pwm_motor.start(0) # Fixed the 'pwn' typo here

# 5. Define Motor Control Functions
def motor_forward(speed=40):
    # Set Direction: IN1 High, IN2 Low
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)  # Fixed: changed from IN1 to IN2
    # Set Speed
    pwm_motor.ChangeDutyCycle(speed)

def motor_backward(speed=40):
    # Set Direction: IN1 Low, IN2 High
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH) # Fixed: changed from IN1 to IN2
    # Set Speed
    pwm_motor.ChangeDutyCycle(speed)

def motor_stop():
    # Cut power completely by setting pins LOW and speed to 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm_motor.ChangeDutyCycle(0)

# 6. Main Execution Loop
try:
    print("Starting full motor test sequence...")
    
    while True:
        button_state1 = GPIO.input(BTN_PIN1)
        button_state2 = GPIO.input(BTN_PIN2) 
        
        if button_state1 == GPIO.LOW:
            print("F")
            motor_forward(40) # Drives forward at 40% speed
            sleep(3)

        elif button_state2 == GPIO.LOW:
            print("B")
            motor_backward(40) # Drives backward at 40% speed
            sleep(3)
            
        else:
            motor_stop()
            sleep(0.1) # Reduced from 1 to 0.1 for better responsiveness when idle

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    # Always clean up when you exit to protect the pins
    print("Cleaning up GPIO resources...")
    pwm_motor.stop() # Fixed: stopping the correct PWM object name
    GPIO.cleanup()
    print("Done!")