import discord
from discord.ext import commands
from discord import app_commands, ui


class HelpDropdown(ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="🎵 Music Commands", description="Playback and audio controls"),
            discord.SelectOption(label="🎮 Game Commands", description="Snake / Chess"),
            discord.SelectOption(label="🌸 Anime Commands", description="Waifu / Neko / Husbando"),
            discord.SelectOption(label="😂 Meme Commands", description="Memes and image fun"),
            discord.SelectOption(label="💬 Chat Commands", description="Chat / Remember / Profile"),
            discord.SelectOption(label="⚙ System Commands", description="Admin and utility commands"),
        ]

        super().__init__(
            placeholder="Choose a command category...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        if "Music" in choice:
            embed = discord.Embed(
                title="🎵 Music Commands",
                color=discord.Color.blue()
            )
            embed.add_field(name="/play <query>", value="Play a song from YouTube", inline=False)
            embed.add_field(name="/skip", value="Skip the current track", inline=False)
            embed.add_field(name="/pause", value="Pause playback", inline=False)
            embed.add_field(name="/resume", value="Resume playback", inline=False)
            embed.add_field(name="/queue", value="Show the current queue", inline=False)
            embed.add_field(name="/speed <0.5-2.0>", value="Adjust playback speed", inline=False)
            embed.add_field(name="/eq <bass_db> <treble_db>", value="Set bass and treble manually", inline=False)
            embed.add_field(name="/tone <normal|bass|treble>", value="Apply a quick tone preset", inline=False)
            embed.add_field(name="/audio_profile", value="Show current audio settings", inline=False)
            embed.add_field(name="/stop", value="Stop playback and clear the queue", inline=False)
            embed.add_field(name="/leave", value="Disconnect from voice", inline=False)
            embed.add_field(name="/mdebug", value="Show music and voice debug info", inline=False)
            embed.add_field(name="/testtone", value="Play a short test tone", inline=False)

        elif "Game" in choice:
            embed = discord.Embed(
                title="🎮 Game Commands",
                color=discord.Color.green()
            )
            embed.add_field(name="/snake", value="Start Snake", inline=False)
            embed.add_field(name="/zchess", value="Start a chess match", inline=False)
            embed.add_field(name="/ox_start", value="Play Tic-Tac-Toe", inline=False)

        elif "Anime" in choice:
            embed = discord.Embed(
                title="🌸 Anime Commands",
                color=discord.Color.purple()
            )
            embed.add_field(name="/waifu", value="Get a random waifu image", inline=False)
            embed.add_field(name="/neko", value="Get a random neko image", inline=False)
            embed.add_field(name="/husbando", value="Get a random husbando image", inline=False)
            embed.add_field(name="/happy", value="Get a happy anime image", inline=False)

        elif "Meme" in choice:
            embed = discord.Embed(
                title="😂 Meme Commands",
                color=discord.Color.orange()
            )
            embed.add_field(name="/meme", value="Fetch a random meme", inline=False)
            embed.add_field(name="/catmeme", value="Fetch a cat meme", inline=False)
            embed.add_field(name="/dogmeme", value="Fetch a dog meme", inline=False)
            embed.add_field(name="/animememe", value="Fetch an anime meme", inline=False)

        elif "Chat" in choice:
            embed = discord.Embed(
                title="💬 Chat Commands",
                color=discord.Color.purple()
            )
            embed.add_field(name="/chat <message>", value="Talk with Panos", inline=False)
            embed.add_field(name="/continue_chat", value="Continue your last conversation", inline=False)
            embed.add_field(name="/ask <question>", value="Ask a taught question", inline=False)
            embed.add_field(name="/teach <question> <answer>", value="Teach a Q/A pair", inline=False)
            embed.add_field(name="/set_preference <key> <value>", value="Save a preference to your profile", inline=False)
            embed.add_field(name="/forget_preference <key>", value="Remove a saved preference", inline=False)
            embed.add_field(name="/set_nickname <name>", value="Set the name Panos will call you", inline=False)
            embed.add_field(name="/remember <note>", value="Store an important note", inline=False)
            embed.add_field(name="/recall [query]", value="Search what I remember about you", inline=False)
            embed.add_field(name="/profile", value="View your memory profile", inline=False)
            embed.add_field(name="/forget_me", value="Delete what Panos remembers about you", inline=False)
            embed.add_field(name="/server_ai_profile <balanced|aggressive|overdrive|beast>", value="Set server-wide AI learning intensity", inline=False)
            embed.add_field(name="/server_ai_status", value="View server AI learning status", inline=False)
            embed.add_field(name="/server_ai_toggle <true|false>", value="Enable or disable server AI learning", inline=False)
            embed.add_field(name="/server_ai_reset", value="Reset server AI learning state", inline=False)

        else:
            embed = discord.Embed(
                title="⚙ System Commands",
                color=discord.Color.teal()
            )
            embed.add_field(name="+my name", value="Simple greeting command", inline=False)
            embed.add_field(name="+invite", value="Show the server invite link", inline=False)
            embed.add_field(name="+name", value="Show the bot name", inline=False)
            embed.add_field(name="+hungry", value="Light chat command", inline=False)
            embed.add_field(name="+555", value="Laugh reaction", inline=False)
            embed.add_field(name="/restart", value="Restart the bot", inline=False)
            embed.add_field(name="/selfupdate", value="Pull the latest code and restart", inline=False)

        await interaction.response.edit_message(embed=embed)


class HelpView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpDropdown())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show the full command menu")
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="📖 Panos Help Menu",
            description="Choose a command category below.",
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Panos V2 by Dale")
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)

        await interaction.response.send_message(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
