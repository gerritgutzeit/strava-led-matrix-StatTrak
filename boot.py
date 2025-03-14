# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)

import webrepl
import gc
import machine
import time

# Free up memory
gc.collect()

# Small delay to allow system to stabilize
time.sleep(1)

try:
    import d1_mini_gear_check
    d1_mini_gear_check.main()
except Exception as e:
    print("Error in main program:", e)
    # If there's an error, wait 10 seconds and reset
    time.sleep(10)
    machine.reset()

# Start WebREPL
webrepl.start() 