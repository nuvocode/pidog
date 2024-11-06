import asyncio
import websockets
import json
from pidog import Pidog
from vilib import Vilib
import time
import os
import logging
from datetime import datetime
from preset_actions import hand_shake, high_five
import sys
import signal

# Initialize logging
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

# Global variables
my_dog = None
server = None
is_running = True

# Head control variables
head_yrp = [0, 0, 0]
head_pitch_init = 0
HEAD_SPEED = 80

def cleanup():
    global my_dog, is_running
    logger.info("Cleaning up resources...")
    is_running = False
    
    if my_dog:
        try:
            my_dog.rgb_strip.set_mode('off')
            my_dog.close()
        except Exception as e:
            logger.error(f"Error closing PiDog: {e}")
    
    try:
        Vilib.camera_close()
    except Exception as e:
        logger.error(f"Error closing camera: {e}")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

def getIP():
    wlan0 = os.popen("ifconfig wlan0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
    eth0 = os.popen("ifconfig eth0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
    return wlan0 if wlan0 != '' else eth0

async def welcome_sequence(my_dog):
    try:
        logger.info("Starting welcome sequence")
        my_dog.do_action('sit', speed=80)
        await asyncio.sleep(1)
        
        my_dog.rgb_strip.set_mode('breath', color='green', bps=1.0)
        my_dog.speak('pasha', 100)
        await asyncio.sleep(1)
        
        my_dog.rgb_strip.set_mode('breath', color='blue', bps=1.0)
        hand_shake(my_dog)
        await asyncio.sleep(1)
        
        my_dog.rgb_strip.set_mode('breath', color='red', bps=1.0)
        high_five(my_dog)
        await asyncio.sleep(1)
        
        my_dog.rgb_strip.set_mode('breath', color='yellow', bps=0.5)
        my_dog.do_action('sit', speed=80)
        await asyncio.sleep(1)
        
        return True
    except Exception as e:
        logger.error(f"Error during welcome sequence: {e}")
        return False

async def handle_command(websocket, path):
    try:
        async for message in websocket:
            if not is_running:
                break
                
            logger.info(f"Received message: {message}")
            try:
                data = json.loads(message)
                command_type = data.get('command')
                
                if command_type == 'head_move':
                    try:
                        head_data = data.get('data', {})
                        yaw = head_data.get('yaw', 0)
                        pitch = head_data.get('pitch', 0)
                        roll = head_data.get('roll', 0)
                        
                        head_yrp[0] = yaw
                        head_yrp[1] = roll
                        head_yrp[2] = pitch
                        
                        my_dog.head_move([head_yrp], pitch_comp=head_pitch_init,
                                       immediately=True, speed=HEAD_SPEED)
                        
                    except Exception as e:
                        logger.error(f"Error in head movement: {e}")

                elif command_type == 'welcome':
                    try:
                        await websocket.send(json.dumps({
                            'status': 'success',
                            'command': 'welcome'
                        }))
                        await welcome_sequence(my_dog)
                    except Exception as e:
                        logger.error(f"Error in welcome sequence: {e}")
                        await websocket.send(json.dumps({
                            'status': 'error',
                            'command': 'welcome',
                            'message': str(e)
                        }))

                elif command_type == 'sit':
                    try:
                        await websocket.send(json.dumps({
                            'status': 'success',
                            'command': 'sit'
                        }))
                        my_dog.do_action('sit', speed=80)
                    except Exception as e:
                        logger.error(f"Error in sit command: {e}")
                        await websocket.send(json.dumps({
                            'status': 'error',
                            'command': 'sit',
                            'message': str(e)
                        }))

                elif command_type == 'stand':
                    try:
                        await websocket.send(json.dumps({
                            'status': 'success',
                            'command': 'stand'
                        }))
                        my_dog.do_action('stand', speed=80)
                    except Exception as e:
                        logger.error(f"Error in stand command: {e}")
                        await websocket.send(json.dumps({
                            'status': 'error',
                            'command': 'stand',
                            'message': str(e)
                        }))

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding message: {e}")
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': f"JSON decode error: {str(e)}"
                }))
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                await websocket.send(json.dumps({
                    'status': 'error',
                    'message': f"Processing error: {str(e)}"
                }))

    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

async def main():
    global my_dog, server, is_running
    
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize PiDog
        logger.info("Initializing PiDog")
        my_dog = Pidog()
        time.sleep(0.5)
        
        # Start video stream
        logger.info("Starting video stream")
        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.display(local=False, web=True)
        
        # Get and display IP
        ip = getIP()
        logger.info(f'Video stream available at: http://{ip}:9000/mjpg')
        logger.info(f'WebSocket server starting on ws://{ip}:8765')

        # Start WebSocket server
        server = await websockets.serve(handle_command, "0.0.0.0", 8765)
        logger.info("WebSocket server running...")
        
        # Keep the server running
        while is_running:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"\033[31mERROR: {e}\033[m")
    finally:
        cleanup()