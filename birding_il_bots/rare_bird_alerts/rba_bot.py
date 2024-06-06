import logging
from datetime import datetime
from itertools import cycle
from datetime import timedelta

import discord
import requests
from discord.ext import tasks

from ..secret_provider import get_current_version_of_text_secret
from .filtered_species_provider import get_filtered_species

LOG = logging.getLogger(__name__)

CHANNEL_NAME = "ebird-alerts"

# Replace YOUR_EBIRD_API_KEY with your eBird API key
EBIRD_API_KEY = get_current_version_of_text_secret("ebird-api-key")

# Illinois Region Code for eBird API
IL_REGION_CODE = 'US-IL'

UPDATE_INTERVAL = timedelta(hours=1)

# Initialize the Discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)
status = cycle(['Watching for Rare Birds',
               'Keeping an Eye on the Skies (or eBird)'])


def create_sighting_embed(sighting):
    """Create a message embed for the bird sighting"""
    embed = discord.Embed(
        title=sighting['comName'] + " | " +
        sighting['subnational2Name'] + " County",
        color=0x00ff00,  # You can customize the color here
    )
    embed.add_field(name="Observer",
                    value=sighting['userDisplayName'], inline=False)
    embed.add_field(name="Location", value=sighting['locName'], inline=False)
    embed.add_field(name="Date", value=sighting['obsDt'], inline=False)
    embed.add_field(name="Confirmed?",
                    value=sighting['obsValid'], inline=False)
    embed.add_field(name="Check it out on eBird",
                    value="https://ebird.org/checklist/" + sighting['subId'], inline=False)
    return embed


# Global var to track first fun
first_run = True

# Global variable to keep track of old sightings
old_sightings = []


def check_for_new_sightings():
    """Fetch and process new bird sightings"""
    # Step 1: Fetch notable bird sightings from the eBird API
    response = requests.get(
        f'https://api.ebird.org/v2/data/obs/{IL_REGION_CODE}/recent/notable?back=1&detail=full', headers={'X-eBirdApiToken': EBIRD_API_KEY})
    response.raise_for_status()
    sightings = response.json()

    embeds = []
    already_seen_this_run = []
    filtered_out_this_run = []

    for new_sighting in sightings:
        # Create a unique ID for the sighting using species code, county, and observation date
        new_sighting_id = new_sighting['speciesCode'] + \
            new_sighting['subnational2Name'] + new_sighting['obsDt'][:10]

        if new_sighting_id in old_sightings:
            already_seen_this_run.append(new_sighting_id)
            continue

        comName = new_sighting['comName'].split(
            '(')[0].strip()  # Remove characters after "("

        # Check if the species is not in the filtered list
        if comName in get_filtered_species():
            filtered_out_this_run.append(new_sighting_id)
            continue

        old_sightings.append(new_sighting_id)

        if len(old_sightings) > 1000:
            old_sightings.pop(0)

        embed = create_sighting_embed(new_sighting)

        LOG.debug("Adding embed %s", embed)
        embeds.append(embed)

    LOG.info('Total of %s sightings returned', len(sightings))
    LOG.info('%s already seen previously', len(already_seen_this_run))
    LOG.info('%s filtered out', len(filtered_out_this_run))
    LOG.info('%s to send', len(embeds))

    return embeds


@client.event
async def on_ready():
    """Runs when the bot is ready"""
    LOG.info(f'We have logged in as %s, part of %s',
             client.user, list(client.guilds))
    change_status.start()
    check_for_new_sightings_task.start()


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@tasks.loop(seconds=UPDATE_INTERVAL.seconds)
async def check_for_new_sightings_task():
    global first_run
    LOG.info("Entering check_for_new_sightings_task")
    try:
        embeds = check_for_new_sightings()

        if first_run == True:
            first_run = False
            return

        channels = list(filter(lambda channel: channel.name == CHANNEL_NAME, client.get_all_channels()))

        LOG.info("Found %s channels to send to", len(channels))

        for channel in channels:
            for embed in embeds:
                await channel.send(embed=embed)

    except:
        LOG.error("Error while checking for new sightings", exc_info=1)
