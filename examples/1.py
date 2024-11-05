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

def safe_action(dog, action_name, timeout=3, **kwargs):
    try:
        logger.info(f"Attempting action: {action_name}")
        start_time = time.time()
        dog.do_action(action_name, **kwargs)
        sleep(0.1)
        
        while time.time() - start_time < timeout:
            sleep(0.1)
            if dog.legs_done:
                logger.info(f"Action {action_name} completed naturally")
                return True
            
        logger.warning(f"Action {action_name} timed out")
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
        logger.info("Performing head movement")
        my_dog.head_move([[0, 0, 20], [0, 0, -20], [0, 0, 0]], 
                        speed=80,
                        immediately=True)
        sleep(1)
        
        # Sit sequence
        logger.info("Sitting")
        safe_action(my_dog, 'sit', timeout=2, speed=50)
        safe_rgb(my_dog, 'breath', 'green', 1.0, 0.8)
        sleep(2)
        
        # Stand sequence
        logger.info("Standing")
        safe_action(my_dog, 'stand', timeout=2, speed=50)
        safe_rgb(my_dog, 'breath', 'pink', 1.0, 0.8)
        sleep(2)
        
        # Final state
        logger.info("Entering final state")
        safe_rgb(my_dog, 'breath', 'purple', 0.5, 0.8)
        sleep(3)
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