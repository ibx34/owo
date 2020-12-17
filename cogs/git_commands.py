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


class make_my_life_easier:
    def __init__(self, bot):
        self.bot = bot
        self.api_urls = {"user": "https://api.github.com/search/user/{query}"}
        self.g = Github(f"{config.github_token}")

    async def search_user(self, user):
        data = self.g.get_user(user).raw_data

        embed = discord.Embed(
            color=config.base_color, title=f'Showing top result for: "{user}"'
        )
        embed.set_thumbnail(url=data["avatar_url"])
        embed.add_field(
            name="Links",
            value=dedent(
                f"""
        [`Repos ({data['public_repos']})`](https://github.com/{user}?tab=repositories)
        [`Gists ({data['public_gists']})`](https://gist.github.com/{user})
        [`Organizations`](https://github.com/{user})
        [`Subscriptions`](https://github.com/{user})
        [`Followers ({data['followers']})`](https://github.com/{user}?tab=followers)
        [`Following ({data['following']})`](https://github.com/{user}?tab=following)
        [`Starred`](https://github.com/{user}?tab=stars)
        """
            ),
            inline=False,
        )

        embed.add_field(
            name="Relevant Information",
            value=dedent(
                f"""
        Name: {data['name']}
        Company: {data['company']}
        Blog: {data['blog']}
        Location: {data['location']}
        Email: {data['email']}
        Hireable: {data['hireable']}
        Twitter: {data['twitter_username']}

        Created: {arrow.get(data['created_at']).humanize()} ({data['created_at']})
        Last Updated: {arrow.get(data['updated_at']).humanize()} ({data['updated_at']})

        Bio: ```{data['bio']}```
        """
            ),
            inline=False,
        )

        return embed

    async def search_user_repos(self, user, page):
        data = requests.get(
            f"{self.g.get_user(user).repos_url}?page={page}&per_page=29"
        ).json()
        fields = 7

        repos = [
            f"""`[{x}]` [`{data[x]['full_name']}`]({data[x]['html_url']}) {"<:fork:788611349352546310>" if data[x]['fork'] else ""}"""
            for x in range(len(data))
        ]
        decided = [
            repos[i * fields : (i + 1) * fields]
            for i in range((len(repos) + fields - 1) // fields)
        ]

        embed = discord.Embed(
            color=config.base_color,
            title=f'Showing repos for: "{user}"',
            description="Type the number next to a repo to view it as if you were running `owo --repo <.../...>`",
        )
        embed.set_thumbnail(url=data[0]["owner"]["avatar_url"])

        for x in range(len(decided)):
            embed.add_field(name=f"Links", value="\n".join(decided[x]), inline=False)

        return {
            "embed": embed,
            "repo_data": [data[x]["full_name"] for x in range(len(data))],
        }

    async def search_repo(self, repo):
        data = self.g.get_repo(repo).raw_data
        InputFileContent

        embed = discord.Embed(
            color=config.base_color,
            title=f'Showing info for: "{repo}"',
            description=data["description"],
        )
        embed.set_thumbnail(url=data["owner"]["avatar_url"])
        embed.add_field(
            name="Links",
            value=dedent(
                f"""
        [`Jump to repo`]({data['html_url']})
        [`Issies`]({data['html_url']}/issues)
        [`Pull Requests`]({data['html_url']}/pulls)
        [`Stars ({data['stargazers_count']})`]({data['html_url']}/stargazers)
        [`Forks`]({data['html_url']}/network/members)
        [`Commit Activity`]({data['html_url']}/graphs/commit-activity)
        [`Repo Pulse`]({data['html_url']}/pulse)
        [`Contributors`]({data['html_url']}/graphs/contributors)
        [`Actions`]({data['html_url']}/actions)
        [`Repo Security`]({data['html_url']}/security)
        [`Repo Homepage`]({data['homepage']})
        [`Watchers ({data['watchers_count']})`]({data['html_url']}/watchers)
        """
            ),
            inline=False,
        )
        embed.add_field(
            name="Relevant Information",
            value=dedent(
                f"""
        {f"Repo License: {data['license']['name']}" if data['license'] else ""}
        Repo Language: {data['language']}
        Archived: {data['archived']}
        Open Issues: {data['open_issues']}
        Default Branch: {data['default_branch']}
        Created: {arrow.get(data['created_at']).humanize()} ({data['created_at']})
        Last Updated: {arrow.get(data['updated_at']).humanize()} ({data['updated_at']})
        Last Pushed: {arrow.get(data['pushed_at']).humanize()} ({data['pushed_at']})
        """
            ),
            inline=False,
        )
        return embed

    async def search_org(self, org):
        data = self.g.get_organization(org).raw_data

        embed = discord.Embed(
            color=config.base_color,
            title=f"Showing info for: \"{data['login']}\"",
            description=data["description"],
        )
        embed.set_thumbnail(url=data["avatar_url"])
        embed.add_field(
            name="Links",
            value=dedent(
                f"""
        [`Jump to Organization`]({data['html_url']})
        """
            ),
            inline=False,
        )
        embed.add_field(
            name="Repositories",
            value=f"Run `owo --org -repos {org}` to get a full list of repos.",
        )

        embed.add_field(
            name="Relevant Information",
            value=dedent(
                f"""
        Name: {data['name']}
        Company: {data['company']}
        Blog: {data['blog']}
        Location: {data['location']}
        Email: {data['email']}
        Twitter: {data['twitter_username']}
        Verified Org: {data['is_verified']}
        Repo Count: {data['public_repos']}
        Gist Count: {data['public_gists']}
        Follwers: {data['followers']}
        Following: {data['following']}
        Created: {arrow.get(data['created_at']).humanize()} ({data['created_at']})
        Last Updated: {arrow.get(data['updated_at']).humanize()} ({data['updated_at']})        
        """
            ),
            inline=False,
        )

        return embed

    async def search_org_repos(self, org):
        data = requests.get(self.g.get_organization(org).repos_url).json()
        fields = 7

        repos = [
            f"""`[{x}]` [`{data[x]['full_name']}`]({data[x]['html_url']}) {"<:fork:788611349352546310>" if data[x]['fork'] else ""}"""
            for x in range(len(data))
        ]
        decided = [
            repos[i * fields : (i + 1) * fields]
            for i in range((len(repos) + fields - 1) // fields)
        ]

        embed = discord.Embed(
            color=config.base_color,
            title=f'Showing repos for: "{org}"',
            description="Type the number next to a repo to view it as if you were running `owo --repo <.../...>`",
        )
        embed.set_thumbnail(url=data[0]["owner"]["avatar_url"])

        for x in range(len(decided)):
            embed.add_field(name=f"Links", value="\n".join(decided[x]), inline=False)

        return {
            "embed": embed,
            "repo_data": [data[x]["full_name"] for x in range(len(data))],
        }

    async def search_org_members(self, org):
        data = requests.get(f"https://api.github.com/orgs/{org}/members").json()
        fields = 7

        members = [
            f"`[{x}]` [`{data[x]['login']}`]({data[x]['html_url']})"
            for x in range(len(data))
        ]
        decided = [
            members[i * fields : (i + 1) * fields]
            for i in range((len(members) + fields - 1) // fields)
        ]

        embed = discord.Embed(
            color=config.base_color,
            title=f'Showing members for: "{org}"',
            description="Type the number next to a member to view it as if you were running `owo --user <...>`",
        )

        for x in range(len(decided)):
            embed.add_field(name=f"Links", value="\n".join(decided[x]), inline=False)

        return {
            "embed": embed,
            "repo_data": [data[x]["login"] for x in range(len(data))],
        }

    async def find_largest_starred(self, user):
        data = self.g.get_user(user)
        list = []
        list2 = []
        for x in data.get_repos():
            list.append(x.stargazers_count)
            list2.append(x.html_url)

        return f"**{user}**'s most starred repo has **{max(list)}** stars.\nLink: <{list2[list.index(max(list))]}>"

    async def search_repo_commits(self, repo, page):
        data = self.g.get_repo(repo)
        commits = data.get_commits().get_page(page)
        commit_list = [f"[`{x.sha[:7]}`]({x.html_url})" for x in commits]
        fields = 7
        decided = [
            commit_list[i * fields : (i + 1) * fields]
            for i in range((len(commit_list) + fields - 1) // fields)
        ]

        embed = discord.Embed(
            color=config.base_color, title=f'Showing commits for: "{repo}"'
        )
        embed.set_thumbnail(url=data.owner.avatar_url)
        for x in range(len(decided)):
            embed.add_field(name=f"Links", value="\n".join(decided[x]))

        return embed

    async def search_repo_issues(self, repo, page):
        data = self.g.get_repo(repo)
        issues = data.get_issues().get_page(page)
        issue_list = [
            f"[`{x.number}`]({x.html_url})" for x in issues if not x.state == "closed"
        ]
        fields = 7
        decided = [
            issue_list[i * fields : (i + 1) * fields]
            for i in range((len(issue_list) + fields - 1) // fields)
        ]
        pages = []

        for x in range(len(decided)):
            embed = discord.Embed(
                color=config.base_color, title=f'Showing issues for: "{repo}"'
            )
            embed.set_thumbnail(url=data.owner.avatar_url)
            embed.add_field(name=f"Links {x}", value="\n".join(decided[x]))
            pages.append(embed)

        return pages

    async def get_repo_issue(self, repo, issue_id):
        repo = self.g.get_repo(repo)
        data = requests.get(f"{repo.url}/issues/{issue_id}").json()

        embed = discord.Embed(color=config.base_color, title=data["title"])
        embed.set_author(
            name=data["user"]["login"],
            icon_url=data["user"]["avatar_url"],
            url=data["user"]["html_url"],
        )
        embed.set_thumbnail(url=data["user"]["avatar_url"])
        embed.add_field(
            name="Links",
            value=dedent(
                f"""
        [`Jump to issue`]({data['html_url']})
        [`Jump to repo`]({repo.html_url})
        [`Jump to author`]({data['user']['html_url']})
        """
            ),
        )
        embed.add_field(
            name="Issue Information",
            value=dedent(
                f"""
        State: {data['state']}
        Locked: {data['locked']} ({data['active_lock_reason']})
        {f"Assignees: {', '.join([f'{x.login}' for x in data['assignees']])}"}
        Comments: {data['comments']}
        Created: {arrow.get(data['created_at']).humanize()} ({data['created_at']})
        Last Updated: {arrow.get(data['updated_at']).humanize()} ({data['updated_at']})        
        """
            ),
            inline=False,
        )
        if data.get("body"):
            embed.add_field(
                name="Issue Comment",
                value=data['body']
            )
        if data.get("labels"):
            embed.add_field(
                name="Issue Labels",
                value=", ".join(
                    [
                        f"**{data['labels'][x]['name']}**"
                        for x in range(len(data["labels"]))
                    ]
                ),
                inline=False,
            )

        return embed


class github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="--user",
        brief="Get information off of github based on user, repo, org.",
        description="Get information off of github based on user, repo, org.",
        invoke_without_command=True,
    )
    async def _github_user(self, ctx, *, user):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_user(user=user)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_user.command(
        name="-repos",
        brief="View a users **PUBLIC** repos",
        description="Get information on a users repository",
    )
    async def _github_user_repos(self, ctx, user, page: int = 1):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_user_repos(user=user, page=page)

            await ctx.message.add_reaction("✔️")
            original_message = await ctx.send(embed=returned["embed"])

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check, timeout=500)
            try:
                new_returned = await ibxs_helper.search_repo(
                    repo=returned["repo_data"][int(msg.content)]
                )
                await original_message.delete()
                await ctx.send(embed=new_returned)
            except Exception as err:
                print(err)

        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @commands.group(
        name="--repo",
        brief="Get information off of github basedd on user, repo, org",
        description="Get information off of github based on user, repo, org.",
        invoke_without_command=True,
    )
    async def _github_repo(self, ctx, *, repo):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_repo(repo=repo)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_repo.command(
        name="-commits",
        brief="Get information off of github basedd on user, repo, org",
        description="Get information off of github based on user, repo, org.",
    )
    async def _github_repo_commits(self, ctx, repo, page: int = 1):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_repo_commits(repo=repo, page=page)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_repo.command(
        name="-issues",
        brief="Get information off of github basedd on user, repo, org",
        description="Get information off of github based on user, repo, org.",
    )
    async def _github_repo_issues(self, ctx, repo, page: int = 1):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_repo_issues(repo=repo, page=page)

            await ctx.message.add_reaction("✔️")
            paginator = BotEmbedPaginator(ctx, returned)
            return await paginator.run()
            # await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_repo.command(
        name="-issue",
        brief="Get information off of github basedd on user, repo, org",
        description="Get information off of github based on user, repo, org.",
    )
    async def _github_repo_issue(self, ctx, repo, issue_id):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.get_repo_issue(repo=repo, issue_id=issue_id)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @commands.group(
        name="--org",
        brief="Get information off of github basedd on user, repo, org",
        description="Get information off of github based on user, repo, org.",
        invoke_without_command=True,
    )
    async def _github_org(self, ctx, *, org):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_org(org=org)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_org.command(
        name="-members",
        brief="View an orgs members",
        description="Get information on an orgs members",
    )
    async def _github_org_members(self, ctx, *, org):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_org_members(org=org)

            await ctx.message.add_reaction("✔️")
            original_message = await ctx.send(embed=returned["embed"])

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check, timeout=500)
            try:
                new_returned = await ibxs_helper.search_user(
                    user=returned["repo_data"][int(msg.content)]
                )
                await original_message.delete()
                await ctx.send(embed=new_returned)
            except Exception as err:
                print(err)

        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_org.command(
        name="-repos",
        brief="View an orgs **PUBLIC** repos",
        description="Get information on an orgs repository",
    )
    async def _github_org_repo(self, ctx, *, org):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_org_repos(org=org)

            await ctx.message.add_reaction("✔️")
            original_message = await ctx.send(embed=returned["embed"])

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check, timeout=500)
            try:
                new_returned = await ibxs_helper.search_repo(
                    repo=returned["repo_data"][int(msg.content)]
                )
                await original_message.delete()
                await ctx.send(embed=new_returned)
            except Exception as err:
                print(err)

        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @commands.command(
        name="--starred",
        brief="Get information off of github basedd on user, repo, org",
        description="Get information off of github based on user, repo, org.",
    )
    async def _github_starred(self, ctx, *, user):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.find_largest_starred(user=user)

            await ctx.message.add_reaction("✔️")
            await ctx.send(returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)


def setup(bot):
    bot.add_cog(github(bot))
