import sys
import time
import asyncio
import aiohttp
import logging
from pyfiglet import Figlet
from rich.console import Console
from geopy.geocoders import Nominatim
from concurrent.futures import ThreadPoolExecutor

console = Console()

# Set up logging
logging.basicConfig(filename='geolock.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize geolocator
geolocator = Nominatim(user_agent="GeoLock")


async def get_messages():
    try:
        # Discord bot token and channel ID
        BOT_TOKEN = ''
        CHANNEL_ID = '1233543633286860910'

        url = f'https://discord.com/api/v9/channels/{CHANNEL_ID}/messages'
        headers = {'Authorization': f'Bot {BOT_TOKEN}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    messages = await response.json()
                    for message in messages:
                        if 'Location:' in message['content']:
                            location_data = message['content'].split(': ')[1]
                            logger.info('Received location: %s', location_data)
                            return location_data
                else:
                    logger.error('Failed to fetch messages: %s', response.status)
                    print('Failed to fetch messages: %s', response.status)
    except Exception as e:
        logger.error('An error occurred while fetching messages: %s', str(e))
        print('An error occurred while fetching messages:', str(e))

def parse_location(location_data):
    try:
        logger.info('Parsing data...')
        components = location_data.split(', ')
        latitude = None
        longitude = None
        for component in components:
            if component.startswith('Latitude='):
                latitude = float(component.split('=')[1])
            elif component.startswith('Longitude='):
                longitude = float(component.split('=')[1])
        return latitude, longitude
    except Exception as e:
        logger.error('An error occurred while parsing location data: %s', str(e))
        print('An error occurred while parsing location data:', str(e))
        return None, None

def reverse_geocode(latitude, longitude):
    try:
        logger.info('Fetching location...')
        location = geolocator.reverse((latitude, longitude), language='en')
        logger.info('Current Location: %s', location.address)
        return location  # Return the location object directly
    except Exception as e:
        logger.error('An error occurred while fetching location: %s', str(e))
        print('An error occurred while fetching location:', str(e))
        return None

async def get_coordinates():
    try:
        loc_data = await get_messages()
        if loc_data:
            lat, lon = parse_location(loc_data)
            return lat, lon
    except Exception as e:
        logger.error('An error occurred while getting coordinates: %s', str(e))
        print('An error occurred while getting coordinates:', str(e))
        return None, None

async def display_location(get_coordinates):
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()

        while True:
            try:
                latitude, longitude = await get_coordinates()
                if latitude is not None and longitude is not None:
                    location = await loop.run_in_executor(executor, reverse_geocode, latitude, longitude)
                    sys.stdout.write("\033[F")  # Move the cursor up one line
                    sys.stdout.write("\r\033[K")  # Clear the line
                    sys.stdout.write("\033[F")  # Move the cursor up one line
                    sys.stdout.write("\r\033[K")  # Clear the line
                    sys.stdout.write("\r\033[K")  # Clear the line
                    sys.stdout.write(f"Location: {location.address}\n")
                    sys.stdout.flush()
                else:
                    print("Invalid coordinates")
                time.sleep(10)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error('An error occurred while displaying location: %s', str(e))
                print('An error occurred while displaying location:', str(e))
                time.sleep(10)
                

async def main():
    # Display Logo ASCII art and introduction
    logo = """
                       ...:::::::...                       
                   .::---==-==-==---:::.                   
                 .::-===+********+===-:-.                  
                 :--:--+#%%%%%%%%*=---:--:                 
                :-::''';:=++==:-++;''':..:..                
               ==-:"'~.`_.:.-:.:-._',.'"::::.               
              .:=+:::---:...+-...-:--:.:-:=-:.              
            .-==++--=+*=: \..+-../ :=*+=-*&^=+=.             
            :==+*++=++++=- =::;::  -+++++++=+=-:            
           .:*#+*+++++++**. ";;"  **++++**+=++-.           
           -++******#*+=--_{  ' }_--==++*##***++*          
           ..+-**#*+#%#**+**&**%+*##%%#*++=*#+..           
    """
    f = Figlet(font='linux')
    intro_f = (f.renderText("      GEOLOCK"))
    console.print(intro_f + logo, style="bold red")
    console.print("\n**ctrl+shift+m to open live mapview in browser.", style="bold yellow")
    console.print("**ctrl+shift+q to shutdown websocket server.", style="bold yellow")

    console.print("                             _._EAGLEYES_._", style="italic bold black")
    console.print("      ._ _ _ _ __ _ _ _ _ __ _ _ _ _ _ _ __ _ _ _ _ _ __ _ _ _ _. ", style="bold red")
    print("\n")

    print("Initializing....")
    try:
        while True:
            await display_location(get_coordinates)
            await asyncio.sleep(7)  # Adjust the sleep time as needed
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
