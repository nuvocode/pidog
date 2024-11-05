#!/usr/bin/env python3
import logging
from pidog import Pidog
from time import sleep
import sys
from datetime import datetime
from preset_actions import hand_shake, high_five  # Import the functions directly

def setup_logging():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'pidog_log_{timestamp}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def greeting_sequence(my_dog, volume=100):
    try:
        # Initial sit
        logger.info("Starting greeting sequence")
        my_dog.do_action('sit', speed=80)
        my_dog.wait_all_done()

        # Play sound and flash RGB
        logger.info("Playing sound and setting RGB")
        my_dog.rgb_strip.set_mode('breath', color='green', bps=1.0)
        my_dog.speak('pasha', volume)
        sleep(1)

        # Handshake
        logger.info("Performing handshake")
        my_dog.rgb_strip.set_mode('breath', color='blue', bps=1.0)
        hand_shake(my_dog)  # Call the function directly
        sleep(1)

        # High five
        logger.info("Performing high five")
        my_dog.rgb_strip.set_mode('breath', color='red', bps=1.0)
        high_five(my_dog)  # Call the function directly
        sleep(1)

        # Return to normal position
        logger.info("Returning to sit position")
        my_dog.rgb_strip.set_mode('breath', color='yellow', bps=0.5)
        my_dog.do_action('sit', speed=80)
        my_dog.wait_all_done()

    except Exception as e:
        logger.error(f"Error during greeting sequence: {e}")

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog greeting program")
        my_dog = Pidog(head_init_angles=[0, 0, 0])
        logger.info("PiDog initialized successfully")
        sleep(1)
        
        while True:
            greeting_sequence(my_dog)
            sleep(3)  # Wait between sequences

    except KeyboardInterrupt:
        logger.info("Program stopped by user")
        if my_dog:
            my_dog.rgb_strip.set_mode('off', None, 0, 0)
            
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
    finally:
        if my_dog is not None:
            try:
                logger.info("Closing PiDog connection")
                my_dog.close()
            except Exception as e:
                logger.error(f"Error while closing PiDog: {e}")

if __name__ == "__main__":
    main()