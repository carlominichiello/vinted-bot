from schema import Or, Schema, SchemaError


def _validate_log_levels(value):
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if value not in log_levels:
        raise SchemaError(
            f"{value} is not a valid log level: supported log levels are {log_levels}"
        )
    return True


def _validate_watch(value):
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
                raise SchemaError("min_rating should be a float")
        if "min_favourites" in watch_item:
            try:
                int(watch_item["min_favourites"])
            except ValueError:
                raise SchemaError("min_favourites should be a int")
        if "max_days_offset" in watch_item:
            try:
                int(watch_item["max_days_offset"])
            except ValueError:
                raise SchemaError("max_days_offset should be a int")
        if "min_views" in watch_item:
            try:
                int(watch_item["min_views"])
            except ValueError:
                raise SchemaError("min_views should be a int")
        if "min_fv_ratio" in watch_item:
            try:
                float(watch_item["min_fv_ratio"])
            except ValueError:
                raise SchemaError("min_fv_ratio should be a float")
    return True


app_config_schema = Schema({"log_level": _validate_log_levels, "logs_directory": str})

bot_config_schema = Schema(
    {
        "token": str,
        "command_prefix": str,
        "log_level": _validate_log_levels,
        "logs_directory": str,
        "watch": _validate_watch,
        "logs_channel": Or(str, None),
    }
)

scraper_config_schema = Schema(
    {
        "log_level": _validate_log_levels,
        "logs_directory": str,
        "request_interval": int,
        "recheck_interval": int,
        "page_limit": int,
    }
)

database_config_schema = Schema(
    {
        "log_level": _validate_log_levels,
        "logs_directory": str,
        "connection_string": str,
        "db_name": str,
    }
)
