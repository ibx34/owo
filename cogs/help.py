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
        # prefix = ctx.prefix  # config.prefix

        return ctx

    async def send_cog_help(self, cog):

        ctx = self.context
        # prefix = ctx.prefix
        # commands = cog.get_commands()

        return ctx

    async def send_command_help(self, command):

        ctx = self.context
        # prefix = ctx.prefix

        return ctx

    async def send_group_help(self, group):

        ctx = self.context
        # prefix = ctx.prefix
        # command = ctx.bot.get_command(group.name)

        return ctx


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
