
import logging
import re
from itertools import cycle

import discord
from discord.ext import tasks

LOG = logging.getLogger(__name__)


# Role name to be removed when a user agrees to the rules
NEW_MEMBER_ROLE_NAME = "New Member"

# Regular expression pattern to match different formats for agreeing
AGREE_PATTERN = re.compile(r'(?i)^\s*[!i]\s*agree\s*(.*)$')

# Initialize the Discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

status = cycle(['Helping Users Join', 'Assisting with Server Invites'])


@client.event
async def on_ready():
    """Runs when the bot is ready"""
    change_status.start()
    LOG.info(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    """Run when a message is sent in the server"""
    LOG.debug("Received message %s", message)
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Check if the message matches the agree pattern
    match = AGREE_PATTERN.match(message.content)
    if match:
        # Extract the name from the message
        name = match.group(1).strip()

        # Check if the name has at least a first name and a last name
        name_args = name.split(' ')
        if len(name_args) >= 2:
            first_name = name_args[0]
            # Join all elements from the 2nd position onwards
            last_name = " ".join(name_args[1:])

            # Combine the first and last names with a space in between to form the nickname
            nickname = f"{first_name} {last_name}"

            # Check if the author of the message is a member of the server
            if isinstance(message.author, discord.Member) and message.guild:
                # Remove the "new member" role
                role = discord.utils.get(
                    message.guild.roles, name=NEW_MEMBER_ROLE_NAME)
                if role in message.author.roles:
                    await message.author.remove_roles(role)

                # Set the nickname
                await message.author.edit(nick=nickname)

                # Send a confirmation message in the server as an embed
                embed = discord.Embed(
                    description=f"Nickname set to: {nickname}",
                    color=discord.Color.green()
                )
                # Invisible field separator
                embed.add_field(
                    name="\u200b", value="Role 'new member' removed", inline=False)
                await message.channel.send(embed=embed)

                # Send a direct message to the user
                dm_embed = discord.Embed(
                    title="Welcome to the Birding Illinois Server!",
                    description="Thank you for agreeing to the rules. You can select which chats you want to join in Browse Channels.",
                    color=discord.Color.green()
                )
                await message.author.send(embed=dm_embed)
        else:
            # Send an error message if the command is not in the correct format
            await message.channel.send("Please use the format: `!agree <first_name> <last_name>`")


@client.event
async def on_member_join(member):
    """Runs when a new member joins the server"""
    LOG.debug("Member joined %s", member)
    # Check if the member is a bot (we don't want to add the role to bots)
    if member.bot:
        return

    # Check if the member joined a server where the bot is present
    # TODO Not sure how this can ever happen? Should it be a comparison?
    if not member.guild:
        LOG.warn("Member %s not a member of guild", member)
        return

    # Get the "New Member" role
    role = discord.utils.get(member.guild.roles, name=NEW_MEMBER_ROLE_NAME)
    if not role:
        LOG.warn("Role %s not found, returning", NEW_MEMBER_ROLE_NAME)
        return

    # Add the "New Member" role to the new member
    await member.add_roles(role)

    # Send a welcome message in the specified channel as an embed
    welcome_channel_name = "rules"  # Replace with the name of your desired channel
    welcome_channel = discord.utils.get(
        member.guild.channels, name=welcome_channel_name)
    if welcome_channel:
        welcome_embed = discord.Embed(
            title="Welcome to the Server!",
            description="Please review the posting guidelines in #guidelines",
            color=discord.Color.blue()
        )
        welcome_embed.add_field(
            name="Joining the Server",
            value="To join this server, you must reply to this message with the following command "
            '"!agree {first name} {last name}". Please use your full first and last name - '
            "no name abbreviations/pseudonyms/etc. (e.g. !agree John Appleseed) By doing so, "
            "you agree to adhere to these guidelines. After you gain access, please select "
            "which chats you want to join in #Browse Channels.",
            inline=False
        )
        await welcome_channel.send(embed=welcome_embed)


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))
