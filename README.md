# Cephalon Jericho - Your Warframe Guild Discord Bot

<div style="text-align: center;">
  <img src="./images/jericho480.png" alt="Cephalon Jericho Logo">
</div>

Utilize an authorization tool for guild members, multiple tools for admins and functionalities for users. This bot was initially written for the Golden Tenno Clan, but can easily be adjusted to be used for your clan as well.

## Installation

Cephalon Jericho utelizes Docker containers, for easy set up with minimal configuration. Docker-Compose is recommended.

### Prerequisites
- Docker installed on your machine ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Get Docker Compose](https://docs.docker.com/compose/install/))

### Clone the Repository
```bash
git clone https://github.com/your-username/cephalon-jericho.git
cd cephalon-jericho
```

### Run it with Docker Compose
1. Start the bot using Docker Compose:
   ```bash
   docker-compose up -d
   ```
2. Check if the bot is running:
    
    Once the bot is running, check your Discord server to ensure it's online. You can also view logs with:
         ```
         docker logs jericho-bot
         ```

3. Stop the bot:
    ```
    docker-compose down
    ```


An example configuration can be found in the `docker.compose.yml` file.

## Core Functionalities

While Cephalon Jericho offers a few commands, its core functionality lies in being able to link a warframe users masteraccount (the pc account) to their discord user name, assigning a role tied to it and further guild specific utilities, such as an absence form and for moderators/administration an archival form. 

## Settings and Environment

| Environment Variable      | Description                  | Example Value          |
|---------------------|------------------------------|------------------------|
| `DISCORD_TOKEN`     | Your bot's Discord token     | `YOUR_DISCORD_TOKEN`   |
| `GUILD_ID`          | The ID of your Discord guild | `YOUR_GUILD_ID`        |
| `CLAN_NAME`         | Your Warframe clan's name   | `YOUR_GUILD_NAME`         |
| `REPORT_CHANNEL_ID` | Channel ID for bot reports   | `YOUR_CHANNEL_ID`      |
| `MEMBER_ROLE_ID`    | Role ID for guild members    | `YOUR_MEMBER_ROLE_ID`  |
| `GUEST_ROLE_ID`     | Role ID for guest members    | `YOUR_GUEST_ROLE_ID`   |
