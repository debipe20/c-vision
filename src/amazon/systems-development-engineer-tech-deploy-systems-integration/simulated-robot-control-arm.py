"""
A robotic arm is controlled via a simulated PLC which receives digital inputs and sets outputs to control the robot's state. You are to:

Monitor a start button (DI1), a part sensor (DI2), and a stop button (DI3).

Simulate a simple sequence: if the system is ON, and a part is detected, move the robot (print action) and wait 3 seconds.

If the stop button is pressed anytime, halt the system.
"""


import time
import threading

# Simulated PLC Inputs (Digital Inputs)
PLC_INPUTS = {
    "DI1": False,  # Start button
    "DI2": False,  # Part present
    "DI3": False   # Stop button
}

# State flags
system_running = False

def simulate_inputs():
    """
    Simulates external inputs to the PLC.
    """
    time.sleep(1)
    PLC_INPUTS["DI1"] = True  # Start button pressed
    time.sleep(2)
    PLC_INPUTS["DI2"] = True  # Part detected
    time.sleep(1)
    PLC_INPUTS["DI2"] = False
    time.sleep(4)
    PLC_INPUTS["DI3"] = True  # Stop button pressed

def plc_control_loop():
    global system_running
    while True:
        if PLC_INPUTS["DI1"]:
            print("[PLC] Start signal received.")
            system_running = True
            PLC_INPUTS["DI1"] = False

        if system_running:
            if PLC_INPUTS["DI2"]:
                print("[Robot] Part detected. Grabbing part...")
                time.sleep(3)
                print("[Robot] Part placed.")
                PLC_INPUTS["DI2"] = False

            if PLC_INPUTS["DI3"]:
                print("[PLC] Stop signal received. Halting system.")
                system_running = False
                PLC_INPUTS["DI3"] = False
                break

        time.sleep(0.5)

if __name__ == "__main__":
    threading.Thread(target=simulate_inputs).start()
    plc_control_loop()
