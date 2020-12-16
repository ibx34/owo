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

class make_my_life_easier:
    def __init__(self,bot):
        self.bot = bot
        self.api_urls = {"user": "https://api.github.com/search/user/{query}"}
        self.g = Github(f"{config.github_token}")

    async def search_user(self,user):
        data = self.g.get_user(user).raw_data

        embed = discord.Embed(color=config.base_color,title=f"Showing top result for: \"{user}\"")
        embed.set_thumbnail(url=data['avatar_url'])
        embed.add_field(name="Links",value=dedent(f"""
        [`Repos ({data['public_repos']})`](https://github.com/{user}?tab=repositories)
        [`Gists ({data['public_gists']})`](https://gist.github.com/{user})
        [`Organizations`](https://github.com/{user})
        [`Subscriptions`](https://github.com/{user})
        [`Followers ({data['followers']})`](https://github.com/{user}?tab=followers)
        [`Following ({data['following']})`](https://github.com/{user}?tab=following)
        [`Starred`](https://github.com/{user}?tab=stars)
        """),inline=False) 

        embed.add_field(name="Relevant Information",value=dedent(f"""
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
        """),inline=False)

        return embed

    async def search_user_repos(self,user):
        data = requests.get(self.g.get_user(user).repos_url).json()
        fields = 7

        repos = [f"""`[{x}]` [`{data[x]['full_name']}`]({data[x]['html_url']}) {"<:fork:788611349352546310>" if data[x]['fork'] else ""}""" for x in range(len(data))]
        decided = [repos[i * fields:(i + 1) * fields] for i in range((len(repos) + fields - 1) // fields )]  

        embed = discord.Embed(color=config.base_color,title=f"Showing repos for: \"{user}\"",description="Type the number next to a repo to view it as if you were running `owo --repo <.../...>`")
        embed.set_thumbnail(url=data[0]['owner']['avatar_url'])      

        for x in range(len(decided)): 
            embed.add_field(name=f"Links",value="\n".join(decided[x]),inline=False)

        return {"embed": embed, "repo_data": [data[x]['full_name'] for x in range(len(data))]}

    async def search_repo(self,repo):
        data = self.g.get_repo(repo).raw_data
        InputFileContent

        embed = discord.Embed(color=config.base_color,title=f"Showing info for: \"{repo}\"",description=data['description'])
        embed.set_thumbnail(url=data['owner']['avatar_url'])
        embed.add_field(name="Links",value=dedent(f"""
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
        """),inline=False)
        embed.add_field(name="Relevant Information",value=dedent(f"""
        {f"Repo License: {data['license']['name']}" if data['license'] else ""}
        Repo Language: {data['language']}
        Archived: {data['archived']}
        Open Issues: {data['open_issues']}
        Default Branch: {data['default_branch']}
        Created: {arrow.get(data['created_at']).humanize()} ({data['created_at']})
        Last Updated: {arrow.get(data['updated_at']).humanize()} ({data['updated_at']})
        Last Pushed: {arrow.get(data['pushed_at']).humanize()} ({data['pushed_at']})
        """),inline=False)
        return embed

    async def search_org(self,org):
        data = self.g.get_organization(org).raw_data

        embed = discord.Embed(color=config.base_color,title=f"Showing info for: \"{data['login']}\"",description=data['description'])
        embed.set_thumbnail(url=data['avatar_url'])
        embed.add_field(name="Links",value=dedent(f"""
        [`Jump to Organization`]({data['html_url']})
        """),inline=False)
        embed.add_field(name="Repositories",value=f"Run `owo --org -repos {org}` to get a full list of repos.")

        embed.add_field(name="Relevant Information",value=dedent(f"""
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
        """),inline=False)

        return embed

    async def search_org_repos(self,org):
        data = requests.get(self.g.get_organization(org).repos_url).json()
        fields = 7

        repos = [f"""`[{x}]` [`{data[x]['full_name']}`]({data[x]['html_url']}) {"<:fork:788611349352546310>" if data[x]['fork'] else ""}""" for x in range(len(data))]
        decided = [repos[i * fields:(i + 1) * fields] for i in range((len(repos) + fields - 1) // fields )]  

        embed = discord.Embed(color=config.base_color,title=f"Showing repos for: \"{org}\"",description="Type the number next to a repo to view it as if you were running `owo --repo <.../...>`")
        embed.set_thumbnail(url=data[0]['owner']['avatar_url'])      

        for x in range(len(decided)): 
            embed.add_field(name=f"Links",value="\n".join(decided[x]),inline=False)

        return {"embed": embed, "repo_data": [data[x]['full_name'] for x in range(len(data))]}

    async def search_org_members(self,org):
        data = requests.get(f"https://api.github.com/orgs/{org}/members").json()
        fields = 7

        members = [f"`[{x}]` [`{data[x]['login']}`]({data[x]['html_url']})" for x in range(len(data))]
        decided = [members[i * fields:(i + 1) * fields] for i in range((len(members) + fields - 1) // fields )]  

        embed = discord.Embed(color=config.base_color,title=f"Showing members for: \"{org}\"",description="Type the number next to a member to view it as if you were running `owo --user <...>`")     

        for x in range(len(decided)): 
            embed.add_field(name=f"Links",value="\n".join(decided[x]),inline=False)

        return {"embed": embed, "repo_data": [data[x]['login'] for x in range(len(data))]}

    async def search_for_code(self,statement):
        code_seach = self.g.search_code(statement).get_page(1)
        list = []
        for x in code_seach:
            try:
                repo = x.path.split('/')[0]
                possible_repo = self.g.search_repositories(repo).get_page(1)[0]
                if type(possible_repo) == Repository.Repository:
                    list.append(repo)
            except:
                pass

        print(list)
        return(list)

class github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="--user",brief="Get information off of github based on user, repo, org.",description="Get information off of github based on user, repo, org.",invoke_without_command=True)
    async def _github_user(self,ctx,*,user):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_user(user=user)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)
    
    @_github_user.command(name="-repos",brief="View a users **PUBLIC** repos",description="Get information on a users repository")
    async def _github_user_repos(self,ctx,*,user):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_user_repos(user=user)

            await ctx.message.add_reaction("✔️")
            original_message = await ctx.send(embed=returned['embed'])

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check, timeout=500)
            try:
                new_returned = await ibxs_helper.search_repo(repo=returned["repo_data"][int(msg.content)])
                await original_message.delete()
                await ctx.send(embed=new_returned)
            except Exception as err:
                print(err)

        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)     

    @commands.command(name="--repo",brief="Get information off of github basedd on user, repo, org",description="Get information off of github based on user, repo, org.")
    async def _github_repo(self,ctx,*,repo):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_repo(repo=repo)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @commands.group(name="--org",brief="Get information off of github basedd on user, repo, org",description="Get information off of github based on user, repo, org.",invoke_without_command=True)
    async def _github_org(self,ctx,*,org):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_org(org=org)

            await ctx.message.add_reaction("✔️")
            await ctx.send(embed=returned)
        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)

    @_github_org.command(name="-members",brief="View an orgs members",description="Get information on an orgs members")
    async def _github_org_members(self,ctx,*,org):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_org_members(org=org)

            await ctx.message.add_reaction("✔️")
            original_message = await ctx.send(embed=returned['embed'])

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check, timeout=500)
            try:
                new_returned = await ibxs_helper.search_user(user=returned["repo_data"][int(msg.content)])
                await original_message.delete()
                await ctx.send(embed=new_returned)
            except Exception as err:
                print(err)

        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)    

    @_github_org.command(name="-repos",brief="View an orgs **PUBLIC** repos",description="Get information on an orgs repository")
    async def _github_org_repo(self,ctx,*,org):
        ibxs_helper = make_my_life_easier(bot=self.bot)
        try:
            returned = await ibxs_helper.search_org_repos(org=org)

            await ctx.message.add_reaction("✔️")
            original_message = await ctx.send(embed=returned['embed'])

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check, timeout=500)
            try:
                new_returned = await ibxs_helper.search_repo(repo=returned["repo_data"][int(msg.content)])
                await original_message.delete()
                await ctx.send(embed=new_returned)
            except Exception as err:
                print(err)

        except Exception as err:
            await ctx.message.add_reaction("❌")
            await ctx.send(err)    


    @commands.command(name="--help",brief="Shows this menu.",description="Get information off of github based on user, repo, org.")   
    async def _github_help(self,ctx):

        embed = discord.Embed(color=config.base_color)
        embed.set_author(name="Help as arrived!",icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Commands",value=dedent(f"""
        For commands please check out my [GitHub Repo](), this will list commands and how to use them. If you're still confused feel free to join my [Support server]({config.support})
        """),inline=False)

        embed.add_field(name="Useful Links",value=dedent(f"""
        [`Support server`]({config.support})
        [`Github`]({config.github})
        """),inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(github(bot))
