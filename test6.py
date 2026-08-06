import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Pin Definitions
LED_PIN1 = 12
LED_PIN2 = 25
LED_PIN3 = 18
LED_PIN4 = 17
LED_PIN5 = 4

LED_PIN00 = 23
LED_PIN01 = 24

# Setup Pins
leds = [LED_PIN1, LED_PIN2, LED_PIN3, LED_PIN4, LED_PIN5]
for pin in leds:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

GPIO.setup(LED_PIN00, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN01, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# FIX 1: Initialize the tracking variable
count = 0 

try:
    while True:
        button_state1 = GPIO.input(LED_PIN00)
        button_state2 = GPIO.input(LED_PIN01)
        
        # FIX 3: Both buttons pressed check MUST go first!
        if button_state1 == GPIO.LOW and button_state2 == GPIO.LOW:
            print("Both pressed: Turning all LEDs OFF")
            for pin in leds:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5) # Prevent registering multiple rapid presses
            
        # Button 1 sequence (Manual Step Loop)
        elif button_state1 == GPIO.LOW:
            # Turn off all LEDs first so only one lights up at a time
            for pin in leds:
                GPIO.output(pin, GPIO.LOW)
                
            print(f"Button 1 pressed: Index {count}")
            GPIO.output(leds[count], GPIO.HIGH)
            
            count += 1
            # FIX 2: Reset if it reaches index 5 (valid indexes are 0 to 4)
            if count >= 5: 
                count = 0
                
            time.sleep(0.3) # Short bounce delay for manual clicking
            
        # Button 2 sequence (Auto Sequence)
        elif button_state2 == GPIO.LOW:
            for pin in leds:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5)
            print("Button 2 pressed: Starting Auto Sequence")
            # Cleaner way to do your auto sequence using a loop
            for pin in leds:
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(pin, GPIO.LOW)

        time.sleep(0.05) # Keep CPU load minimal

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    GPIO.cleanup()
    print("GPIO pins have been safely cleaned up!")