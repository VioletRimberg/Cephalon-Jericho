# Cephalon Jericho - Your Warframe Guild Discord Bot

<div style="text-align: center;">
  <img src="./images/jericho480.png" alt="Cephalon Jericho Logo">
</div>

Cephalon Jericho is a Discord bot for managing Warframe guilds. It offers features such as user authorization, member role management, and more, helping guild admins streamline their server administration while engaging users.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Contributing](#contributing)
- [License](#license)

## Installation

To get started with Cephalon Jericho, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/cephalon-jericho.git
    cd cephalon-jericho
    ```

2. **Set up Docker** (optional, but recommended):
    ```bash
    docker build -t cephalon-jericho .
    docker run -d --name jericho-bot -p 3000:3000 --env-file .env cephalon-jericho
    ```

3. **Configure environment variables**:
    Copy the `.env.example` file to `.env` and replace the placeholders with your own values:
    ```bash
    cp .env.example .env
    ```
    Fill in the required fields:
    - `DISCORD_TOKEN`
    - `GUILD_ID`
    - `CLAN_NAME`
    - `REPORT_CHANNEL_ID`
    - `MEMBER_ROLE_ID`
    - `GUEST_ROLE_ID`

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

## Usage

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

## Contributing

We welcome contributions to Cephalon Jericho! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to your fork (`git push origin feature-branch`)
6. Create a new Pull Request

## License

Cephalon Jericho is licensed under the [MIT License](LICENSE).