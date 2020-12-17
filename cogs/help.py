"""
Copyright 2020 ibx34

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from textwrap import dedent
import config
import discord
from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"hidden": True})

    def get_command_signature(self, command):
        return "{0.clean_prefix}{1.qualified_name} {1.signature}".format(self, command)

    async def send_bot_help(self, mapping):

        ctx = self.context

        embed = discord.Embed(color=config.base_color)
        embed.set_author(name="Help as arrived!", icon_url=ctx.bot.user.avatar_url)
        embed.add_field(
            name="Commands",
            value="\n".join(
                [
                    f"`{x.name} | {x.brief}`"
                    for x in ctx.bot.commands
                    if x.name not in ["jishaku"]
                ]
            ),
            inline=False,
        )

        embed.add_field(
            name="Useful Links",
            value=dedent(
                f"""
        [`Support server`]({config.support})
        [`Github`]({config.github})
        """
            ),
            inline=False,
        )

        await ctx.send(embed=embed)

    async def send_command_help(self, command):

        ctx = self.context
        prefix = ctx.prefix

        embed = discord.Embed(
            color=config.base_color,
            title=f'Showing help for: "{command.name}"',
            description=command.description,
        )
        embed.add_field(
            name="Usage",
            value=f"`{prefix}{command} {' '.join([f'<{command.clean_params[x]}>' for x in command.clean_params])}`",
        )

        await ctx.send(embed=embed)

    async def send_group_help(self, group):

        ctx = self.context
        command = ctx.bot.get_command(group.name)

        str = "\n".join(f"`{x.name} | {x.brief}`" for x in group.commands)

        embed = discord.Embed(
            color=config.base_color,
            title=f'Showing help for: "{command}"',
            description=group.description,
        )
        embed.add_field(name="Commands", value=str)

        await ctx.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


def cog_unload(self):
    self.bot.help_command = self.old_help_command


def setup(bot):
    bot.add_cog(Help(bot))
