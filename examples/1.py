#!/usr/bin/env python3
import logging
from pidog import Pidog
from time import sleep
import time
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
        logger.info(f"Starting action: {action_name}")
        start_time = time.time()
        dog.do_action(action_name, **kwargs)
        while time.time() - start_time < timeout:
            sleep(0.1)
        logger.info(f"Completed action: {action_name}")
        return True
    except Exception as e:
        logger.error(f"Action {action_name} failed: {e}")
        return False

def safe_rgb(dog, mode, color, bps, brightness):
    try:
        logger.info(f"Setting RGB mode: {mode}")
        dog.rgb_strip.set_mode(mode, color=color, bps=bps, brightness=brightness)
        sleep(0.5)
        logger.info("RGB set successfully")
    except Exception as e:
        logger.error(f"RGB setting failed: {e}")

def safe_head_move(dog, angles, **kwargs):
    try:
        logger.info("Moving head")
        dog.head_move(angles, **kwargs)
        sleep(0.5)
        logger.info("Head move completed")
    except Exception as e:
        logger.error(f"Head move failed: {e}")

def wake_up(my_dog):
    try:
        # Initial setup
        logger.info("Starting wake up sequence")
        safe_rgb(my_dog, 'listen', 'yellow', 0.6, 0.8)
        sleep(1)

        # Basic movements
        logger.info("Starting basic movements")
        safe_action(my_dog, 'stretch', timeout=3, speed=50)
        sleep(1)

        safe_head_move(my_dog, [[0, 0, 30]], immediately=True)
        sleep(1)

        # Sit sequence
        logger.info("Starting sit sequence")
        safe_action(my_dog, 'sit', timeout=3, speed=25)
        sleep(1)

        # Wag tail sequence
        logger.info("Starting wag tail")
        safe_action(my_dog, 'wag_tail', timeout=2, step_count=3, speed=100)
        safe_rgb(my_dog, 'breath', [245, 10, 10], 2.5, 0.8)
        sleep(1)

        # Hold pattern with simple wag
        logger.info("Entering hold pattern")
        count = 0
        while True:
            try:
                count += 1
                logger.info(f"Hold pattern iteration: {count}")
                safe_action(my_dog, 'wag_tail', timeout=2, step_count=3, speed=30)
                safe_rgb(my_dog, 'breath', 'pink', 0.5, 0.8)
                sleep(2)
            except Exception as e:
                logger.error(f"Hold pattern error: {e}")
                sleep(1)

    except Exception as e:
        logger.error(f"Error during wake up sequence: {e}")
        raise

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog wake up program")
        my_dog = Pidog(head_init_angles=[0, 0, -30])
        logger.info("PiDog initialized successfully")
        sleep(2)  # Added longer delay after initialization
        
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