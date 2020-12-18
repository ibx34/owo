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

import asyncio
import re
from textwrap import dedent

import json
import aiohttp
import aioredis
import arrow
import asyncpg
import config
import discord
import requests
from discord.ext import commands
from github import Github, InputFileContent, Repository
from cogs.pagination import BotEmbedPaginator
import helpers
from cogs.error import on_cooldown


class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.g = Github(f"{config.github_token}")

    @commands.group(
        name="--settings",
        brief="Add prefered users, orgs, repos to make running commands easier.",
        description="Add prefered users, orgs, repos to make running commands easier.",
        invoke_without_command=True,
    )
    async def _user_settings(self, ctx):

        return await ctx.send(
            "To setup settings please run `owogit --settings -<setting> [<value>]`. If there is any issues with your values i'll get you know!"
        )

    @_user_settings.command(
        name="-register",
        brief="Add prefered users, orgs, repos to make running commands easier.",
        description="Add prefered users, orgs, repos to make running commands easier.",
    )
    @on_cooldown(3600)
    async def _user_settings_register(self, ctx):
        async with self.bot.pool.acquire() as conn:
            user = await conn.fetchval(
                "SELECT user_id FROM user_settings WHERE user_id = $1", ctx.author.id
            )

            if user:
                return await ctx.send(
                    f"<:redX:788616379271872512> You're already registered. If you would like to delete your data run `owogit --settings -delete`."
                )

            try:
                await conn.execute(
                    "INSERT INTO user_settings(user_id) VALUES($1)", ctx.author.id
                )
            except Exception as err:
                return await ctx.send(
                    f"Something went wrong whilst updating your settings.```{err}```"
                )

            await ctx.send(
                f"<:greenCheck:788616379103707157> You're good to go! You can start running settings commands."
            )

    @_user_settings.command(
        name="-delete",
        brief="Add prefered users, orgs, repos to make running commands easier.",
        description="Add prefered users, orgs, repos to make running commands easier.",
    )
    @on_cooldown(3600)
    async def _user_settings_delete(self, ctx):
        async with self.bot.pool.acquire() as conn:
            user = await conn.fetchval(
                "SELECT user_id FROM user_settings WHERE user_id = $1", ctx.author.id
            )

            if not user:
                return await ctx.send(
                    f"<:redX:788616379271872512> You're not registered. You can run `owogit --settings -register` to register."
                )

            try:
                await conn.execute(
                    "DELETE FROM user_settings WHERE user_id = $1", ctx.author.id
                )
            except Exception as err:
                return await ctx.send(
                    f"Something went wrong whilst updating your settings.```{err}```"
                )

            await ctx.send(
                f"<:greenCheck:788616379103707157> Your data has been deleted. You'll have to run `owogit --settings -register` again."
            )

    @_user_settings.command(
        name="-repo",
        brief="Add prefered users, orgs, repos to make running commands easier.",
        description="Add prefered users, orgs, repos to make running commands easier.",
    )
    @on_cooldown(30)
    async def _user_settings_repo(self, ctx, repo):
        try:
            self.g.get_repo(repo)
        except Exception as err:
            return await ctx.send(
                f"I failed to get that repo. Make sure it exists and you're using the `<user>/<repo_name>` format.\n```{err}```"
            )

        async with self.bot.pool.acquire() as conn:
            try:
                await conn.execute(
                    "UPDATE user_settings SET pref_repo = $1 WHERE user_id = $2",
                    repo,
                    ctx.author.id,
                )
            except Exception as err:
                return await ctx.send(
                    f"Something went wrong whilst updating your settings.```{err}```"
                )

            await ctx.send(
                f"<:greenCheck:788616379103707157> Updated your settings. Your preferred repo is now {repo}"
            )

    @_user_settings.command(
        name="-user",
        brief="Add prefered users, orgs, repos to make running commands easier.",
        description="Add prefered users, orgs, repos to make running commands easier.",
    )
    @on_cooldown(30)
    async def _user_settings_user(self, ctx, user):
        try:
            self.g.get_user(user)
        except Exception as err:
            return await ctx.send(
                f"I failed to get that user. Make sure they exist.\n```{err}```"
            )

        async with self.bot.pool.acquire() as conn:
            try:
                await conn.execute(
                    "UPDATE user_settings SET pref_user = $1 WHERE user_id = $2",
                    user,
                    ctx.author.id,
                )
            except Exception as err:
                return await ctx.send(
                    f"Something went wrong whilst updating your settings.```{err}```"
                )

            await ctx.send(
                f"<:greenCheck:788616379103707157> Updated your settings. Your preferred user is now {user}"
            )

    @_user_settings.command(
        name="-config",
        brief="Add prefered users, orgs, repos to make running commands easier.",
        description="Add prefered users, orgs, repos to make running commands easier.",
    )
    @on_cooldown(30)
    async def _user_settings_config(self, ctx):
        async with self.bot.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM user_settings WHERE user_id = $1", ctx.author.id
            )

            if not user:
                return await ctx.send(
                    f"<:redX:788616379271872512> You're not registered. You can run `owogit --settings -register` to register."
                )

            await ctx.send(
                dedent(
                    f"""
            (!) Showing config **{ctx.author.display_name}** ({ctx.author})
            Preferred User: {f"<https://github.com/{user['pref_user']}>" if user['pref_user'] is not None else "owogit --settings -user <user>"}
            Preferred Repo: {f"<https://github.com/{user['pref_repo']}>" if user['pref_repo'] is not None else "owogit --settings -repo <user>/<repo_name>"}
            """
                )
            )


def setup(bot):
    bot.add_cog(settings(bot))
