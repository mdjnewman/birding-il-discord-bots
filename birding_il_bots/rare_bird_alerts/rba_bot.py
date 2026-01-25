import logging
from datetime import datetime
from itertools import cycle
from datetime import timedelta

import discord
import requests
from discord.ext import tasks

from ..secret_provider import get_current_version_of_text_secret
from .filtered_species_provider import get_filtered_species
from .servers import server_configs, filtered_species_filenames

LOG = logging.getLogger(__name__)

CHANNEL_NAME = "ebird-alerts"

# Replace YOUR_EBIRD_API_KEY with your eBird API key
EBIRD_API_KEY = get_current_version_of_text_secret("ebird-api-key")

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


def check_for_new_sightings(region_code: str,  filtered_species: set[str]):
    """Fetch and process new bird sightings"""
    # Step 1: Fetch notable bird sightings from the eBird API
    response = requests.get(
        f'https://api.ebird.org/v2/data/obs/{region_code}/recent/notable?back=1&detail=full', headers={'X-eBirdApiToken': EBIRD_API_KEY})
    response.raise_for_status()
    sightings = response.json()

    embeds = []
    already_seen_this_run = []
    filtered_out_this_run = []

    for new_sighting in sightings:
        # Create a unique ID for the sighting using species code, county, and observation date
        new_sighting_id = new_sighting['speciesCode'] + \
            new_sighting['subnational2Name'] + new_sighting['subnational1Code'] + new_sighting['obsDt'][:10]

        if new_sighting_id in old_sightings:
            already_seen_this_run.append(new_sighting_id)
            continue

        comName = new_sighting['comName'].split(
            '(')[0].strip()  # Remove characters after "("

        # Check if the species is not in the filtered list
        if comName in filtered_species:
            filtered_out_this_run.append(new_sighting_id)
            continue

        old_sightings.append(new_sighting_id)

        if len(old_sightings) > 1000:
            old_sightings.pop(0)

        embed = create_sighting_embed(new_sighting)

        LOG.debug("Adding embed %s", embed)
        embeds.append(embed)

    LOG.info('%s: Total of %s sightings returned', region_code, len(sightings))
    LOG.info('%s: %s already seen previously', region_code, len(already_seen_this_run))
    LOG.info('%s: %s filtered out', region_code, len(filtered_out_this_run))
    LOG.info('%s: %s to send', region_code, len(embeds))

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

    regions = set(map(lambda server_conf: server_conf.region, server_configs))
    filtered_species = dict(map(lambda region: (region, get_filtered_species(filtered_species_filenames[region])), regions))

    try:
        sightings = dict(map(lambda region: (region, check_for_new_sightings(region, filtered_species[region])), regions))

    except:
        LOG.error("Error while checking for new sightings", exc_info=1)
        return

    if first_run == True:
        LOG.info("Skipping sending this time")
        first_run = False
        return

    for server_conf in server_configs:

        embeds = sightings[server_conf.region]

        channels = list(filter(lambda channel: channel.name == server_conf.alerts_channel and channel.guild.id == server_conf.server_id, client.get_all_channels()))

        for channel in channels:
            try:
                for embed in embeds:
                    await channel.send(embed=embed)
            except:
                LOG.error(f"Error while sending to {channel.guild.id}", exc_info=1)
