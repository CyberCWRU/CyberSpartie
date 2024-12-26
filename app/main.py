# Imports
from typing import Final
import os
import sqlite3
import dbhandler
import logging
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands, Object, Interaction
from responses import get_response


# Loading the .env file
load_dotenv()
DISCORD_TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
FLAG_ADD_ROLE_ID: Final[int] = int(os.getenv('FLAG_ADD_ROLE_ID'))
FLAG_ADD_CHANNEL_ID: Final[int] = int(os.getenv('FLAG_ADD_CHANNEL_ID'))
FLAG_SOLVE_CHANNEL_ID: Final[int] = int(os.getenv('FLAG_SOLVE_CHANNEL_ID'))
GUILD_ID: Final[int] = int(os.getenv('GUILD_ID'))
PATH_TO_DB: Final[str] = os.getenv('PATH_TO_DB')


# Set up the logger
log_file = os.path.join('logs', 'bot.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='(%(asctime)s) [%(levelname)s] %(message)s'
)


# Setting up some global variables
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name = 'submit-flag',
    description= 'Submit a flag to CyberSpartie',
    guild=Object(id=GUILD_ID)
)
@app_commands.describe(flag="The flag to submit")
async def submit_flag(interaction: Interaction, flag: str) -> None:
    '''A function for the slash command to submit a flag

    Args:
        interaction: the interaction object passed by the discord API when the slash command is invoked
        flag: the submitted flag
    '''

    con = sqlite3.connect(PATH_TO_DB)
    cursor = con.cursor()

    challenge_id = dbhandler.query_solve(cursor, con, flag)

    # Check if the flag is valid
    if challenge_id is not None:
        user_id = str(interaction.user.id)

        # Check if the user has already submitted this flag
        if dbhandler.add_solve(cursor, con, challenge_id, user_id):
            await interaction.response.send_message("Flag successfully submitted!", ephemeral=True)
            channel = client.get_channel(FLAG_SOLVE_CHANNEL_ID)
            await channel.send(f"{interaction.user.mention} has solved `{dbhandler.get_challenge_name(cursor, con, challenge_id)}`!")
        else:
            await interaction.response.send_message("You have already submitted this flag!", ephemeral=True)
    else:
        await interaction.response.send_message("Sorry! Invalid Flag!", ephemeral=True)


@tree.command(
    name = 'add-flag',
    description= 'Add a CyberCWRU CTF flag',
    guild=Object(id=GUILD_ID)
)
@app_commands.describe(flag="The flag to add", challenge_id="The ID of the CTF challenge")
async def add_flag(interaction: Interaction, flag: str, challenge_id: str) -> None:
    '''A function for the slash command to add a flag for a challenge

    Args:
        interaction: the interaction object passed by the discord API when the slash command is invoked
        flag: the flag to set for the challenge
        challenge_id: the ID of the challenge to add a flag to
    '''

    # Check if the user has the necessary permissions and is in the right channel
    if await auth_member(interaction):
        con = sqlite3.connect(PATH_TO_DB)
        cursor = con.cursor()

        if (name := dbhandler.get_challenge_name(cursor, con, challenge_id)) is not None:
            dbhandler.add_flag(cursor, con, flag, challenge_id)
            await interaction.response.send_message(f"Successfully added the flag for `{name}`!", ephemeral=True)
        else:
            await interaction.response.send_message(f"You need to create a challenge with this ID first!", ephemeral=True)

        con.close()


@tree.command(
    name = 'remove-flag',
    description= 'Remove a CyberCWRU CTF flag',
    guild=Object(id=GUILD_ID)
)
@app_commands.describe(challenge_id="The ID of the CTF challenge")
async def remove_flags(interaction: Interaction, challenge_id: str):
    '''A function for the slash command to remove all flags from a challenge

    Args:
        interaction: the interaction object passed by the discord API when the slash command is invoked
        challenge_id: the ID of the challenge to remove flags from
    '''

    # Check if the user has the necessary permissions and is in the right channel
    if await auth_member(interaction):
        con = sqlite3.connect(PATH_TO_DB)
        cursor = con.cursor()
        dbhandler.remove_flag(cursor, con, challenge_id)
        con.close()
        await interaction.response.send_message("Successfully removed the Flag!", ephemeral=True)


@tree.command(
    name = 'create-challenge',
    description= 'Create a CyberCWRU CTF challenge',
    guild=Object(id=GUILD_ID)
)
@app_commands.describe(challenge_id="The ID of the CTF challenge", challenge_name="The name of the CTF challenge")
async def add_challenge(interaction: Interaction, challenge_id: str, challenge_name: str) -> None:
    '''A function for the slash command to add a new CTF challenge

    Args:
        interaction: the interaction object passed by the discord API when the slash command is invoked
        challenge_id: the ID of the new challenge
        challenge_name: the name of the new challenge
    '''

    # Check if the user has the necessary permissions and is in the right channel
    if await auth_member(interaction):
        con = sqlite3.connect(PATH_TO_DB)
        cursor = con.cursor()
        dbhandler.create_challenge(cursor, con, challenge_id, challenge_name, "", "") # The category and description attributes will be implemented later
        con.close()
        await interaction.response.send_message("Successfully created the CTF challenge!", ephemeral=True)


async def send_message(message: Message, user_message: str) -> None:
    '''A function to handle sending messages (as of right now, we don't use this)

    Args:
        message: the user message object the bot is responding to
        user_message: the string content of the user message
    '''
    if not user_message:
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        logging.error(str(e))


async def auth_member(interaction: Interaction) -> bool:
    '''A function that authenticates a member for certain slash commands, and responds to them appropriately if unauthenticated

    Args:
        interaction: the interaction object passed by the discord API when the authenticating slash command is invoked

    Returns:
        True if the user is allowed to run the command, False otherwise
    '''
    user = interaction.user
    roles = user.roles

    # Check if the user has the required role to execute the slash commands
    if client.get_guild(GUILD_ID).get_role(FLAG_ADD_ROLE_ID) not in user.roles:
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)

    # Check if the user is in the right channel
    elif interaction.channel_id != FLAG_ADD_CHANNEL_ID:
        await interaction.response.send_message("You cannot run this command in this channel!", ephemeral=True)

    else:
        return True

    return False


@client.event
async def on_ready() -> None:
    '''A function that sets up the command tree and indicates the bot is active'''

    await tree.sync(guild=Object(id=GUILD_ID))
    logging.info(f'CyberSpartie is running!')


@client.event
async def on_message(message: Message) -> None:
    '''A function that handles incoming messages

    Args:
        message: the message object of the incoming message
    '''

    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    await send_message(message, user_message)


def main() -> None:
    '''The main function that runs the bot'''

    client.run(token=DISCORD_TOKEN)


if __name__ == '__main__':

    try:
        dbhandler.intitialize_table(PATH_TO_DB)
        main()

    except Exception as e:
        logging.error(str(e))
