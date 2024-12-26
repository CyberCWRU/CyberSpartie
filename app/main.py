from typing import Final
import os
import sqlite3
import dbhandler
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands, Object, Interaction
from responses import get_response

load_dotenv()
DISCORD_TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
FLAG_ADD_ROLE_ID: Final[int] = int(os.getenv('FLAG_ADD_ROLE_ID'))
FLAG_ADD_CHANNEL_ID = int(os.getenv('FLAG_ADD_CHANNEL_ID'))
FLAG_SOLVE_CHANNEL_ID = int(os.getenv('FLAG_SOLVE_CHANNEL_ID'))
GUILD_ID = int(os.getenv('GUILD_ID'))
PATH_TO_DB = os.getenv('PATH_TO_DB')

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
async def Submit(interaction: Interaction, flag: str):

    con = sqlite3.connect(PATH_TO_DB)
    cursor = con.cursor()

    challenge_id = dbhandler.query_solve(cursor, con, flag)

    if challenge_id is not None:
        user_id = str(interaction.user.id)
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
async def Add(interaction: Interaction, flag: str, challenge_id: str):

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
async def Remove(interaction: Interaction, challenge_id: str):

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
async def AddChallenge(interaction: Interaction, challenge_id: str, challenge_name: str):

    if await auth_member(interaction):
        con = sqlite3.connect(PATH_TO_DB)
        cursor = con.cursor()
        dbhandler.create_challenge(cursor, con, challenge_id, challenge_name, "", "") # I SET CATEGORY AND DESC BLANK FOR TESTING, CHANGE LATER
        con.close()
        await interaction.response.send_message("Successfully created the CTF challenge!", ephemeral=True)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)

async def auth_member(interaction: Interaction):
    user = interaction.user
    roles = user.roles
    if client.get_guild(GUILD_ID).get_role(FLAG_ADD_ROLE_ID) not in user.roles:
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
    elif interaction.channel_id != FLAG_ADD_CHANNEL_ID:
        await interaction.response.send_message("You cannot run this command in this channel!", ephemeral=True)
    else:
        return True
    return False

@client.event
async def on_ready() -> None:
    await tree.sync(guild=Object(id=GUILD_ID))
    print(f'CyberSpartie is running!')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    await send_message(message, user_message)

def main() -> None:
    client.run(token=DISCORD_TOKEN)

if __name__ == '__main__':
    dbhandler.intitialize_table(PATH_TO_DB)
    main()
