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

import math
import arrow
import config
import discord
import requests
from cogs.pagination import BotEmbedPaginator
from github import Github, InputFileContent, Repository
from cogs.jsk_pagination import PaginatorInterface, WrappedPaginator


async def get_gist(ctx, gist_link):
    str = gist_link.split("/")
    gist_data = requests.get(f"https://api.github.com/gists/{str[4]}").json()

    for x in gist_data["files"]:
        paginator = WrappedPaginator(
            prefix=f'```{gist_data["files"][x]["language"]}',
            suffix="```",
            max_size=1985,
        )
        result = gist_data["files"][x][
            "content"
        ]  # repr(gist_data['files'][x]['content'])
        paginator.add_line(result)

    interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
    await interface.send_to(ctx)
