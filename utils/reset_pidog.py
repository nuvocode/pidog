#!/usr/bin/env python3
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_pidog():
    try:
        # Kill any running python processes
        logger.info("Killing python processes...")
        os.system("sudo pkill -9 python3")
        time.sleep(2)

        # Reset the GPIO pins
        logger.info("Resetting GPIO...")
        os.system("sudo gpio -v reset")
        time.sleep(1)

        # Optionally reload required kernel modules
        logger.info("Reloading I2C module...")
        os.system("sudo rmmod i2c_bcm2835")
        time.sleep(1)
        os.system("sudo modprobe i2c_bcm2835")
        time.sleep(1)

        logger.info("Reset complete!")
        
    except Exception as e:
        logger.error(f"Error during reset: {e}")

if __name__ == "__main__":
    reset_pidog()