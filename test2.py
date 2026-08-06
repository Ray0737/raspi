import RPi.GPIO as GPIO
import time
 # use BCM pin
GPIO.setmode(GPIO.BOARD) # use board pin numbering (use this one for board)
GPIO.setup(8, GPIO.OUT)


while True:
	GPIO.output(8,1)
	time.sleep(1)
	GPIO.output(8,0)
	time.sleep(1)

