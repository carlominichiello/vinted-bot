# vinted-bot

Vinted bot is composed of two applications, a Discord bot, and a scraper, that allows you to get notified when a new item is posted on Vinted. The bot can also do background scraping to scrape while waiting for new items and random scraping to scrape random items.

- [Configuration](#configuration)
- [Running the bot](#running-the-bot)
- [Usage](#usage)

## Configuration

Several configuration files are needed to run the bot and the monitor:
- `app.yaml`: general configuration file
- `bot.yaml`: Bot configuration file
- `database.yaml`: Database configuration file
- `scraper.yaml`: Scraper configuration file

Here are the common configuration parameters:
- `log_level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logs_directory`: Directory where the logs are stored


### App configuration
```yaml
log_level: INFO
logs_directory: ./logs
```

### Bot configuration
```yaml
log_level: INFO
logs_directory: ./logs
logs_channel: <webhook_url> # if you want to log the bot activity in a specific channel (can be created with the $set_logs_channel command)
token: <discord bot token> 
command_prefix: $
watch:
  <webhook_url>: 
    channel: <channel_name>
    min_favourites: # if you want to be notified only if the item has more than min_favourites favourites
    min_rating: # if you want to be notified only if the seller has more than min_rating rating
    max_days_offset: # if you want to be notified only if the item has been posted less than max_days_offset days ago
    min_views: # if you want to be notified only if the item has more than min_views views
    min_fv_ratio: # if you want to be notified only if the item has more than min_fv_ratio favourites/views ratio
    background_scraping: # if you want to scrape in background
    url: <url_to_watch>
```

### Database configuration
```yaml
log_level: INFO
logs_directory: ./logs
connection_string: <mongodb connection string>
db_name: <database name>
```

### Scraper configuration
```yaml
log_level: INFO
logs_directory: ./logs
request_interval: <seconds between each request>
recheck_interval: <seconds between each recheck>
```

## Running the bot

### Docker

I recommend using docker-compose to run the bot and the monitor. Here is an example of a docker-compose file:

```yaml
version: "3.3"
services:
  vinted-bot:
    image: vinted-bot
    container_name: vinted-bot
    volumes:
      - "/home/pi/docker/vinted-bot/config:/config"
    restart: unless-stopped
    network_mode: host # if using MongoDB Atlas
  vinted-monitor:
    image: vinted-monitor
    container_name: vinted-monitor
    volumes:
      - "/home/pi/docker/vinted-bot/config:/config"
    restart: unless-stopped
    network_mode: host # if using MongoDB Atlas

    # you can eventually add a MongoDB container if you want to use a local database
```

### Manual

```bash
pip install -r requirements.txt
```

Then you can start the bot:
```bash
python bot.py
```

And the monitor:
```bash
python monitor.py
```


## Usage

Go to a Discord channel you want to turn into a watch channel and type `$watch_create <url>` (`$` being your prefix). The bot will then send a message to the channel when a new item is posted on Vinted.
For more information, type `$help` in a Discord channel.

![Bot Image](https://i.imgur.com/chIQxK3.png)