import discord
import requests
import asyncio
import os
from keep_alive import keep_alive
from datetime import date, datetime

#Change the below lines

#List of species to filter out (example list put in)
filtered_species = {
  #Canada Goose,
  #American Robin
  }

# Replace YOUR_DISCORD_BOT_TOKEN with your actual bot token
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_SECRET']

# Replace YOUR_DISCORD_CHANNEL_ID with the ID of the channel where you want to send messages
DISCORD_CHANNEL_ID = '1136054663674867912'

# Replace YOUR_EBIRD_API_KEY with your eBird API key
EBIRD_API_KEY = os.environ['EBIRD_SECRET']

# Illinois Region Code for eBird API
IL_REGION_CODE = 'US-IL'

# URL to check for new rare bird sightings in Illinois
EBIRD_API_URL = f'https://api.ebird.org/v2/data/obs/{IL_REGION_CODE}/recent/notable?back=1&detail=full'

# Global variable to keep track of the last sighting ID
last_sighting_id = None

# Function to create a message embed for the bird sighting
def create_sighting_embed(sighting):
    embed = discord.Embed(
        title=sighting['comName']+ " | " + sighting['subnational2Name'] + " County",
        color=0x00ff00,  # You can customize the color here
    )
    embed.add_field(name="Observer", value=sighting['userDisplayName'], inline=False)
    embed.add_field(name="Location", value=sighting['locName'], inline=False)
    embed.add_field(name="Date", value=sighting['obsDt'], inline=False)
    embed.add_field(name="Confirmed?", value=sighting['obsValid'], inline=False)
    embed.add_field(name="Check it out on eBird", value="https://ebird.org/checklist/" + sighting['subId'], inline=False)
    return embed

# Global variable to keep track of old sightings
old_sightings = []

# Function to fetch and process new bird sightings
async def check_for_new_sightings():
    try:
        # Step 1: Fetch notable bird sightings from the eBird API
        response = requests.get(EBIRD_API_URL, headers={'X-eBirdApiToken': EBIRD_API_KEY})
        response.raise_for_status()
        sightings = response.json()

        
        # Get the current time in UTC timezone
        current_time_utc = datetime.utcnow()

        # Set the timezone to Eastern Time (US & Canada)
        eastern_timezone = pytz.timezone('US/Eastern')

        # Convert current_time_utc to Eastern Time
        current_time = current_time_utc.astimezone(eastern_timezone)

        for new_sighting in sightings:
            # Create a unique ID for the sighting using species code, county, and observation date
            new_sighting_id = new_sighting['speciesCode'] + new_sighting['subnational2Name'] + new_sighting['obsDt'][:10] 

            if new_sighting_id not in old_sightings:
                comName = new_sighting['comName'].split('(')[0].strip()  # Remove characters after "("

                # Check if the species is not in the filtered list
                if comName not in filtered_species:
                    # Step 2: Fetch the checklist details to check its submission time
                    checklist_url = f'https://api.ebird.org/v2/product/checklist/view/{new_sighting["subId"]}'
                    checklist_response = requests.get(checklist_url, headers={'X-eBirdApiToken': EBIRD_API_KEY})
                    checklist_response.raise_for_status()
                    checklist_data = checklist_response.json()

                    # Get the submission time from the checklist details
                    submission_time_str = checklist_data['creationDt']

            # Convert the submission time to a datetime object and make it offset-aware (in Eastern Time)
                    creation_time = eastern_timezone.localize(datetime.strptime(submission_time_str, '%Y-%m-%d %H:%M'))
                    #print(current_time)
                    #print(creation_time)
            # Calculate the time difference between current time and submission time
                    time_difference = current_time - creation_time
                    #print(time_difference.total_seconds())

                    # Only process the sighting if the checklist was submitted within the last 5 minutes
                    if time_difference.total_seconds() <= 3600:
                        old_sightings.append(new_sighting_id)

                        # If the list exceeds 1000000 records, remove the oldest record(s) to maintain the limit
                        if len(old_sightings) > 10000:
                            old_sightings.pop(0)

                        # Create the message embed for the sighting
                        embed = create_sighting_embed(new_sighting)

                        # Send the embed message to Discord channel
                        channel = client.get_channel(int(DISCORD_CHANNEL_ID))
                        await channel.send(embed=embed)
    except Exception as e:
        print(f"Error: {e}")



# Initialize the Discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

status = cycle(['Watching for Rare Birds','Keeping an Eye on the Skies (or eBird)'])

# Event to run when the bot is ready
@client.event
async def on_ready():
    change_status.start()
    print("Your bot is ready")
    print(f'We have logged in as {client.user}')

    # Run the check_for_new_sightings function every 2 minutes
    while True:
        await check_for_new_sightings()
        await asyncio.sleep(3600)  # 120 seconds = 2 minutes


@tasks.loop(seconds=10)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))

# Run the bot with the provided token
keep_alive()
client.run(DISCORD_BOT_TOKEN)