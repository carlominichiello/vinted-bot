from schema import Schema, SchemaError


def validate_log_levels(value):
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if value not in log_levels:
        raise SchemaError(
            f"{value} is not a valid log level: supported log levels are {log_levels}"
        )
    return True


def validate_watch(value):
    if not value:
        return True
    if not isinstance(value, dict):
        raise SchemaError(f"{value} should be a dict")
    for k, v in value.items():
        watch_item = value[k]
        if "url" not in watch_item:
            raise SchemaError(f"Missing url in watch item {k}")
        if "channel" not in watch_item:
            raise SchemaError(f"Missing channel in watch item {k}")
        if "min_rating" in watch_item:
            try:
                float(watch_item["min_rating"])
            except ValueError:
                raise SchemaError(f"min_rating should be a float")
        if "min_favourites" in watch_item:
            try:
                int(watch_item["min_favourites"])
            except ValueError:
                raise SchemaError(f"min_favourites should be a int")
    return True


app_config_schema = Schema({"log_level": validate_log_levels, "logs_directory": str})

bot_config_schema = Schema(
    {
        "token": str,
        "command_prefix": str,
        "log_level": validate_log_levels,
        "logs_directory": str,
        "watch": validate_watch,
    }
)

scraper_config_schema = Schema(
    {
        "log_level": validate_log_levels,
        "logs_directory": str,
        "request_interval": int,
        "recheck_interval": int,
        "page_limit": int,
    }
)

database_config_schema = Schema(
    {
        "log_level": validate_log_levels,
        "logs_directory": str,
        "connection_string": str,
        "db_name": str,
    }
)