import RPi.GPIO as GPIO
import time

# --- Pin Setup ---
GPIO.setmode(GPIO.BCM)

# 5 LEDs in linear order
LED_PINS = [12, 25, 18, 17, 4]
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Ensure all are off initially

# Buttons using internal pull-up resistors
BTN_STEP = 5
BTN_AUTO = 6
GPIO.setup(BTN_STEP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_AUTO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- State Variables ---
current_led_index = -1  # -1 means no LEDs are turned on yet
auto_mode = False

def turn_off_all_leds():
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.LOW)

def check_simultaneous():
    # Low signal means pressed because of PUD_UP
    if GPIO.input(BTN_STEP) == GPIO.LOW and GPIO.input(BTN_AUTO) == GPIO.LOW:
        turn_off_all_leds()
        global current_led_index, auto_mode
        current_led_index = -1
        auto_mode = False
        time.sleep(0.5)  # Debounce delay
        return True
    return False

try:
    
    while True:
        # 1. Check for simultaneous press first
        if check_simultaneous():
            continue

        # 2. Check Button 1: Step through LEDs one at a time
        if GPIO.input(BTN_STEP) == GPIO.LOW:
            auto_mode = False  # Cancel auto mode if stepping manually
            turn_off_all_leds()
            
            # Move to next LED (0 to 4). If it reaches 5 (6th press), resets to 0.
            current_led_index = (current_led_index + 1) % 5
            
            print(f"Button 1: Lighting up LED {current_led_index + 1}")
            GPIO.output(LED_PINS[current_led_index], GPIO.HIGH)
            
            time.sleep(0.3)  # Debounce button press

        # 3. Check Button 2: Activate Auto Cycle Mode
        if GPIO.input(BTN_AUTO) == GPIO.LOW:
            print("Button 2: Auto sequence activated.")
            auto_mode = True
            time.sleep(0.3)  # Debounce button press

        # 4. Handle Auto Mode Execution
        if auto_mode:
            for i in range(5):
                # Double-check inside the loop to see if user interrupted or pressed both
                if check_simultaneous() or GPIO.input(BTN_STEP) == GPIO.LOW:
                    auto_mode = False
                    break
                
                turn_off_all_leds()
                GPIO.output(LED_PINS[i], GPIO.HIGH)
                
                # Small intervals during sleep to stay responsive to interrupts
                for _ in range(10): 
                    if check_simultaneous() or GPIO.input(BTN_STEP) == GPIO.LOW:
                        break
                    time.sleep(0.05) # 0.05s * 10 = 0.5 seconds per LED

        time.sleep(0.01)  # Minimal delay to ease CPU usage

except KeyboardInterrupt:
    print("\nProgram stopped safely.")

finally:
    GPIO.cleanup()
    print("GPIO cleared.")