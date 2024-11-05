#!/usr/bin/env python3
import logging
from pidog import Pidog
from time import sleep
import time
from preset_actions import pant
from preset_actions import body_twisting
import sys
from datetime import datetime

# Set up logging
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

def safe_action(dog, action_name, timeout=5, **kwargs):
    try:
        start_time = time.time()
        dog.do_action(action_name, **kwargs)
        while time.time() - start_time < timeout:
            sleep(0.1)
        return True
    except Exception as e:
        logger.error(f"Action {action_name} failed: {e}")
        return False

def safe_wait(dog, timeout=2):
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            sleep(0.1)
    except Exception as e:
        logger.error(f"Wait failed: {e}")

def wake_up(my_dog):
    try:
        # stretch
        logger.info("Starting wake up sequence - stretch")
        my_dog.rgb_strip.set_mode('listen', color='yellow', bps=0.6, brightness=0.8)
        safe_wait(my_dog, 1)

        safe_action(my_dog, 'stretch', speed=50)
        safe_wait(my_dog, 2)

        my_dog.head_move([[0, 0, 30]], immediately=True)
        safe_wait(my_dog, 1)

        logger.info("Performing body twisting")
        try:
            body_twisting(my_dog)
            safe_wait(my_dog, 2)
        except Exception as e:
            logger.error(f"Body twisting error: {e}")

        my_dog.head_move([[0, 0, -30]], immediately=True, speed=90)
        safe_wait(my_dog, 1)

        # sit and wag_tail
        logger.info("Starting sit and wag tail sequence")
        safe_action(my_dog, 'sit', speed=25)
        safe_wait(my_dog, 2)

        safe_action(my_dog, 'wag_tail', step_count=5, speed=100)
        my_dog.rgb_strip.set_mode('breath', color=[245, 10, 10], bps=2.5, brightness=0.8)
        safe_wait(my_dog, 1)

        try:
            pant(my_dog, pitch_comp=-30, volume=80)
        except Exception as e:
            logger.error(f"Panting error: {e}")
        safe_wait(my_dog, 1)

        # hold pattern with recovery
        logger.info("Entering hold pattern")
        while True:
            try:
                safe_action(my_dog, 'wag_tail', step_count=5, speed=30, timeout=3)
                my_dog.rgb_strip.set_mode('breath', 'pink', bps=0.5)
                safe_wait(my_dog, 2)
            except Exception as e:
                logger.error(f"Hold pattern error: {e}")
                safe_wait(my_dog, 1)

    except Exception as e:
        logger.error(f"Error during wake up sequence: {e}")
        raise

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog wake up program")
        my_dog = Pidog(head_init_angles=[0, 0, -30])
        logger.info("PiDog initialized successfully")
        sleep(1)
        wake_up(my_dog)

    except KeyboardInterrupt:
        logger.info("Program stopped by user")
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