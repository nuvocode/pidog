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

# Initialize PiDog
my_dog = Pidog()
time.sleep(0.5)

# Head control variables
head_yrp = [0, 0, 0]
head_pitch_init = 0
HEAD_SPEED = 80

def getIP():
    wlan0 = os.popen("ifconfig wlan0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
    eth0 = os.popen("ifconfig eth0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
    return wlan0 if wlan0 != '' else eth0

async def welcome_sequence(my_dog):
    try:
        logger.info("Starting welcome sequence")
        # Initial sit
        my_dog.do_action('sit', speed=80)
        await asyncio.sleep(1)
        
        # Play sound and flash RGB
        logger.info("Playing sound and setting RGB")
        my_dog.rgb_strip.set_mode('breath', color='green', bps=1.0)
        my_dog.speak('pasha', 100)
        await asyncio.sleep(1)
        
        # Handshake
        logger.info("Performing handshake")
        my_dog.rgb_strip.set_mode('breath', color='blue', bps=1.0)
        hand_shake(my_dog)
        await asyncio.sleep(1)
        
        # High five
        logger.info("Performing high five")
        my_dog.rgb_strip.set_mode('breath', color='red', bps=1.0)
        high_five(my_dog)
        await asyncio.sleep(1)
        
        # Return to normal position
        logger.info("Returning to sit position")
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
                        
                        # Update head position
                        head_yrp[0] = yaw
                        head_yrp[1] = roll
                        head_yrp[2] = pitch
                        
                        # Move head
                        my_dog.head_move([head_yrp], pitch_comp=head_pitch_init,
                                       immediately=True, speed=HEAD_SPEED)
                        
                        response = {
                            'status': 'success',
                            'command': 'head_move',
                            'position': {'yaw': yaw, 'pitch': pitch, 'roll': roll}
                        }
                        logger.info(f"Head moved to - Yaw: {yaw}, Pitch: {pitch}, Roll: {roll}")
                    except Exception as e:
                        logger.error(f"Error in head movement: {e}")
                        response = {
                            'status': 'error',
                            'command': 'head_move',
                            'message': str(e)
                        }
                    await websocket.send(json.dumps(response))

                elif command_type == 'welcome':
                    try:
                        logger.info("Processing welcome command")
                        success = await welcome_sequence(my_dog)
                        response = {
                            'status': 'success' if success else 'error',
                            'command': 'welcome'
                        }
                        logger.info("Welcome sequence completed")
                    except Exception as e:
                        logger.error(f"Error in welcome sequence: {e}")
                        response = {
                            'status': 'error',
                            'command': 'welcome',
                            'message': str(e)
                        }
                    await websocket.send(json.dumps(response))

                elif command_type == 'sit':
                    try:
                        logger.info("Processing sit command")
                        my_dog.do_action('sit', speed=80)
                        await asyncio.sleep(1)
                        response = {
                            'status': 'success',
                            'command': 'sit'
                        }
                        logger.info("Sit command completed")
                    except Exception as e:
                        logger.error(f"Error in sit command: {e}")
                        response = {
                            'status': 'error',
                            'command': 'sit',
                            'message': str(e)
                        }
                    await websocket.send(json.dumps(response))

                elif command_type == 'stand':
                    try:
                        logger.info("Processing stand command")
                        my_dog.do_action('stand', speed=80)
                        await asyncio.sleep(1)
                        response = {
                            'status': 'success',
                            'command': 'stand'
                        }
                        logger.info("Stand command completed")
                    except Exception as e:
                        logger.error(f"Error in stand command: {e}")
                        response = {
                            'status': 'error',
                            'command': 'stand',
                            'message': str(e)
                        }
                    await websocket.send(json.dumps(response))
                    
                elif command_type == 'voice_command':
                    try:
                        command = data.get('data', {}).get('command', '')
                        logger.info(f"Received voice command: {command}")
                        response = {
                            'status': 'success',
                            'command': 'voice_command',
                            'processed': command
                        }
                    except Exception as e:
                        logger.error(f"Error in voice command: {e}")
                        response = {
                            'status': 'error',
                            'command': 'voice_command',
                            'message': str(e)
                        }
                    await websocket.send(json.dumps(response))

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
    try:
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
        await server.wait_closed()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"\033[31mERROR: {e}\033[m")
    finally:
        try:
            my_dog.close()
            Vilib.camera_close()
            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")