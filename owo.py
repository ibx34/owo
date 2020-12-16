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

import aiohttp
import aioredis
import asyncpg
import discord
from discord.ext import commands

import config


class owo(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_pre,
            case_insensitive=True,
            reconnect=True,
            status=discord.Status.idle,
            intents=discord.Intents(
                messages=True,
                guilds=True,
                members=True,
                guild_messages=True,
                dm_messages=True,
                reactions=True,
                guild_reactions=True,
                dm_reactions=True,
                voice_states=True,
                presences=True,
            ),
        )
        self.config = config
        self.session = None
        self.pool = None
        self.redis = None
        self.used = 0
        self.remove_command("help")

    async def get_pre(self, bot, message):

        return commands.when_mentioned_or(*config.prefix)(bot, message)

    async def start(self):
        self.session = aiohttp.ClientSession(loop=self.loop)

        await super().start(config.token)

    async def on_ready(self):

        self.redis = await aioredis.create_redis_pool(
            "redis://localhost", loop=self.loop
        )

        self.guild = self.get_guild(config.home_guild)

        await self.change_presence(
            status=discord.Status.online, activity=discord.Game("\\owo/")
        )

        print("✔️ Bot started loading modules")
        for ext in config.extensions:
            try:
                self.load_extension(f"{ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}, {e}")
                print(ext)

        print(f"✔️ Bot started. Guilds: {len(self.guilds)} Users: {len(self.users)}")

    async def on_message(self, message):

        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command:
            await self.process_commands(message, ctx)

    async def process_commands(self, message, ctx):

        if ctx.command is None:
            return

        self.used += 1
        await self.invoke(ctx)

    async def on_guild_join(self, guild):

        if guild.id == config.home_guild:
            return


if __name__ == "__main__":
    owo().run()
