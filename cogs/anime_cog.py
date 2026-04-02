import discord
from discord.ext import commands
from discord import app_commands
import requests


class AnimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="neko", description="Send a random neko image 😺")
    async def neko(self, interaction: discord.Interaction):
        res = requests.get("https://nekos.best/api/v2/neko").json()
        url = res["results"][0]["url"]

        embed = discord.Embed(title="Neko 😺", color=discord.Color.random())
        embed.set_image(url=url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="waifu", description="Send a random waifu image 💞")
    async def waifu(self, interaction: discord.Interaction):
        res = requests.get("https://nekos.best/api/v2/waifu").json()
        url = res["results"][0]["url"]

        embed = discord.Embed(title="Waifu 💞", color=discord.Color.random())
        embed.set_image(url=url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="husbando", description="Send a random husbando image 💫")
    async def husbando(self, interaction: discord.Interaction):
        res = requests.get("https://nekos.best/api/v2/husbando").json()
        url = res["results"][0]["url"]

        embed = discord.Embed(title="Husbando ⭐", color=discord.Color.random())
        embed.set_image(url=url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="happy", description="Send a happy anime image 🥰")
    async def happy(self, interaction: discord.Interaction):
        res = requests.get("https://nekos.best/api/v2/happy").json()
        url = res["results"][0]["url"]

        embed = discord.Embed(title="Happy 😊", color=discord.Color.random())
        embed.set_image(url=url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pat", description="Send a random pat image 💗")
    async def pat(self, interaction: discord.Interaction):
        res = requests.get("https://nekos.best/api/v2/pat").json()
        url = res["results"][0]["url"]

        embed = discord.Embed(title="Pat 💗", color=discord.Color.random())
        embed.set_image(url=url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="wallpaper", description="Send a random anime wallpaper 🖼️")
    async def wallpaper(self, interaction: discord.Interaction):
        res = requests.get("https://www.nekos.life/api/v2/img/wallpaper").json()

        embed = discord.Embed(title="Wallpaper 🖼️", color=discord.Color.random())
        embed.set_image(url=res["url"])

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dog", description="Send a random dog image 🐶")
    async def dog(self, interaction: discord.Interaction):
        res = requests.get("https://dog.ceo/api/breeds/image/random").json()

        embed = discord.Embed(title="Dog 🐶", color=discord.Color.random())
        embed.set_image(url=res["message"])

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AnimeCog(bot))
