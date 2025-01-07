# CyberSpartie - CyberCWRU's CTF Submission Bot

## Setup

To set up CyberSpartie, you need to set up a .env file and connect to an existing sqlite database. Here is a step-by-step guide:

1. First, clone this repository using the following command:
	`git clone https://github.com/CyberCWRU/CyberSpartie.git`
2. Install the dependencies using `pip install -r requirements.txt`
3. In the `app` directory, create a file called `.env`
4. Add the following boilerplate to `app/.env`:
    ```env
    DISCORD_TOKEN = <The bot discord token here>
    FLAG_ADD_ROLE_ID = <The ID of the role authorized to create challenges and flags here>
    FLAG_ADD_CHANNEL_ID = <The channel ID where flags and challenges can be added here>
    FLAG_SOLVE_CHANNEL_ID = <The channel ID where solves for CTF challenges are announced here>
    GUILD_ID = <The ID of the discord server here>
    PATH_TO_DB= <The path to your EMPTY sqlite database here>
    ```
5. Fill in the boilerplate, replacing the \<bracket text> with the descriptions contained within them (remove the <brackets> too)
6. Run `app/main.py` to start the bot and you're done!

## License

This project is licensed to CyberCWRU under the [MIT License](LICENSE.md). It was originally created by [Kavin Muthuselvan](https://github.com/Lycanthropy3301)
