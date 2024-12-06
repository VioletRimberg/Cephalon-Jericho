# Cephalon Jericho - Your Warframe Guild Discord Bot

<div align="center">
  <img src="./images/Jericho480.png" alt="Cephalon Jericho Logo">
</div>

Utilize an authorization tool for guild members, multiple tools for admins and functionalities for users. This bot was initially written for the Golden Tenno Clan, but can easily be adjusted to be used for your clan as well.

## Installation

Cephalon Jericho utilizes [Docker](https://docs.docker.com/get-docker/), for easy set up with minimal configuration. `docker-compose` is recommended, and an exemplary config can be found [here](./docker-compose.yaml).

### Run it with Docker Compose
1. Start the bot using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Stop the bot:
    ```
    docker-compose down
    ```

## Core Functionalities

While Cephalon Jericho offers a few [commands](./docs.md), its core functionality lies in being able to link a warframe users masteraccount (the pc account) to their discord user name, assigning a role tied to it and further guild specific utilities, such as an absence form and for moderators/administration an archival form. This also includes a slimmed down riven functionality, which is based on the work done in [44bananas riven excel](https://docs.google.com/spreadsheets/d/1zbaeJBuBn44cbVKzJins_E3hTDpnmvOk8heYN-G8yy8/edit?gid=1687910063#gid=1687910063).

## Settings and Environment

| Environment Variable      | Description                  | Example Value          |
|---------------------|------------------------------|------------------------|
| `DISCORD_TOKEN`     | Your bot's Discord token     | `YOUR_DISCORD_TOKEN`   |
| `GUILD_ID`          | The ID of your Discord guild | `YOUR_GUILD_ID`        |
| `CLAN_NAME`         | Your Warframe clan's name   | `YOUR_GUILD_NAME`         |
| `REPORT_CHANNEL_ID` | Channel ID for bot reports   | `YOUR_CHANNEL_ID`      |
| `MEMBER_ROLE_ID`    | Role ID for guild members    | `YOUR_MEMBER_ROLE_ID`  |
| `GUEST_ROLE_ID`     | Role ID for guest members    | `YOUR_GUEST_ROLE_ID`   |
| `MAINTENANCE_ROLE_ID`     | Role ID for maintenance users    | `YOUR_MAINTENANCE_ROLE_ID`   |
| `MESSAGE_PROVIDER_URL`     | URL for the message provider, defaults to [jericho_text](https://docs.google.com/spreadsheets/d/1iIcJkWBY898qGPhkQ3GcLlj1KOkgjlWxWkmiHkzDuzk/edit)   | `YOUR_MESSAGE_PROVIDER_URL`   |
