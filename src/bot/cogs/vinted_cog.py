import json
import logging
import os

import discord
import yaml
from discord.ext import commands

from src.bot.cogs.cog import Cog

logger = logging.getLogger("bot")


class VintedCog(Cog):
    """
    Vinted commands
    """

    @commands.command()
    async def watch(self, ctx):
        """
        Sends the watch url for this channel
        Usage: `watch`
        """
        for weburl in self.bot_config["watch"]:
            if self.bot_config["watch"][weburl]["channel"] == ctx.channel.name:
                await ctx.send(
                    f"{ctx.author.mention} - **Watching {self.bot_config['watch'][weburl]['url']}!**"
                )
                return
        await ctx.send(f"{ctx.author.mention} - **No existing watch in this channel!**")

    @commands.command()
    async def watch_create(self, ctx, vintedurl):
        """
        Creates a new watch
        Usage: `watch_create [url]`
        """
        # check if channel is already watched
        for weburl in self.bot_config["watch"]:
            if self.bot_config["watch"][weburl]["channel"] == ctx.channel.name:
                logger.info(f"Channel {ctx.channel.name} is already watched")
                await ctx.send(
                    f"{ctx.author.mention} - **❌ Channel {ctx.channel.name} is already watched!**"
                )
                return

        webhook = await ctx.channel.create_webhook(name="Watcher")
        webhook_url = str(webhook.url)

        new_watch = {}
        new_watch["url"] = vintedurl
        new_watch["channel"] = str(ctx.channel.name)

        watch = self.bot_config["watch"]
        watch[webhook_url] = new_watch
        self.bot_config["watch"] = watch

        logger.info(f"Created watch: {webhook_url}")
        await ctx.send(f"{ctx.author.mention} - **✔️ Watching {vintedurl}!**")

    @commands.command()
    async def watch_update(self, ctx, new_url):
        """
        Changes the url of an existing webhook
        Usage: `watch_update [new_url]`
        """
        for weburl in self.bot_config["watch"]:
            if self.bot_config["watch"][weburl]["channel"] == ctx.channel.name:
                watch = self.bot_config["watch"]
                watch[weburl]["url"] = new_url
                self.bot_config["watch"] = watch

                logger.info(f"Modified url of watch {weburl} to {new_url}")
                await ctx.send(
                    f"{ctx.author.mention} - **✔️ Successfully updated watch for {ctx.channel.name}!**"
                )
                return
        await ctx.send(
            f"{ctx.author.mention} - **❌ No existing watch in this channel!**"
        )

    @commands.command()
    async def watch_remove(self, ctx):
        """
        Removes an existing webhook
        Usage: `watch_remove`
        """
        for weburl in self.bot_config["watch"]:
            if self.bot_config["watch"][weburl]["channel"] == ctx.channel.name:
                watch = self.bot_config["watch"]
                del watch[weburl]
                self.bot_config["watch"] = watch

                logger.info(f"Deleted watch {weburl}")
                await ctx.send(
                    f"{ctx.author.mention} - **✔️ Successfully deleted watch for {ctx.channel.name}!**"
                )
                return
        await ctx.send(
            f"{ctx.author.mention} - **❌ No existing watch in this channel!**"
        )

    @commands.command()
    async def watch_list(self, ctx):
        """
        List all watches
        Usage: `watch_list`
        """
        body = "- ".join(
            [
                f"{v['channel']} => {v['url']}\n"
                for k, v in self.bot_config["watch"].items()
            ]
        )
        await ctx.send(f"**{body}**")

    @commands.command()
    async def set_min_rating(self, ctx, rating):
        """
        Sets the minimum rating (out of 5) for the bot to send a notification
        Usage: `set_min_rating [rating]`
        """
        for weburl in self.bot_config["watch"]:
            if self.bot_config["watch"][weburl]["channel"] == ctx.channel.name:
                watch = self.bot_config["watch"]
                watch[weburl]["min_rating"] = rating
                self.bot_config["watch"] = watch

                logger.info(f"Modified min_rating of watch {weburl} to {rating}")
                await ctx.send(
                    f"{ctx.author.mention} - **✔️ Successfully updated min_rating for {ctx.channel.name}!**"
                )
                return
        await ctx.send(
            f"{ctx.author.mention} - **❌ No existing watch in this channel!**"
        )

    @commands.command()
    async def set_min_favourites(self, ctx, favourites):
        """
        Sets the minimum favourites for the bot to send a notification
        Usage: `set_min_favourites [favourites]`
        """
        for weburl in self.bot_config["watch"]:
            if self.bot_config["watch"][weburl]["channel"] == ctx.channel.name:
                watch = self.bot_config["watch"]
                watch[weburl]["min_favourites"] = favourites
                self.bot_config["watch"] = watch

                logger.info(
                    f"Modified min_favourites of watch {weburl} to {favourites}"
                )
                await ctx.send(
                    f"{ctx.author.mention} - **✔️ Successfully updated min_favourites for {ctx.channel.name}!**"
                )
                return
        await ctx.send(
            f"{ctx.author.mention} - **❌ No existing watch in this channel!**"
        )