![WhereContextBot3](https://socialify.git.ci/SDeVuyst/WhereContextBot3/image?description=1&descriptionEditable=Where%20Context%3F%3F&font=Raleway&issues=1&language=1&name=1&owner=1&pattern=Solid&stargazers=1&theme=Dark)

A discord bot built for a personal server.
Built with discord.py and various api implementations.

Has audio functionality, games, automatic triggers and many other commands.

Also thanks to [kkrypt0n](https://github.com/kkrypt0nn/Python-Discord-Bot-Template) for providing a very helpful template.


## Getting Started

### Create a discord bot

Go to the (discord developer portal)[https://discord.com/developers/applications] and create a new application

### Configure bot

Create a 'stack.env' file in the root of the project.
This file should contain the following required variables:

```
POSTGRES_USER=wcb3
POSTGRES_PASSWORD=wcb3
POSTGRES_DB=pg_wcb3
OWNERS=DISCORD_ID_OF_BOT_OWNER
APPLICATION_ID=BOT_APPLICATION_ID
GUILD_ID=GUILD_ID_OF_MAIN_SERVER
TOKEN=DISCORD_TOKEN
CHANNEL=MAIN_BOT_CHANNEL_ID
AUTOUNBAN=False
```

The env file can also contain the following optional requirements:

> NOTE!: some commands will fail if one or more of the following variables are not set

```
COUNTDOWN_TITLE
COUNTDOWN=31/03/24 00:00:00
COUNTDOWN_URL
YACHJA=DISCORD_ID_YACHJA
GROM=DISCORD_ID_PINGY1
API_NINJAS_KEY
PHILOSOPHY_CHANNEL=DISCORD_ID_PHILOSOPHY_CHANNEL
S3_REGION=us-east-1
S3_ACCESS_KEY_ID
S3_SECRET_ACCESS_KEY
S3_BUCKET
S3_PREFIX
POSTGRES_HOST
POSTGRES_DATABASE
OPENAI_API_KEY
BANTRESHOLD=4
MEMBER_ROLE_ID=DISCORD_MEMBER_ROLE_ID
```

## Starting the bot

First, build the docker image using 
```cmd
docker-compose build
````

Then, you can start the bot using
```cmd
docker-compose up
```
