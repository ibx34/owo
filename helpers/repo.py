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

import arrow
import config
import discord
import requests
from cogs.pagination import BotEmbedPaginator
from github import Github, InputFileContent, Repository

g = Github(f"{config.github_token}")

async def search_repo(self, repo):
    data = g.get_repo(repo).raw_data
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
    [`Issues`]({data['html_url']}/issues)
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

async def search_repo_commits(self, repo, page):
    data = g.get_repo(repo)
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
    data = g.get_repo(repo)
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
    repo = g.get_repo(repo)
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

async def get_repo_contributors(self,repo,page):
    data = g.get_repo(repo)
    contributors = data.get_contributors().get_page(page)
    contributors_list = [
        f"[`{x.login}`]({x.html_url})" for x in contributors
    ]
    fields = 7
    decided = [
        contributors_list[i * fields : (i + 1) * fields]
        for i in range((len(contributors_list) + fields - 1) // fields)
    ]
    pages = []

    for x in range(len(decided)):
        embed = discord.Embed(
            color=config.base_color, title=f'Showing contributors for: "{repo}"'
        )
        embed.set_thumbnail(url=data.owner.avatar_url)
        embed.add_field(name=f"Links {x}", value="\n".join(decided[x]))
        pages.append(embed)

    return pages
