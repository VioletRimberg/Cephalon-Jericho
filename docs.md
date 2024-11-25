# Table of Contents

- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [License](#license)

## Configuration

Cephalon Jericho uses environment variables for configuration which are required.

| Variable Name       | Description                  | Example Value          |
|---------------------|------------------------------|------------------------|
| `DISCORD_TOKEN`     | Your bot's Discord token     | `YOUR_DISCORD_TOKEN`   |
| `GUILD_ID`          | The ID of your Discord guild | `YOUR_GUILD_ID`        |
| `CLAN_NAME`         | Your Warframe clan's name    | `YOUR_CLAN_NAME`         |
| `REPORT_CHANNEL_ID` | Channel ID for bot reports   | `YOUR_CHANNEL_ID`      |
| `MEMBER_ROLE_ID`    | Role ID for guild members    | `YOUR_MEMBER_ROLE_ID`  |
| `GUEST_ROLE_ID`     | Role ID for guest members    | `YOUR_GUEST_ROLE_ID`   |
| `MAINTENANCE_ROLE_ID`     | Role ID for maintenance users    | `YOUR_MAINTENANCE_ROLE_ID`   |
| `MESSAGE_PROVIDER_URL`     | URL for the message provider, defaults to [jericho_text](https://docs.google.com/spreadsheets/d/1iIcJkWBY898qGPhkQ3GcLlj1KOkgjlWxWkmiHkzDuzk/edit)   | `YOUR_MESSAGE_PROVIDER_URL`   |

## Usage

Once the bot is running, you can interact with it in the following ways:

1. **Command for role assign and verification**: 
   
    Use `/role` to open a modal to enter a Warframe username. It is then checked in the Warframe API if it’s part of the entered Guild Name and assigns a corresponding role. If a user is not a member, they have the option to choose a guest role. This is also logged in the backend.

2. **Absence report**:
     
     To self-report an absence to prevent kicking or to inform administration/moderators, users can fill out the form pulled up by the `/absence` command. Similar to the Admin tool `/archive`, the input is then sent to the `REPORT_CHANNEL_ID` report text channel.

3. **Other User features**: 
    
    For engagement, Cephalon Jericho offers a simple `/hello` function, as well as a Koumei-inspired dice roller with `/koumei`. For usage of the Warframe API, users can query Warframe profiles with `/profile` as well, which also reports if a user is part of Golden Tenno. Upon popular request, users can interact with Jericho outside of the `/judge_jericho` function with `/smooch` to give their favorite Cephalon a little kiss.

4. **Admin features**:
    
     `/archive` pulls up a modal that allows you to enter a title and report summary, which is then pushed into a corresponding report channel defined with the `REPORT_CHANNEL_ID` in the `.env` file.

5. **Logging**:
    
    To ensure error catching and user issues, most functionalities that require the Warframe API or cause a change in Discord/redirect messages are logged in the backend.


## Commands

The current list of commands contains the following functions:

- `/absence`: A self reporting absence form.
- `/archive`: A self-archiving form for note-taking and records.
- `/hello`: Says hello to Cephalon Jericho.
- `/judge_jericho`: Inform Cephalon Jericho on whether or whether not he was a good bot - with resulting consequences. 
- `koumei`: A simple d6 dice bot, with custom outputs for a jackpot and a snake eyes result. 
- `/profile`: A form to check warframe user data, including warframe name, mastery rank and clan.
- `/role`: Allows users to either choose member or guest roles. To verify as a member, users must enter their Warframe username, which is checked against the guild name. After verification, the corresponding role is automatically assigned. 
- `/smooch`: Allows the user to give Cephalon Jericho a little kiss. 
- `/text_maintenance`: Allows users with the maintenance role to refresh currently loaded google sheet

## License

Cephalon Jericho is licensed under the [MIT License](LICENSE).