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
    "Acadian Flycatcher",
    "Alder Flycatcher",
    "American Avocet",
    "American Bittern",
    "American Black Duck",
    "American Coot",
    "American Crow",
    "American Golden-Plover",
    "American Goldfinch",
    "American Kestrel",
    "American Pipit",
    "American Redstart",
    "American Robin",
    "American Tree Sparrow",
    "American White Pelican",
    "American Wigeon x Mallard",
    "American Wigeon",
    "American Woodcock",
    "Baird's Sandpiper",
    "Bald Eagle",
    "Baltimore Oriole",
    "Bank Swallow",
    "Barn Swallow",
    "Barred Owl",
    "Bay-breasted Warbler",
    "Bell's Vireo",
    "Belted Kingfisher",
    "Black Scoter",
    "Black Tern",
    "Black-and-white Warbler",
    "Black-bellied Plover",
    "Black-billed Cuckoo",
    "Black-capped Chickadee",
    "Black-crowned Night-Heron",
    "Black-necked Stilt",
    "Black-throated Blue Warbler",
    "Black-throated Green Warbler",
    "Blackburnian Warbler",
    "Blackpoll Warbler",
    "Blue Grosbeak",
    "Blue Jay",
    "Blue-gray Gnatcatcher",
    "Blue-headed Vireo",
    "Blue-winged Teal",
    "Blue-winged Teal x Northern Shoveler",
    "Blue-winged Warbler",
    "Bobolink",
    "Bonaparte's Gull",
    "Brewer's Blackbird",
    "Brewster's Warbler",
    "Broad-winged Hawk",
    "Brown Creeper",
    "Brown Thrasher",
    "Brown-headed Cowbird",
    "Buff-breasted Sandpiper",
    "Bufflehead",
    "Cackling Goose",
    "Canada Goose",
    "Canada Warbler",
    "Canvasback",
    "Cape May Warbler",
    "Carolina Chickadee",
    "Carolina Wren",
    "Caspian Tern",
    "Cattle Egret",
    "Cedar Waxwing",
    "Chestnut-sided Warbler",
    "Chimney Swift",
    "Chipping Sparrow",
    "Chuck-will's-widow",
    "Clay-colored Sparrow",
    "Cliff Swallow",
    "Common Gallinule",
    "Common Goldeneye",
    "Common Grackle",
    "Common Loon",
    "Common Merganser",
    "Common Nighthawk",
    "Common Redpoll",
    "Common Tern",
    "Common Yellowthroat",
    "Connecticut Warbler",
    "Cooper's Hawk",
    "Dark-eyed Junco",
    "Dickcissel",
    "Domestic goose sp. x Canada Goose",
    "Double-crested Cormorant",
    "Downy Woodpecker",
    "Dunlin",
    "Eastern Bluebird",
    "Eastern Kingbird",
    "Eastern Meadowlark",
    "Eastern Phoebe",
    "Eastern Screech-Owl",
    "Eastern Towhee",
    "Eastern Whip-poor-will",
    "Eastern Wood-Pewee",
    "Eurasian Collared-Dove",
    "European Starling",
    "Field Sparrow",
    "Forster's Tern",
    "Fox Sparrow",
    "Franklin's Gull",
    "Gadwall",
    "Glaucous Gull",
    "Golden-crowned Kinglet",
    "Golden-winged Warbler",
    "Golden-winged x Blue-winged Warbler",
    "Grasshopper Sparrow",
    "Gray Catbird",
    "Gray-cheeked Thrush",
    "Graylag x Canada Goose",
    "Great Black-backed Gull",
    "Great Blue Heron",
    "Great Crested Flycatcher",
    "Great Egret",
    "Great Horned Owl",
    "Greater Prairie-Chicken",
    "Greater Scaup",
    "Greater White-fronted Goose",
    "Greater White-fronted x Canada Goose",
    "Greater Yellowlegs",
    "Green Heron",
    "Green-winged Teal",
    "Hairy Woodpecker",
    "Henslow's Sparrow",
    "Hermit Thrush",
    "Herring Gull",
    "Hooded Merganser",
    "Hooded Warbler",
    "Horned Grebe",
    "Horned Lark",
    "House Finch",
    "House Sparrow",
    "House Wren",
    "Iceland Gull",
    "Indigo Bunting",
    "Kentucky Warbler",
    "Killdeer",
    "Lapland Longspur",
    "Lark Sparrow",
    "Lawrence's Warbler",
    "LeConte's Sparrow",
    "Least Bittern",
    "Least Flycatcher",
    "Least Sandpiper",
    "Lesser Black-backed Gull",
    "Lesser Scaup",
    "Lesser Yellowlegs",
    "Lincoln's Sparrow",
    "Little Blue Heron",
    "Long-billed Dowitcher",
    "Long-eared Owl",
    "Long-tailed Duck",
    "Louisiana Waterthrush",
    "Magnolia Warbler",
    "Mallard x American Black Duck",
    "Mallard x Northern Pintail",
    "Mallard",
    "Marsh Wren",
    "Merlin",
    "Monk Parakeet",
    "Mourning Dove",
    "Mourning Warbler",
    "Mute Swan",
    "Nashville Warbler",
    "Northern Bobwhite",
    "Northern Cardinal",
    "Northern Flicker",
    "Northern Harrier",
    "Northern Mockingbird",
    "Northern Parula",
    "Northern Pintail",
    "Northern Rough-winged Swallow",
    "Northern Saw-whet Owl",
    "Northern Shoveler",
    "Northern Waterthrush",
    "Olive-sided Flycatcher",
    "Orange-crowned Warbler",
    "Orchard Oriole",
    "Osprey",
    "Ovenbird",
    "Palm Warbler",
    "Pectoral Sandpiper",
    "Peregrine Falcon",
    "Philadelphia Vireo",
    "Pied-billed Grebe",
    "Pileated Woodpecker",
    "Pine Siskin",
    "Pine Warbler",
    "Piping Plover",
    "Prairie Warbler",
    "Prothonotary Warbler",
    "Purple Finch",
    "Purple Martin",
    "Red-bellied Woodpecker",
    "Red-breasted Merganser",
    "Red-breasted Nuthatch",
    "Red-eyed Vireo",
    "Red-headed Woodpecker",
    "Red-necked Phalarope",
    "Red-shouldered Hawk",
    "Red-tailed Hawk",
    "Red-winged Blackbird",
    "Redhead",
    "Ring-billed Gull",
    "Ring-necked Duck",
    "Ring-necked Pheasant",
    "Rock Pigeon",
    "Rose-breasted Grosbeak",
    "Ross's Goose",
    "Rough-legged Hawk",
    "Ruby-crowned Kinglet",
    "Ruby-throated Hummingbird",
    "Ruddy Duck",
    "Ruddy Turnstone",
    "Rusty Blackbird",
    "Sanderling",
    "Sandhill Crane",
    "Savannah Sparrow",
    "Scarlet Tanager",
    "Sedge Wren",
    "Semipalmated Plover",
    "Semipalmated Sandpiper",
    "Sharp-shinned Hawk",
    "Short-billed Dowitcher",
    "Short-eared Owl",
    "Snow Bunting",
    "Snow Goose",
    "Snow x Ross's Goose",
    "Snowy Egret",
    "Solitary Sandpiper",
    "Song Sparrow",
    "Sora",
    "Spotted Sandpiper",
    "Stilt Sandpiper",
    "Summer Tanager",
    "Surf Scoter",
    "Swainson's Thrush",
    "Swamp Sparrow",
    "Swan Goose x Canada Goose",
    "Tennessee Warbler",
    "Tree Swallow",
    "Trumpeter Swan",
    "Tufted Titmouse",
    "Tundra Swan",
    "Turkey Vulture",
    "Upland Sandpiper",
    "Veery",
    "Vesper Sparrow",
    "Virginia Rail",
    "Warbling Vireo",
    "White-breasted Nuthatch",
    "White-crowned Sparrow",
    "White-eyed Vireo",
    "White-rumped Sandpiper",
    "White-throated Sparrow",
    "White-winged Scoter",
    "Wild Turkey",
    "Willet",
    "Willow Flycatcher",
    "Wilson's Phalarope",
    "Wilson's Snipe",
    "Wilson's Warbler",
    "Winter Wren",
    "Wood Duck",
    "Wood Thrush",
    "Yellow Warbler",
    "Yellow-bellied Flycatcher",
    "Yellow-bellied Sapsucker",
    "Yellow-billed Cuckoo",
    "Yellow-breasted Chat",
    "Yellow-crowned Night-Heron",
    "Yellow-rumped Warbler",
    "Yellow-throated Vireo",
    "Yellow-throated Warbler",
}

# Replace YOUR_DISCORD_CHANNEL_ID with the ID of the channel where you want to send messages
DISCORD_CHANNEL_ID = '1136054663674867912' # ebird-alerts in Birding IL
# DISCORD_CHANNEL_ID = '1224892992037458021'  # ebird-rarities in test server

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

    # Get the current time in UTC timezone
    current_time_utc = datetime.utcnow()

    # Set the timezone to Eastern Time (US & Canada)
    eastern_timezone = pytz.timezone('US/Eastern')

    # Convert current_time_utc to Eastern Time
    current_time = current_time_utc.astimezone(eastern_timezone)

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
        if comName in filtered_species:
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

        # Send the embed message to Discord channel
        channel = (client.get_channel(DISCORD_CHANNEL_ID) or await client.fetch_channel(DISCORD_CHANNEL_ID))

        if first_run == True:
            first_run = False
            return

        for embed in embeds:
            await channel.send(embed=embed)

    except:
        LOG.error("Error while checking for new sightings", exc_info=1)
