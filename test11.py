import RPi.GPIO as GPIO
from time import sleep

# 1. Tell the Pi we are using BCM (GPIO labels)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 2. Define the pins based on your T-Cobbler labels
IN1 = 18   # Connects to Orange wire
IN2 = 12   # Connects to Red wire
ENA = 13   # Speed Control Pin (Enable A)

# 3. Configure the pins (Removed button pin configs as they are no longer needed)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# 4. Initialize Software PWM on ENA pin at 1000Hz frequency
pwm_motor = GPIO.PWM(ENA, 1000)
pwm_motor.start(0) 

# Track the engine states
current_speed = 40  # Start at a default baseline speed of 40%
current_direction = "STOP" # Options: "F", "B", "STOP"

# 5. Define Motor Control Functions
def motor_forward(speed):
    global current_direction
    current_direction = "F"
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)  
    pwm_motor.ChangeDutyCycle(speed)

def motor_backward(speed):
    global current_direction
    current_direction = "B"
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH) 
    pwm_motor.ChangeDutyCycle(speed)

def motor_stop():
    global current_direction
    current_direction = "STOP"
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm_motor.ChangeDutyCycle(0)

# 6. Main Terminal Input Loop
try:
    print("--- Terminal Motor Controller Active ---")
    print("Commands:")
    print("  F : Drive Forward")
    print("  B : Drive Backward")
    print("  S : Stop Motor")
    print("  + : Increase Speed by 10%")
    print("  - : Decrease Speed by 10%")
    print("-----------------------------------------")
    
    while True:
        print(f"\n[Status] Direction: {current_direction} | Speed: {current_speed}%")
        # Prompt user for terminal input character
        user_input = input("Enter command (+, -, F, B, S): ").strip()

        # Handle Speed Increases
        if user_input == "+":
            current_speed += 10
            if current_speed > 100: 
                current_speed = 100  # Cap speed maximum at 100%
                print("Already at maximum speed!")
            
            # Instantly apply the speed update to the running motor
            if current_direction == "F":
                motor_forward(current_speed)
            elif current_direction == "B":
                motor_backward(current_speed)

        # Handle Speed Decreases
        elif user_input == "-":
            current_speed -= 10
            if current_speed < 0:
                current_speed = 0    # Floor speed minimum at 0%
                print("Already stopped!")
            
            # Instantly apply the speed update to the running motor
            if current_direction == "F":
                motor_forward(current_speed)
            elif current_direction == "B":
                motor_backward(current_speed)

        # Handle Directional Commands
        elif user_input.upper() == "F":
            print("Driving Forward...")
            motor_forward(current_speed)

        elif user_input.upper() == "B":
            print("Driving Backward...")
            motor_backward(current_speed)

        elif user_input.upper() == "S":
            print("Stopping Motor...")
            motor_stop()
            
        else:
            print("Invalid command. Please use +, -, F, B, or S.")

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    print("Cleaning up GPIO resources...")
    pwm_motor.stop() 
    GPIO.cleanup()
    print("Done!")