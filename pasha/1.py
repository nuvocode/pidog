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

def safe_action(dog, action_name, **kwargs):
    try:
        logger.info(f"Performing action: {action_name}")
        dog.do_action(action_name, **kwargs)
        sleep(2)  # Simple fixed delay
        return True
    except Exception as e:
        logger.error(f"Action {action_name} failed: {e}")
        return False

def safe_rgb(dog, mode, color, bps, brightness):
    try:
        dog.rgb_strip.set_mode(mode, color=color, bps=bps, brightness=brightness)
        sleep(0.1)
    except Exception as e:
        logger.error(f"RGB setting failed: {e}")

def wake_up(my_dog):
    try:
        # Initial RGB
        logger.info("Starting wake-up sequence")
        safe_rgb(my_dog, 'breath', 'blue', 1.0, 0.8)
        sleep(1)
        
        # Simple head movement
        logger.info("Moving head")
        my_dog.head_move([[0, 0, 20]], immediately=True, speed=80)
        sleep(1)
        my_dog.head_move([[0, 0, -20]], immediately=True, speed=80)
        sleep(1)
        my_dog.head_move([[0, 0, 0]], immediately=True, speed=80)
        sleep(1)
        
        # Sit sequence
        safe_rgb(my_dog, 'breath', 'green', 1.0, 0.8)
        safe_action(my_dog, 'sit', speed=50)
        sleep(2)
        
        # Stand sequence
        safe_rgb(my_dog, 'breath', 'red', 1.0, 0.8)
        safe_action(my_dog, 'stand', speed=50)
        sleep(2)
        
        # Final state
        safe_rgb(my_dog, 'breath', 'yellow', 0.5, 0.8)
        logger.info("Sequence complete")

    except Exception as e:
        logger.error(f"Error during wake up sequence: {e}")
        raise

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog wake up program")
        my_dog = Pidog(head_init_angles=[0, 0, 0])
        logger.info("PiDog initialized successfully")
        sleep(1)
        
        wake_up(my_dog)

    except KeyboardInterrupt:
        logger.info("Program stopped by user")
        if my_dog:
            safe_rgb(my_dog, 'off', 'blue', 0, 0)
            
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