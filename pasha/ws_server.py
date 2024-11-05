import asyncio
import websockets
import json
from pidog import Pidog
from vilib import Vilib
import time
import os

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

async def handle_command(websocket, path):
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            try:
                data = json.loads(message)
                command_type = data.get('command')
                
                if command_type == 'head_move':
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
                    await websocket.send(json.dumps(response))
                    print(f"Head moved to - Yaw: {yaw}, Pitch: {pitch}, Roll: {roll}")
                
                elif command_type == 'voice_command':
                    command = data.get('data', {}).get('command', '')
                    print(f"Received voice command: {command}")
                    # Add voice command handling here if needed
                    response = {
                        'status': 'success',
                        'command': 'voice_command',
                        'processed': command
                    }
                    await websocket.send(json.dumps(response))

            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
                await websocket.send(json.dumps({'status': 'error', 'message': str(e)}))
            except Exception as e:
                print(f"Error processing command: {e}")
                await websocket.send(json.dumps({'status': 'error', 'message': str(e)}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def main():
    # Start video stream
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=True)
    
    # Get and display IP
    ip = getIP()
    print(f'Video stream available at: http://{ip}:9000/mjpg')
    print(f'WebSocket server starting on ws://{ip}:8765')

    # Start WebSocket server
    server = await websockets.serve(handle_command, "0.0.0.0", 8765)
    print("WebSocket server running...")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        my_dog.close()
        Vilib.camera_close()