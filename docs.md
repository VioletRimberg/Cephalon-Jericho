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

3. **Rivens**:
     
     To find details about what stats one should aim for with a riven, users can search a weapon with `/riven_weapon_stats` which offers suggested weapons while typing. With the `/riven_grade` command a user can first enter a weapon and then stats to recieve a corresponding grade from 5. `/riven_help` provides explanations to stat abriviations, the weapon stats and the way jericho grades rivens. Grading is done based on the work of [44bananas](https://docs.google.com/spreadsheets/d/1zbaeJBuBn44cbVKzJins_E3hTDpnmvOk8heYN-G8yy8/edit?gid=1687910063#gid=1687910063). For grading, the variation in attributes is not considered.
     The 5 grades by which Jericho grades:
    *Perfect*
        A perfect riven has at least one of the best stats for the weapon and the rest are either best or desired stats, with a harmless negative. This is what you would often consider a god roll, so count yourself lucky Operator, if you find a roll such as this.

    *Prestigious*
        A prestigious riven is a roll that just barely isn't a god roll by traditional standards. It only has desired or best stats and may or may not have a harmless or non detrimental negative, with no irrelevant stat on it. These are rivens that will evelate whatever build you put it in and push a weapon to levels that could only be bested by a god roll. 

    *Decent*
        A decent riven has at least one best or desired stat, the rest may be stats that are not in that category for the weapon and it may have either a harmless or non detrimental negative or no negative at all. This is still a good roll that can fit many builds. Hah, you could say it is decent, Operator.

    *Neutral*
        A neutral riven has no desired or best stats, but also no harmful negative. They may be useful for a niche build, or for your build in particular, but the majority of the times you want to roll this riven some more. 

    *Unuseable*
        An unusuable riven has a harmful negative - simpel as that. Harmful is any negative that would be a desired or best stat if it wasn't the negative and therefore ruins many builds. You'd be adviced to reroll such a riven, unless you have a specific use for it in mind.

4. **Other User features**: 
    
    For engagement, Cephalon Jericho offers a simple `/hello` function, as well as a Koumei-inspired dice roller with `/koumei`. For usage of the Warframe API, users can query Warframe profiles with `/profile` as well, which also reports if a user is part of Golden Tenno. Upon popular request, users can interact with Jericho outside of the `/judge_jericho` function with `/smooch` to give their favorite Cephalon a little kiss.

5. **Admin features**:
    
     `/archive` pulls up a modal that allows you to enter a title and report summary, which is then pushed into a corresponding report channel defined with the `REPORT_CHANNEL_ID` in the `.env` file. With `/text_maintenance` and `/riven_maintenance` users with the corresponding maintenance role can refresh the CSVs made from the google sheets.

6. **Logging**:
    
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
- `/maintenance_text`: Allows users with the maintenance role to refresh currently loaded google sheet for text lines
-`/maintenance_sync_commands`: Allows users with the maintenance role to refresh currently loaded commands to remove duplicats and re-add missing commands while server is live.
- `/maintenance_riven`: Allows users with the maintenance role to refresh the currently loaded google sheet for rivens
- `/riven_weapon_stats`: An autosuggesting weapon query for best, desired and harmless negative stats corresponding to the weapon
- `/riven_grade`: Grades a riven based on provided weapon and stats by scores based on 5 overall grades. This is solely based on attributes, and not the individual attribute variation roll. 
- `/tough_love`: A social command providing harsh, but true advice.
- `/feeling_lost`: A social command meant to cheer up and motivate.
- `/trivia`: A social command providing a random fact about warframe.
- `/rate_outfit`: A social command asking Jericho to rate your current outfit.

## License

Cephalon Jericho is licensed under the [MIT License](LICENSE).