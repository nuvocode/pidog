#!/usr/bin/env python3
import logging
from pidog import Pidog
from time import sleep
import time
from preset_actions import pant
from preset_actions import body_twisting
import sys
from datetime import datetime
from functools import wraps

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

# Decorator for timeout handling
def timeout_handler(timeout_duration=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                if time.time() - start_time > timeout_duration:
                    logger.warning(f"{func.__name__} took longer than {timeout_duration} seconds")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return None
        return wrapper
    return decorator

class SafePidog:
    def __init__(self):
        self.dog = None
        self.init_pidog()

    @timeout_handler(5)
    def init_pidog(self):
        try:
            self.dog = Pidog(head_init_angles=[0, 0, -30])
            logger.info("PiDog initialized successfully")
            sleep(1)
        except Exception as e:
            logger.error(f"Failed to initialize PiDog: {e}")
            raise

    @timeout_handler(3)
    def set_rgb(self, mode, color, bps, brightness):
        try:
            self.dog.rgb_strip.set_mode(mode, color=color, bps=bps, brightness=brightness)
            sleep(0.5)  # Give time for RGB to stabilize
        except Exception as e:
            logger.error(f"RGB strip error: {e}")

    @timeout_handler(5)
    def perform_action(self, action_name, **kwargs):
        try:
            self.dog.do_action(action_name, **kwargs)
            self.dog.wait_all_done()
            sleep(0.5)  # Buffer between actions
        except Exception as e:
            logger.error(f"Action error ({action_name}): {e}")

    @timeout_handler(3)
    def move_head(self, angles, **kwargs):
        try:
            self.dog.head_move(angles, **kwargs)
            sleep(0.3)  # Give head movement time to complete
        except Exception as e:
            logger.error(f"Head movement error: {e}")

    def wake_up(self):
        try:
            # Initial stretch sequence
            logger.info("Starting wake up sequence - stretch")
            self.set_rgb('listen', 'yellow', 0.6, 0.8)
            sleep(0.5)

            self.perform_action('stretch', speed=50)
            sleep(0.5)

            self.move_head([[0, 0, 30]]*2, immediately=True)
            sleep(0.5)

            # Body twisting sequence
            logger.info("Performing body twisting")
            try:
                body_twisting(self.dog)
                self.dog.wait_all_done()
            except Exception as e:
                logger.error(f"Body twisting error: {e}")
            sleep(1)

            self.move_head([[0, 0, -30]], immediately=True, speed=90)
            sleep(0.5)

            # Sit and wag sequence
            logger.info("Starting sit and wag tail sequence")
            self.perform_action('sit', speed=25)
            sleep(1)

            self.perform_action('wag_tail', step_count=10, speed=100)
            sleep(0.5)

            self.set_rgb('breath', [245, 10, 10], 2.5, 0.8)
            sleep(0.5)

            # Panting sequence
            try:
                pant(self.dog, pitch_comp=-30, volume=80)
            except Exception as e:
                logger.error(f"Panting error: {e}")
            sleep(1)

            # Hold pattern
            logger.info("Entering hold pattern")
            self.perform_action('wag_tail', step_count=10, speed=30)
            self.set_rgb('breath', 'pink', 0.5, 0.8)

            while True:
                sleep(1)

        except Exception as e:
            logger.error(f"Error during wake up sequence: {e}")
            raise

    def close(self):
        try:
            if self.dog is not None:
                logger.info("Closing PiDog connection")
                self.dog.close()
        except Exception as e:
            logger.error(f"Error while closing PiDog: {e}")

def main():
    pidog = None
    try:
        logger.info("Starting PiDog wake up program")
        pidog = SafePidog()
        pidog.wake_up()

    except KeyboardInterrupt:
        logger.info("Program stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
    finally:
        if pidog is not None:
            pidog.close()

if __name__ == "__main__":
    main()