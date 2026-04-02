import discord
from discord.ext import commands
from discord import ui, app_commands
import random

BOARD_SIZE = 9


class SnakeView(ui.View):
    def __init__(self, cog: "SnakeCog", user: discord.User):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user.id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This game belongs to someone else.",
                ephemeral=True,
            )
            return False
        return True

    @ui.button(emoji="⬅️", style=discord.ButtonStyle.primary, row=0)
    async def left(self, interaction: discord.Interaction, button: ui.Button):
        await self.cog.move(interaction, -1, 0)

    @ui.button(emoji="⬆️", style=discord.ButtonStyle.primary, row=0)
    async def up(self, interaction: discord.Interaction, button: ui.Button):
        await self.cog.move(interaction, 0, -1)

    @ui.button(emoji="⬇️", style=discord.ButtonStyle.primary, row=0)
    async def down(self, interaction: discord.Interaction, button: ui.Button):
        await self.cog.move(interaction, 0, 1)

    @ui.button(emoji="➡️", style=discord.ButtonStyle.primary, row=0)
    async def right(self, interaction: discord.Interaction, button: ui.Button):
        await self.cog.move(interaction, 1, 0)

    @ui.button(label="Restart", emoji="🔄", style=discord.ButtonStyle.success, row=1)
    async def restart(self, interaction: discord.Interaction, button: ui.Button):
        await self.cog.restart_game(interaction, self.user_id)


class SnakeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, dict] = {}

    def generate_board(self, game: dict) -> str:
        board = [["⬛" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        fx, fy = game["fruit"]
        board[fy][fx] = "🍎"

        for i, (x, y) in enumerate(game["snake"]):
            board[y][x] = "🟩" if i == 0 else "🟢"

        return "\n".join("".join(row) for row in board)

    @app_commands.command(name="snake", description="Start a Snake game 🐍")
    async def snake_slash(self, interaction: discord.Interaction):
        await self.start_game(interaction)

    async def start_game(self, interaction: discord.Interaction):
        game = {
            "snake": [(BOARD_SIZE // 2, BOARD_SIZE // 2)],
            "direction": (0, 0),
            "fruit": (
                random.randrange(0, BOARD_SIZE),
                random.randrange(0, BOARD_SIZE),
            ),
            "alive": True,
            "score": 0,
            "owner_id": interaction.user.id,
            "message_id": None,
            "channel_id": interaction.channel.id,
        }

        self.games[interaction.channel.id] = game

        board_text = self.generate_board(game)
        view = SnakeView(self, interaction.user)

        await interaction.response.send_message(
            f"🐍 **Snake Game started.**\nScore: **0**\n{board_text}",
            view=view,
        )

        msg = await interaction.original_response()
        game["message_id"] = msg.id

    async def restart_game(self, interaction: discord.Interaction, owner_id: int):
        channel_id = interaction.channel.id

        game = {
            "snake": [(BOARD_SIZE // 2, BOARD_SIZE // 2)],
            "direction": (0, 0),
            "fruit": (
                random.randrange(0, BOARD_SIZE),
                random.randrange(0, BOARD_SIZE),
            ),
            "alive": True,
            "score": 0,
            "owner_id": owner_id,
            "message_id": None,
            "channel_id": channel_id,
        }
        self.games[channel_id] = game

        board_text = self.generate_board(game)
        view = SnakeView(self, interaction.user)

        try:
            msg = await interaction.channel.fetch_message(
                self.games[channel_id]["message_id"]
            )
        except Exception:
            await interaction.response.edit_message(
                content=f"🐍 **Snake Game restarted.**\nScore: **0**\n{board_text}",
                view=view,
            )
            return

        await interaction.response.defer()
        await msg.edit(
            content=f"🐍 **Snake Game restarted.**\nScore: **0**\n{board_text}",
            view=view,
        )
        game["message_id"] = msg.id

    async def move(self, interaction: discord.Interaction, dx: int, dy: int):
        channel_id = interaction.channel.id
        game = self.games.get(channel_id)

        if not game or not game["alive"]:
            await interaction.response.send_message(
                "The game has not started yet or has already ended.",
                ephemeral=True,
            )
            return

        if (dx, dy) != (0, 0):
            game["direction"] = (dx, dy)

        snake = game["snake"]
        head_x, head_y = snake[0]
        dir_x, dir_y = game["direction"]

        new_x = head_x + dir_x
        new_y = head_y + dir_y

        if not (0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE):
            game["alive"] = False
            await interaction.response.edit_message(
                content=f"💀 You hit the wall. Final score: **{game['score']}**",
                view=None,
            )
            return

        if (new_x, new_y) in snake:
            game["alive"] = False
            await interaction.response.edit_message(
                content=f"💀 You ran into yourself. Final score: **{game['score']}**",
                view=None,
            )
            return

        snake.insert(0, (new_x, new_y))

        if (new_x, new_y) == game["fruit"]:
            game["score"] += 1

            while True:
                fx = random.randrange(0, BOARD_SIZE)
                fy = random.randrange(0, BOARD_SIZE)
                if (fx, fy) not in snake:
                    game["fruit"] = (fx, fy)
                    break
        else:
            snake.pop()

        board_text = self.generate_board(game)
        view = SnakeView(self, interaction.user)

        await interaction.response.edit_message(
            content=f"🐍 **Snake Game**\nScore: **{game['score']}**\n{board_text}",
            view=view,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SnakeCog(bot))
