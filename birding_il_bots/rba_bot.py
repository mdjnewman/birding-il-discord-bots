import logging
from datetime import datetime
from itertools import cycle
from datetime import timedelta

import discord
import pytz
import requests
from discord.ext import tasks

from .secret_provider import get_current_version_of_text_secret

LOG = logging.getLogger(__name__)

filtered_species = {
    "Snow Goose",
    "Ross’s Goose"
    "Greater White-fronted Goose",
    "Cackling Goose",
    "Canada Goose",
    "Mute Swan",
    "Trumpeter Swan",
    "Tundra Swan",
    "Wood Duck",
    "Blue-winged Teal",
    "Northern Shoveler",
    "Gadwall",
    "American Wigeon",
    "Mallard",
    "American Black Duck",
    "Northern Pintail",
    "Green-winged Teal",
    "Canvasback",
    "Redhead",
    "Ring-necked Duck",
    "Greater Scaup",
    "Lesser Scaup",
    "Surf Scoter",
    "White-winged Scoter",
    "Black Scoter",
    "Long-tailed Duck",
    "Bufflehead",
    "Common Goldeneye",
    "Hooded Merganser",
    "Common Merganser",
    "Red-breasted Merganser",
    "Ruddy Duck",
    "Northern Bobwhite",
    "Wild Turkey",
    "Greater Prairie-Chicken",
    "Ring-necked Pheasant",
    "Pied-billed Grebe",
    "Horned Grebe",
    "Rock Pigeon",
    "Eurasian Collared-Dove",
    "Mourning Dove",
    "Yellow-billed Cuckoo",
    "Black-billed Cuckoo",
    "Common Nighthawk",
    "Chuck-will’s-widow",
    "Eastern Whip-poor-will",
    "Chimney Swift",
    "Ruby-throated Hummingbird",
    "Virginia Rail",
    "Sora",
    "Common Gallinule",
    "American Coot",
    "Sandhill Crane",
    "Black-necked Stilt",
    "American Avocet",
    "Black-bellied Plover",
    "American Golden-Plover",
    "Killdeer",
    "Semipalmated Plover",
    "Piping Plover",
    "Upland Sandpiper",
    "Ruddy Turnstone",
    "Stilt Sandpiper",
    "Sanderling",
    "Dunlin",
    "Baird’s Sandpiper",
    "Least Sandpiper",
    "White-rumped Sandpiper",
    "Buff-breasted Sandpiper",
    "Pectoral Sandpiper",
    "Semipalmated Sandpiper",
    "Short-billed Dowitcher",
    "Long-billed Dowitcher",
    "American Woodcock",
    "Wilson’s Snipe",
    "Spotted Sandpiper",
    "Solitary Sandpiper",
    "Lesser Yellowlegs",
    "Willet",
    "Greater Yellowlegs",
    "Wilson’s Phalarope",
    "Red-necked Phalarope",
    "Bonaparte’s Gull",
    "Franklin’s Gull",
    "Ring-billed Gull",
    "Herring Gull",
    "Iceland Gull",
    "Lesser Black-backed Gull",
    "Glaucous Gull",
    "Great Black-backed Gull",
    "Caspian Tern",
    "Black Tern",
    "Common Tern",
    "Forster’s Tern",
    "Common Loon",
    "Double-crested Cormorant",
    "American White Pelican",
    "American Bittern",
    "Least Bittern",
    "Great Blue Heron",
    "Great Egret",
    "Snowy Egret",
    "Little Blue Heron",
    "Cattle Egret",
    "Green Heron",
    "Black-crowned Night-Heron",
    "Yellow-crowned Night-Heron",
    "Turkey Vulture",
    "Osprey",
    "Northern Harrier",
    "Sharp-shinned Hawk",
    "Cooper’s Hawk",
    "Bald Eagle",
    "Red-shouldered Hawk",
    "Broad-winged Hawk",
    "Red-tailed Hawk",
    "Rough-legged Hawk",
    "Eastern Screech-Owl",
    "Great Horned Owl",
    "Barred Owl",
    "Long-eared Owl",
    "Short-eared Owl",
    "Northern Saw-whet Owl",
    "Belted Kingfisher",
    "Red-headed Woodpecker",
    "Red-bellied Woodpecker",
    "Yellow-bellied Sapsucker",
    "Downy Woodpecker",
    "Hairy Woodpecker",
    "Northern Flicker",
    "Pileated Woodpecker",
    "American Kestrel",
    "Merlin",
    "Peregrine Falcon",
    "Monk Parakeet",
    "Great Crested Flycatcher",
    "Eastern Kingbird",
    "Olive-sided Flycatcher",
    "Eastern Wood-Pewee",
    "Yellow-bellied Flycatcher",
    "Acadian Flycatcher",
    "Alder Flycatcher",
    "Willow Flycatcher",
    "Least Flycatcher",
    "Eastern Phoebe",
    "White-eyed Vireo",
    "Bell’s Vireo",
    "Yellow-throated Vireo",
    "Blue-headed Vireo",
    "Philadelphia Vireo",
    "Warbling Vireo",
    "Red-eyed Vireo",
    "Blue Jay",
    "American Crow",
    "Carolina Chickadee",
    "Black-capped Chickadee",
    "Tufted Titmouse",
    "Horned Lark",
    "Bank Swallow",
    "Tree Swallow",
    "Northern Rough-winged Swallow",
    "Purple Martin",
    "Barn Swallow",
    "Cliff Swallow",
    "Ruby-crowned Kinglet",
    "Golden-crowned Kinglet",
    "Cedar Waxwing",
    "Red-breasted Nuthatch",
    "White-breasted Nuthatch",
    "Brown Creeper",
    "Blue-gray Gnatcatcher",
    "Carolina Wren",
    "House Wren ",
    "Winter Wren ",
    "Sedge Wren",
    "Marsh Wren ",
    "Gray Catbird",
    "Brown Thrasher",
    "Northern Mockingbird",
    "European Starling",
    "Eastern Bluebird",
    "Veery",
    "Gray-cheeked Thrush",
    "Swainson’s Thrush",
    "Hermit Thrush",
    "Wood Thrush",
    "American Robin",
    "House Sparrow",
    "American Pipit",
    "House Finch",
    "Purple Finch",
    "Common Redpoll",
    "Pine Siskin",
    "American Goldfinch",
    "Lapland Longspur",
    "Snow Bunting",
    "Grasshopper Sparrow",
    "Lark Sparrow",
    "Chipping Sparrow",
    "Clay-colored Sparrow",
    "Field Sparrow",
    "Fox Sparrow",
    "American Tree Sparrow",
    "Dark-eyed Junco",
    "White-crowned Sparrow",
    "White-throated Sparrow",
    "Vesper Sparrow",
    "LeConte’s Sparrow",
    "Henslow’s Sparrow",
    "Savannah Sparrow",
    "Song Sparrow",
    "Lincoln’s Sparrow",
    "Swamp Sparrow",
    "Eastern Towhee",
    "Yellow-breasted Chat",
    "Bobolink",
    "Eastern Meadowlark",
    "Orchard Oriole",
    "Baltimore Oriole",
    "Red-winged Blackbird",
    "Brown-headed Cowbird",
    "Rusty Blackbird",
    "Brewer’s Blackbird",
    "Common Grackle",
    "Ovenbird",
    "Louisiana Waterthrush",
    "Northern Waterthrush",
    "Golden-winged Warbler",
    "Blue-winged Warbler",
    "Black-and-white Warbler",
    "Prothonotary Warbler",
    "Tennessee Warbler",
    "Orange-crowned Warbler",
    "Nashville Warbler",
    "Connecticut Warbler",
    "Mourning Warbler",
    "Kentucky Warbler",
    "Common Yellowthroat",
    "Hooded Warbler",
    "American Redstart",
    "Cape May Warbler",
    "Northern Parula",
    "Magnolia Warbler",
    "Bay-breasted Warbler",
    "Blackburnian Warbler",
    "Yellow Warbler",
    "Chestnut-sided Warbler",
    "Blackpoll Warbler",
    "Black-throated Blue Warbler",
    "Palm Warbler",
    "Pine Warbler",
    "Yellow-rumped Warbler",
    "Yellow-throated Warbler",
    "Prairie Warbler",
    "Black-throated Green Warbler",
    "Canada Warbler",
    "Wilson’s Warbler",
    "Summer Tanager",
    "Scarlet Tanager",
    "Northern Cardinal",
    "Rose-breasted Grosbeak",
    "Blue Grosbeak",
    "Indigo Bunting",
    "Dickcissel"
}

# Replace YOUR_DISCORD_CHANNEL_ID with the ID of the channel where you want to send messages
# DISCORD_CHANNEL_ID = '1136054663674867912' # ebird-alerts in Birding IL
DISCORD_CHANNEL_ID = '1224892992037458021'  # ebird-rarities in test server

# Replace YOUR_EBIRD_API_KEY with your eBird API key
EBIRD_API_KEY = get_current_version_of_text_secret("ebird-api-key")

# Illinois Region Code for eBird API
IL_REGION_CODE = 'US-IL'

UPDATE_INTERVAL = timedelta(hours=1)

# Initialize the Discord client
intents = discord.Intents.none()
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


# Global variable to keep track of old sightings
old_sightings = []


def check_for_new_sightings():
    """Fetch and process new bird sightings"""
    # Step 1: Fetch notable bird sightings from the eBird API
    response = requests.get(
        f'https://api.ebird.org/v2/data/obs/{IL_REGION_CODE}/recent/notable?back=1&detail=full', headers={'X-eBirdApiToken': EBIRD_API_KEY})
    response.raise_for_status()
    sightings = response.json()

    LOG.info(f'Total of {len(sightings)} returned')

    # Get the current time in UTC timezone
    current_time_utc = datetime.utcnow()

    # Set the timezone to Eastern Time (US & Canada)
    eastern_timezone = pytz.timezone('US/Eastern')

    # Convert current_time_utc to Eastern Time
    current_time = current_time_utc.astimezone(eastern_timezone)

    embeds = []

    for new_sighting in sightings:
        # Create a unique ID for the sighting using species code, county, and observation date
        new_sighting_id = new_sighting['speciesCode'] + \
            new_sighting['subnational2Name'] + new_sighting['obsDt'][:10]

        if new_sighting_id in old_sightings:
            continue

        comName = new_sighting['comName'].split(
            '(')[0].strip()  # Remove characters after "("

        # Check if the species is not in the filtered list
        if comName in filtered_species:
            continue

        # Step 2: Fetch the checklist details to check its submission time
        checklist_url = f'https://api.ebird.org/v2/product/checklist/view/{new_sighting["subId"]}'
        checklist_response = requests.get(
            checklist_url, headers={'X-eBirdApiToken': EBIRD_API_KEY})
        checklist_response.raise_for_status()
        checklist_data = checklist_response.json()

        # Get the submission time from the checklist details
        submission_time_str = checklist_data['creationDt']

        # Convert the submission time to a datetime object and make it offset-aware (in Eastern Time)
        creation_time = eastern_timezone.localize(
            datetime.strptime(submission_time_str, '%Y-%m-%d %H:%M'))

        # Calculate the time difference between current time and submission time
        time_difference = current_time - creation_time

        # Only process the sighting if the checklist was submitted since the last run
        if time_difference.total_seconds() <= UPDATE_INTERVAL.seconds:
            old_sightings.append(new_sighting_id)

            # If the list exceeds 10000 records, remove the oldest record(s) to maintain the limit
            if len(old_sightings) > 10000:
                old_sightings.pop(0)

            # Create the message embed for the sighting
            embed = create_sighting_embed(new_sighting)

            LOG.debug("Adding embed %s", embed)
            embeds.append(embed)

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
    LOG.info("Entering check_for_new_sightings_task")
    try:
        embeds = check_for_new_sightings()

        # Send the embed message to Discord channel
        channel = (client.get_channel(DISCORD_CHANNEL_ID) or await client.fetch_channel(DISCORD_CHANNEL_ID))

        for embed in embeds:
            await channel.send(embed=embed)
    except:
        LOG.error("Error while checking for new sightings", exc_info=1)
