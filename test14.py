from rpi_lcd import LCD
from time import sleep

lcd = LCD()
try:
    while True:
        lcd.text("hello world",1)
        lcd.text("Raspberry Pi",2)
        sleep(3)
        lcd.clear()
        sleep(1)
except KeyboardInterrupt:
    lcd.clear()
