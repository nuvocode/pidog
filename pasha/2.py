#!/usr/bin/env python3
import logging
from pidog import Pidog
from time import sleep
import sys
from datetime import datetime

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

def custom_howl(my_dog, volume=100):
    try:
        # Initial sit and head position
        logger.info("Starting howl sequence")
        my_dog.do_action('sit', speed=80)
        my_dog.head_move([[0, 0, -30]], speed=95)
        my_dog.wait_all_done()

        # Set RGB and prepare to howl
        logger.info("Setting RGB and preparing to howl")
        my_dog.rgb_strip.set_mode('speak', color='cyan', bps=0.6)
        my_dog.do_action('half_sit', speed=80)
        my_dog.head_move([[0, 0, -60]], speed=80)
        my_dog.wait_all_done()

        # Play custom sound and move
        logger.info("Playing custom sound")
        my_dog.speak('pasha', volume)  # Using your custom sound
        my_dog.do_action('sit', speed=60)
        my_dog.head_move([[0, 0, 10]], speed=70)
        my_dog.wait_all_done()

        my_dog.do_action('sit', speed=60)
        my_dog.head_move([[0, 0, 10]], speed=80)
        my_dog.wait_all_done()

        # Return to normal position
        sleep(2.34)  # Adjust this based on your sound length
        my_dog.do_action('sit', speed=80)
        my_dog.head_move([[0, 0, -40]], speed=80)
        my_dog.wait_all_done()

    except Exception as e:
        logger.error(f"Error during howl sequence: {e}")

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog custom howl program")
        my_dog = Pidog(head_init_angles=[0, 0, 0])
        logger.info("PiDog initialized successfully")
        sleep(1)
        
        while True:
            custom_howl(my_dog)
            sleep(2)  # Wait between howls

    except KeyboardInterrupt:
        logger.info("Program stopped by user")
        if my_dog:
            safe_rgb(my_dog, 'off', None, 0, 0)
            
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