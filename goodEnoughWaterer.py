import time
import board
import pwmio
import adafruit_bh1750
from adafruit_seesaw.seesaw import Seesaw
import digitalio

# Initialize D13 pin as a digital input
d13 = digitalio.DigitalInOut(board.D12)
d13.direction = digitalio.Direction.INPUT
#  solar sensor moisture sensors
i2c = board.I2C()
sensor = adafruit_bh1750.BH1750(i2c)

#  moisture sensors
i2c_bus = board.I2C()
ss = Seesaw(i2c_bus, addr=0x36)
#   Convert to Fahrenheit
temp = ss.get_temp()
fahrenheit = (temp * 9 / 5) + 32

#  to contorl A1 pin on feather
piezo = pwmio.PWMOut(board.A1, duty_cycle=0, frequency=440, variable_frequency=True)

#  begin counter of times watered
counter = 0

while True:
    
    # If D13 is true, wait for 24 hours before checking again
    if d13.value:
        print("D13 is true. Waiting for 24 hours...")
        piezo.duty_cycle = 0  # Off
        time.sleep(86400) # Wait for 24 hours (24 * 60 * 60 seconds)
    else:
        print("D13 is false. Continuing to check...")
        time.sleep(1) # Wait for 1 second before checking again
    if counter % 5 == 0:
        piezo.duty_cycle = 0  # Off
        print("done watering")
        time.sleep(8)
    water = ss.moisture_read()  # read moisture
    temp = ss.get_temp()  # read temperature
    lux = sensor.lux
    if water < 600:  # base moisture reading is ~320 if lower than 400 water
        counter += 1
        piezo.duty_cycle = 65535  # On 100%
        print(
            "#"
            + str(counter)
            + " "
            + "Now Watering... ML:"
            + str(water)
            + "---"
            + "°F:"
            + str(fahrenheit)
        )
        time.sleep(1)
    else:
        piezo.duty_cycle = 0  # Off
        print(
            "#"
            + str(counter)
            + " "
            + "°F:"
            + str(fahrenheit)
            + " "
            + "ML:"
            + str(water)
            + " "
            + "LUX:"
            + str(lux)
        )
        time.sleep(600)
