import asyncio
import random

import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

REDDIT_HEADERS = {"User-Agent": "PanosBot/2.0 (discord.py)"}
REDDIT_LIMIT = 50


class MemeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _fetch_json(self, url: str, headers: dict | None = None) -> dict:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _send_reddit_image(
        self, interaction: discord.Interaction, subreddit: str, title: str
    ):
        await interaction.response.defer(thinking=True)
        url = f"https://www.reddit.com/r/{subreddit}.json?limit={REDDIT_LIMIT}"
        try:
            data = await self._fetch_json(url, headers=REDDIT_HEADERS)
            posts = [
                c["data"]
                for c in data["data"]["children"]
                if c.get("data") and not c["data"].get("over_18")
            ]
            if not posts:
                raise KeyError("no posts")
            post = random.choice(posts)
            image_url = post["url"]
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError, IndexError):
            await interaction.followup.send(
                "Failed to fetch meme. Please try again later."
            )
            return

        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=image_url)
        embed.set_footer(text=f"{title} requested by {interaction.user}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="meme", description="Fetch a random meme")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        try:
            data = await self._fetch_json("https://meme-api.com/gimme")
            meme_url = data["url"]
            meme_name = data["title"]
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError):
            await interaction.followup.send(
                "Failed to fetch meme. Please try again later."
            )
            return

        embed = discord.Embed(title=meme_name, color=discord.Color.random())
        embed.set_image(url=meme_url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="animememe", description="Fetch a random anime meme")
    async def animememe(self, interaction: discord.Interaction):
        await self._send_reddit_image(interaction, "animememes", "Anime meme")

    @app_commands.command(name="dogmeme", description="Fetch a random dog meme")
    async def dogmeme(self, interaction: discord.Interaction):
        await self._send_reddit_image(interaction, "dogmemes", "Dog meme")

    @app_commands.command(name="catmeme", description="Fetch a random cat meme")
    async def catmeme(self, interaction: discord.Interaction):
        await self._send_reddit_image(interaction, "catmemes", "Cat meme")


async def setup(bot):
    await bot.add_cog(MemeCog(bot))
