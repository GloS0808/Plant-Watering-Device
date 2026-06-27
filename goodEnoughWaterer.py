import time
import board
import pwmio
import adafruit_bh1750
from adafruit_seesaw.seesaw import Seesaw
import digitalio

# Initialize D13 (actually D12) pin as a digital input
d13 = digitalio.DigitalInOut(board.D12)
d13.direction = digitalio.Direction.INPUT

# Light sensor
i2c = board.I2C()
sensor = adafruit_bh1750.BH1750(i2c)

# Moisture/temp sensor
i2c_bus = board.I2C()
ss = Seesaw(i2c_bus, addr=0x36)

# Piezo on A1
piezo = pwmio.PWMOut(board.A1, duty_cycle=0, frequency=440, variable_frequency=True)

# --- Timing constants ---
TWO_DAYS = 2 * 24 * 60 * 60      # 172800 seconds
PULSE_DURATION = 1                # run piezo for 1 second
MOISTURE_THRESHOLD = 600
CHECK_INTERVAL = 600              # 10 min between moisture checks when dry-not-watering
D13_WAIT = 86400                  # 24 hours

counter = 0
last_pulse_time = time.monotonic()  # tracks the 2-day timer

while True:
    now = time.monotonic()

    # --- 1-second pulse every 2 days, independent of everything else ---
    if now - last_pulse_time >= TWO_DAYS:
        print("Running scheduled 1-second pulse")
        piezo.duty_cycle = 65535
        time.sleep(PULSE_DURATION)
        piezo.duty_cycle = 0
        last_pulse_time = now

    # --- D13 check ---
    if d13.value:
        print("D13 is true. Waiting 24 hours...")
        piezo.duty_cycle = 0
        time.sleep(D13_WAIT)
        continue  # skip rest of loop, re-check from top
    else:
        print("D13 is false. Continuing to check...")
        time.sleep(1)

    # --- Read sensors fresh each loop ---
    water = ss.moisture_read()
    temp = ss.get_temp()
    fahrenheit = (temp * 9 / 5) + 32
    lux = sensor.lux

    if water < MOISTURE_THRESHOLD:
        counter += 1
        piezo.duty_cycle = 65535
        print(f"#{counter} Now Watering... Moisture:{water} --- °F:{fahrenheit:.1f}")
        time.sleep(1)
        piezo.duty_cycle = 0
    else:
        piezo.duty_cycle = 0
        print(f"#{counter} °F:{fahrenheit:.1f} Moisture:{water} LUX:{lux}")
        time.sleep(CHECK_INTERVAL)