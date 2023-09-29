import discord
from discord.errors import Forbidden
from discord.ext import commands

from src.bot.cogs.cog import Cog


async def send_embed(ctx, embed):
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send(
                "Hey, seems like I can't send embeds. Please check my permissions :)"
            )
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ",
                embed=embed,
            )


class HelpCog(Cog):
    """
    Help commands
    """

    @commands.command()
    async def help(self, ctx, *input):
        """
        Sends this message
        Usage: `help`
        """
        prefix = self.bot_config["command_prefix"]

        owner = "estebanthi"
        github = "https://github.com/estebanthi/vinted-bot"

        if not input:
            try:
                owner = ctx.guild.get_member(owner).mention

            except AttributeError:
                owner = owner

            emb = discord.Embed(
                title="Commands and modules",
                color=discord.Color.blue(),
                description=f"Use `{prefix}help <module>` to gain more information about that module "
                f":smiley:\n",
            )

            cogs_desc = ""
            for cog in self.bot.cogs:
                cogs_desc += f"`{cog}` {self.bot.cogs[cog].__doc__}\n"

            emb.add_field(name="Modules", value=cogs_desc, inline=False)

            commands_desc = ""
            for command in self.bot.walk_commands():
                if not command.cog_name and not command.hidden:
                    commands_desc += f"{command.name} - {command.help}\n"

            if commands_desc:
                emb.add_field(
                    name="Not belonging to a module", value=commands_desc, inline=False
                )

            emb.add_field(
                name="About", value=f"Developed by {owner}.\nGithub: {github}"
            )

        elif len(input) == 1:
            for cog in self.bot.cogs:
                if cog.lower() == input[0].lower():
                    emb = discord.Embed(
                        title=f"{cog} - Commands",
                        description=self.bot.cogs[cog].__doc__,
                        color=discord.Color.green(),
                    )

                    for command in self.bot.get_cog(cog).get_commands():
                        if not command.hidden:
                            emb.add_field(
                                name=f"`{prefix}{command.name}`",
                                value=command.help,
                                inline=False,
                            )
                    break

            else:
                emb = discord.Embed(
                    title="What's that?!",
                    description=f"I've never heard from a module called `{input[0]}` before :scream:",
                    color=discord.Color.orange(),
                )

        elif len(input) > 1:
            emb = discord.Embed(
                title="That's too much.",
                description="Please request only one module at once :sweat_smile:",
                color=discord.Color.orange(),
            )

        await send_embed(ctx, emb)
