# Admin Bot

Admin Bot is a Discord bot designed to provide administrative commands and user rank tracking for your server. It's built using Python and the discord.py library, and uses MongoDB for data storage.

## Features

- **Rank Tracking**: Admin Bot tracks user activity and assigns XP and levels based on various actions, such as sending messages, participating in voice chats, and more. Users can check their own rank or the rank of others with the `/rank` command.

- **Nickname Tracking**: Admin Bot tracks changes to user nicknames and stores this information. Admins can view a user's nickname history with the `/nicknames` command.

- **Warning System**: Admins can issue warnings to users with the `/warn` command, providing a username and a reason for the warning. All warnings are logged and can be viewed with the `/view_warnings` command.

## Installation

1. Clone this repository.
2. Install the required Python packages: `pip install -r requirements.txt`
3. Set up your MongoDB database and update the connection string in the bot's code.
4. Replace the `token` variable in the bot's code with your bot's token.
5. Run the bot: `python level_bot.py`

## Usage

Once the bot is running and has been invited to your server, you can use the following slash commands:

- `/rank [username]`: Check your rank or the rank of another user.
- `/nicknames [username]`: View all past nicknames of a user.
- `/warn username reason`: Issue a warning to a user.
- `/view_warnings username`: View all warnings issued to a user.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## Discord
https://discord.gg/CmrFZgZVEE

## License

This project is licensed under the MIT License.
