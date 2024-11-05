#!/usr/bin/env python3
import logging
from pidog import Pidog
from time import sleep
import time
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

def safe_action(dog, action_name, timeout=5, **kwargs):
    try:
        logger.info(f"Attempting action: {action_name}")
        # First, ensure no other actions are running
        sleep(0.5)
        start_time = time.time()
        dog.do_action(action_name, **kwargs)
        current_time = time.time()
        while current_time - start_time < timeout:
            sleep(0.2)
            current_time = time.time()
            if current_time - start_time > timeout:
                logger.warning(f"Action {action_name} timed out")
                break
        logger.info(f"Completed action: {action_name}")
        return True
    except Exception as e:
        logger.error(f"Action {action_name} failed: {e}")
        return False

def safe_rgb(dog, mode, color, bps, brightness):
    try:
        logger.info(f"Setting RGB mode: {mode}")
        sleep(0.2)  # Small delay before accessing RGB
        dog.rgb_strip.set_mode(mode, color=color, bps=bps, brightness=brightness)
        sleep(0.2)  # Small delay after setting RGB
        logger.info("RGB set successfully")
    except Exception as e:
        logger.error(f"RGB setting failed: {e}")

def wake_up(my_dog):
    try:
        # Just try RGB first
        logger.info("Testing RGB only")
        safe_rgb(my_dog, 'breath', 'blue', 0.5, 0.8)
        sleep(2)

        # Test simple head movement
        logger.info("Testing head movement")
        try:
            my_dog.head_move([[0, 0, 0]], immediately=True, speed=50)
            sleep(2)
            logger.info("Head movement successful")
        except Exception as e:
            logger.error(f"Head movement failed: {e}")

        # Test simple sitting
        logger.info("Testing sit action")
        if safe_action(my_dog, 'sit', timeout=3, speed=25):
            logger.info("Sit action successful")
            sleep(2)
        
        # If we got this far, try a simple wag
        logger.info("Testing wag")
        if safe_action(my_dog, 'wag_tail', timeout=2, step_count=2, speed=30):
            logger.info("Wag successful")
            sleep(2)

        # Enter a very simple hold pattern
        logger.info("Entering simplified hold pattern")
        while True:
            safe_rgb(my_dog, 'breath', 'pink', 0.5, 0.8)
            sleep(3)
            logger.info("Hold pattern cycle complete")

    except Exception as e:
        logger.error(f"Error during wake up sequence: {e}")
        raise

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog wake up program")
        my_dog = Pidog(head_init_angles=[0, 0, 0])  # Starting with neutral position
        logger.info("PiDog initialized successfully")
        sleep(3)  # Longer delay after initialization
        
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