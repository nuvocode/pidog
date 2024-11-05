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

def safe_action(dog, action_name, timeout=3, **kwargs):  # Reduced default timeout
    try:
        logger.info(f"Attempting action: {action_name}")
        start_time = time.time()
        dog.do_action(action_name, **kwargs)
        sleep(0.1)  # Shorter initial delay
        
        # Wait for action with faster checking
        while time.time() - start_time < timeout:
            sleep(0.1)  # Faster polling
            if dog.legs_done:  # Check if action is actually complete
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
        sleep(0.1)  # Minimal delay
    except Exception as e:
        logger.error(f"RGB setting failed: {e}")

def safe_sound(dog, sound_name):
    try:
        logger.info(f"Playing sound: {sound_name}")
        dog.sound_effect.sound_effect_threading(sound_name)
        sleep(0.1)  # Small delay to let sound start
    except Exception as e:
        logger.error(f"Sound playback failed: {e}")

def wake_up(my_dog):
    try:
        # Initial wake-up sequence
        logger.info("Starting wake-up sequence")
        safe_rgb(my_dog, 'breath', 'blue', 1.0, 0.8)  # Faster breathing
        safe_sound(my_dog, 'wakeup')  # Add wake-up sound
        
        # Head movement with sound
        logger.info("Performing head movement")
        my_dog.head_move([[0, 0, 20], [0, 0, -20], [0, 0, 0]], 
                        speed=80,  # Faster speed
                        immediately=True)
        safe_sound(my_dog, 'bark')
        sleep(1)

        # Quick stretch sequence
        logger.info("Stretching")
        safe_action(my_dog, 'stretch', timeout=2, speed=80)  # Faster stretch
        safe_sound(my_dog, 'pant')
        
        # Sit and wag sequence
        logger.info("Sitting and wagging")
        safe_action(my_dog, 'sit', timeout=2, speed=50)
        safe_rgb(my_dog, 'breath', 'green', 1.0, 0.8)
        
        # More dynamic wagging
        for _ in range(3):  # Multiple quick wags
            safe_action(my_dog, 'wag_tail', timeout=1, step_count=2, speed=80)
            safe_sound(my_dog, 'bark_short')
            sleep(0.5)

        # Hold pattern with occasional actions
        logger.info("Entering interactive hold pattern")
        safe_rgb(my_dog, 'breath', 'pink', 0.5, 0.8)
        
        count = 0
        while True:
            count += 1
            if count % 5 == 0:  # Every 5 cycles
                safe_sound(my_dog, 'bark_short')
                safe_action(my_dog, 'wag_tail', timeout=1, step_count=1, speed=50)
            sleep(2)
            logger.info("Hold pattern cycle complete")

    except Exception as e:
        logger.error(f"Error during wake up sequence: {e}")
        raise

def main():
    my_dog = None
    try:
        logger.info("Starting PiDog wake up program")
        my_dog = Pidog(head_init_angles=[0, 0, 0])
        logger.info("PiDog initialized successfully")
        sleep(1)  # Shorter initial delay
        
        wake_up(my_dog)

    except KeyboardInterrupt:
        logger.info("Program stopped by user")
        # Add a goodbye sound
        if my_dog:
            safe_sound(my_dog, 'sleep')
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