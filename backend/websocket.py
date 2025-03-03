import os
import sys
import logging
import asyncio
import threading
import websockets
import webbrowser
from pynput import keyboard
from geolock import get_coordinates, parse_location



# Set up logging for WebSocket errors
logger = logging.getLogger('websocket_logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('websocket.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

server = None
stop_event = threading.Event()

async def handle_client(websocket, path):
    try:
        while not stop_event.is_set():
            coordinates = await get_coordinates()
            if coordinates:
                latitude, longitude = coordinates
                await websocket.send(f"Latitude={latitude}, Longitude={longitude}")
            await asyncio.sleep(5)
    except websockets.exceptions.ConnectionClosedError:
        logger.error("Client connection closed.")
    except Exception as e:
        logger.exception("An error occurred: %s", e)

async def start_websocket_server():
    global server
    server = await websockets.serve(handle_client, "localhost", 8765)
    await server.wait_closed()

def close_websocket_server():
    global server
    if server:
        server.close()
        asyncio.run(server.wait_closed())

def run_websocket_server():
    asyncio.run(start_websocket_server())
    
def listen_for_hotkeys():
    with keyboard.GlobalHotKeys({
        '<ctrl>+<shift>+q': on_activate_q,
        '<ctrl>+<shift>+m': on_activate_m}) as h:
            stop_event.wait()
            h.stop()

def on_activate_q():
    try:
        logger.info("Shutting down WebSocket server...")
        stop_event.set()
        close_websocket_server()
        sys.exit()
        os._exit(0)  # Ensure complete exit
    except Exception as e:
        logger.exception("An error occurred: %s", "Shutdown Successful")
        pass

def on_activate_m():
    try:
        logger.info("Opening map view in browser...")
        webbrowser.open('/home/kali/eagleyes/frontend/index.html')
    except Exception as e:
        logger.exception("An error occurred: %s", e)

def main():
    try:
        websocket_thread = threading.Thread(target=run_websocket_server)
        websocket_thread.daemon = True
        websocket_thread.start()

        hotkey_thread = threading.Thread(target=listen_for_hotkeys)
        hotkey_thread.start()

        websocket_thread.join()
        hotkey_thread.join()
    except Exception as e:
        logger.exception("An error occurred: %s", "Server terminated")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("An error occurred: %s", e)
