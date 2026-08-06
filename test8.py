import RPi.GPIO as GPIO
import time

# --- Setup GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Grouping your pins into an array for easier looping (Left to Right)
# NOTE: Please verify these match your unique 8 physical GPIO pins!
led_pins = [12, 25, 18, 17, 4, 22, 23, 24]  # Adjusted duplicates for safety

# Ultrasonic Sensor Pins
TRIG_PIN = 26
ECHO_PIN = 5

# Initialize Pins
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)

GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

GPIO.output(TRIG_PIN, False)
time.sleep(0.5)

# --- Helper Functions for LED Patterns ---

def all_off():
    for pin in led_pins:
        GPIO.output(pin, False)

def all_on():
    for pin in led_pins:
        GPIO.output(pin, True)

# 1. 5 cm - 20 cm (Blink all 5 times)
def pattern_blink_all():
    for _ in range(5):
        all_on()
        time.sleep(0.15)
        all_off()
        time.sleep(0.15)

# 2. 21 cm - 50 cm (Run outside to inside)
def pattern_outside_in():
    all_off()
    for i in range(4):  # 4 steps to meet in the middle
        GPIO.output(led_pins[i], True)       # From left
        GPIO.output(led_pins[7 - i], True)   # From right
        time.sleep(0.2)
    time.sleep(0.3)
    all_off()

# 3. 51 cm - 100 cm (Alternate blinking)
def pattern_alternate():
    for _ in range(3):
        # Even indices ON, Odd OFF
        for idx, pin in enumerate(led_pins):
            GPIO.output(pin, idx % 2 == 0)
        time.sleep(0.3)
        # Odd indices ON, Even OFF
        for idx, pin in enumerate(led_pins):
            GPIO.output(pin, idx % 2 != 0)
        time.sleep(0.3)
    all_off()

# 4. 101 cm - 150 cm (All on, then turn off one by one from left to right)
def pattern_turn_off_sequence():
    all_on()
    time.sleep(0.3)
    for pin in led_pins:
        GPIO.output(pin, False)
        time.sleep(0.15)

# --- Main Logic Loop ---
print("Distance LED Controller Active. Press Ctrl+C to stop.")

try:
    while True:
        # Trigger the pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001) 
        GPIO.output(TRIG_PIN, False)

        pulse_start = time.time()
        pulse_end = time.time()
        
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        
        if pulse_duration <= 0.00001:
            print("Sensor Error: Pulse timed out.")
            all_off()
        else:
            speed_of_sound_cm = (331 + 0.6 * 25) * 100 
            distance = (pulse_duration * speed_of_sound_cm) // 2
            print(f"Distance: {distance} cm")

            # --- Check distance ranges according to documentation ---
            
            # 5 cm - 20 cm
            if 5 <= distance <= 20:
                print("Action: Blinking 5 times")
                pattern_blink_all()
                
            # 21 cm - 50 cm
            elif 21 <= distance <= 50:
                print("Action: Running Outside-In")
                pattern_outside_in()
                
            # 51 cm - 100 cm
            elif 51 <= distance <= 100:
                print("Action: Alternate Blinking")
                pattern_alternate()
                
            # 101 cm - 150 cm
            elif 101 <= distance <= 150:
                print("Action: Sequential Turn Off")
                pattern_turn_off_sequence()
                
            # More than 150 cm
            elif distance > 150:
                print("Action: All Off")
                all_off()
    
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram stopped.")
finally:
    GPIO.cleanup()