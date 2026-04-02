"""Music command/control layer extracted from PanosV2.

This module centralizes user-facing music flow, embeds, and channel safety
checks so the transport layer can be rewritten later without reworking slash
commands again.
"""

import os
import sys
import importlib.util
from typing import Optional

import discord
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()

YTDL_PLAYER_CLIENTS = [
    client.strip()
    for client in os.getenv("YTDL_PLAYER_CLIENTS", "android,ios,web").split(",")
    if client.strip()
]
YTDL_FALLBACK_BROWSERS = [
    browser.strip()
    for browser in os.getenv(
        "YTDL_FALLBACK_BROWSERS",
        "chrome,edge,firefox,brave,opera,vivaldi,chromium",
    ).split(",")
    if browser.strip()
]
YTDL_COOKIES_FILE = os.getenv("YTDL_COOKIES_FILE", "").strip()
YTDL_COOKIES_BROWSER = os.getenv("YTDL_COOKIES_BROWSER", "").strip()
ALLOW_UNSAFE_NON_STAGE = os.getenv("MUSIC_ALLOW_NON_STAGE_UNSAFE", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
VOICE_DAVE_AVAILABLE = bool(importlib.util.find_spec("davey"))
SUPPORTS_NON_STAGE_VOICE = ALLOW_UNSAFE_NON_STAGE or VOICE_DAVE_AVAILABLE
PLAY_ROUTE_AUTO = "auto"
PLAY_ROUTE_JOIN = "join"
PLAY_ROUTE_BOT_STAGE = "bot_stage"


def music_runtime_summary() -> dict:
    cookies_mode = "none"
    if YTDL_COOKIES_FILE and os.path.isfile(YTDL_COOKIES_FILE):
        cookies_mode = f"file:{YTDL_COOKIES_FILE}"
    elif YTDL_COOKIES_BROWSER:
        cookies_mode = f"browser:{YTDL_COOKIES_BROWSER}"
    return {
        "clients": YTDL_PLAYER_CLIENTS or ["android", "ios", "web"],
        "cookies_mode": cookies_mode,
        "fallback_browsers": YTDL_FALLBACK_BROWSERS,
        "allow_unsafe_non_stage": ALLOW_UNSAFE_NON_STAGE,
        "davey_available": VOICE_DAVE_AVAILABLE,
        "supports_non_stage_voice": SUPPORTS_NON_STAGE_VOICE,
    }


class MusicControlView(discord.ui.View):
    def __init__(self, facade: "MusicRoomFacade", guild_id: int):
        super().__init__(timeout=1800)
        self.facade = facade
        self.owner = facade.owner
        self.guild_id = guild_id
        self._sync_pause_button()

    def _guild(self) -> Optional[discord.Guild]:
        return self.owner.bot.get_guild(self.guild_id)

    def _voice(self) -> Optional[discord.VoiceClient]:
        guild = self._guild()
        if guild is None:
            return None
        return guild.voice_client

    @staticmethod
    async def _send_ephemeral(interaction: discord.Interaction, content: Optional[str] = None, *, embed: Optional[discord.Embed] = None) -> None:
        if interaction.response.is_done():
            await interaction.followup.send(content=content, embed=embed, ephemeral=True)
            return
        await interaction.response.send_message(content=content, embed=embed, ephemeral=True)

    def _sync_pause_button(self) -> None:
        button = self.pause_resume_button
        voice = self._voice()
        if voice is not None and voice.is_paused():
            button.label = "Resume"
            button.emoji = "▶"
            button.style = discord.ButtonStyle.success
            return
        button.label = "Pause"
        button.emoji = "⏸"
        button.style = discord.ButtonStyle.secondary

    async def _refresh_message(self, interaction: discord.Interaction) -> None:
        self._sync_pause_button()
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild_id != self.guild_id:
            await self._send_ephemeral(interaction, "❌ These controls belong to a different server.")
            return False

        guild = self._guild()
        if guild is None:
            await self._send_ephemeral(interaction, "❌ This server is no longer available.")
            return False

        custom_id = str(getattr(interaction, "data", {}).get("custom_id", ""))
        if custom_id == "music_queue":
            return True

        voice = guild.voice_client
        if voice is None or not voice.is_connected():
            await self._send_ephemeral(interaction, "❌ There is no active voice session right now.")
            return False

        user_voice = getattr(interaction.user, "voice", None)
        user_channel = getattr(user_voice, "channel", None)
        bot_channel = getattr(voice, "channel", None)
        if user_channel is None or bot_channel is None or user_channel.id != bot_channel.id:
            await self._send_ephemeral(
                interaction,
                "❌ Join the same voice channel as the bot to use music controls.",
            )
            return False
        return True

    async def on_timeout(self) -> None:
        current_view = getattr(self.owner, "now_playing_views", {}).get(self.guild_id)
        if current_view is not self:
            return
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        message = getattr(self, "message", None)
        if message is not None:
            try:
                await message.edit(view=self)
            except Exception:
                pass

    async def _step_eq(
        self,
        interaction: discord.Interaction,
        *,
        bass_delta: float = 0.0,
        treble_delta: float = 0.0,
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        eq = self.owner._get_guild_eq(self.guild_id)
        self.owner._set_guild_eq(
            self.guild_id,
            bass_db=eq["bass_db"] + bass_delta,
            treble_db=eq["treble_db"] + treble_delta,
        )
        restarted = await self.owner._reapply_current_track_for_guild(self.guild_id)
        updated = self.owner._get_guild_eq(self.guild_id)
        summary = (
            "🎛 Audio profile updated.\n"
            f"- bass: `{updated['bass_db']:+.1f} dB`\n"
            f"- treble: `{updated['treble_db']:+.1f} dB`"
        )
        if restarted:
            summary += "\n🔄 The current track is restarting to apply the new EQ."
        await self._refresh_message(interaction)
        await interaction.followup.send(summary, ephemeral=True)

    @discord.ui.button(label="Bass +", style=discord.ButtonStyle.primary, row=0, custom_id="music_bass_up")
    async def bass_up_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._step_eq(interaction, bass_delta=2.0)

    @discord.ui.button(label="Bass -", style=discord.ButtonStyle.primary, row=0, custom_id="music_bass_down")
    async def bass_down_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._step_eq(interaction, bass_delta=-2.0)

    @discord.ui.button(label="Treble +", style=discord.ButtonStyle.primary, row=0, custom_id="music_treble_up")
    async def treble_up_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._step_eq(interaction, treble_delta=2.0)

    @discord.ui.button(label="Treble -", style=discord.ButtonStyle.primary, row=0, custom_id="music_treble_down")
    async def treble_down_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._step_eq(interaction, treble_delta=-2.0)

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, row=0, custom_id="music_queue")
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = self.facade.build_queue_embed(self.guild_id)
        await self._send_ephemeral(interaction, embed=embed)

    @discord.ui.button(label="Pause", emoji="⏸", style=discord.ButtonStyle.secondary, row=1, custom_id="music_pause_resume")
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        voice = self._voice()
        if voice is None:
            await interaction.followup.send("❌ There is no active playback session.", ephemeral=True)
            return

        if voice.is_paused():
            voice.resume()
            message = "▶ Playback resumed."
        elif voice.is_playing():
            voice.pause()
            message = "⏸ Playback paused."
        else:
            message = "❌ There is no active playback."

        await self._refresh_message(interaction)
        await interaction.followup.send(message, ephemeral=True)

    @discord.ui.button(label="Stop", emoji="⏹", style=discord.ButtonStyle.danger, row=1, custom_id="music_stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        stopped = await self.owner._stop_guild_playback(self.guild_id, disconnect=False)
        if stopped:
            await interaction.followup.send("⏹ Stopped playback and cleared the queue.", ephemeral=True)
            return
        await interaction.followup.send("❌ There was no active playback to stop.", ephemeral=True)


class MusicRoomFacade:
    def __init__(self, owner):
        self.owner = owner

    @property
    def bot(self):
        return self.owner.bot

    @staticmethod
    def _avatar_url(user: object) -> Optional[str]:
        avatar = getattr(user, "display_avatar", None)
        if avatar is None:
            return None
        try:
            return str(avatar.url)
        except Exception:
            return None

    @staticmethod
    def _youtube_thumbnail_url(webpage_url: Optional[str]) -> Optional[str]:
        if not isinstance(webpage_url, str) or "youtube" not in webpage_url and "youtu.be" not in webpage_url:
            return None
        video_id: Optional[str] = None
        if "youtu.be/" in webpage_url:
            video_id = webpage_url.rsplit("/", 1)[-1].split("?", 1)[0]
        elif "v=" in webpage_url:
            video_id = webpage_url.split("v=", 1)[-1].split("&", 1)[0]
        if not video_id:
            return None
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    @staticmethod
    def _normalize_play_route(route: Optional[str]) -> str:
        normalized = str(route or PLAY_ROUTE_AUTO).strip().lower()
        if normalized in {PLAY_ROUTE_AUTO, PLAY_ROUTE_JOIN, PLAY_ROUTE_BOT_STAGE}:
            return normalized
        return PLAY_ROUTE_AUTO

    def build_now_playing_view(self, guild_id: Optional[int]) -> Optional[MusicControlView]:
        if guild_id is None:
            return None
        return MusicControlView(self, guild_id)

    async def _send_non_stage_warning(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel,
    ) -> None:
        embed = discord.Embed(
            title="Music Transport Blocked",
            description=(
                "Discord requires DAVE/E2EE for regular non-Stage voice channels.\n"
                "This runtime will be closed with `4017` if it tries to connect there."
            ),
            color=discord.Color.red(),
        )
        embed.add_field(name="Current Room", value=channel.mention, inline=True)
        embed.add_field(name="Recommended", value="Move to a Stage channel first, then use `/play`.", inline=True)
        if SUPPORTS_NON_STAGE_VOICE:
            embed.add_field(
                name="Voice Runtime",
                value="This runtime supports non-Stage voice. Restart the bot to load the updated stack.",
                inline=False,
            )
        elif ALLOW_UNSAFE_NON_STAGE:
            embed.add_field(
                name="Unsafe Override",
                value="`MUSIC_ALLOW_NON_STAGE_UNSAFE` is enabled, but this is still not recommended.",
                inline=False,
            )
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _send_join_room_unavailable(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel,
    ) -> None:
        embed = discord.Embed(
            title="Join Current Room Unavailable",
            description=(
                "Route `join` sends the bot directly into your current voice channel.\n"
                "Regular non-Stage voice rooms still hit Discord close code `4017` on unsupported runtimes."
            ),
            color=discord.Color.orange(),
        )
        embed.add_field(name="Current Room", value=channel.mention, inline=True)
        embed.add_field(
            name="Recommended",
            value="Use route `bot_stage`, or move into a Stage channel and use route `join` there.",
            inline=True,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _validate_voice_channel(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            return False
        voice_state = getattr(interaction.user, "voice", None)
        voice_channel = getattr(voice_state, "channel", None)
        if voice_channel is None:
            return True
        if isinstance(voice_channel, discord.VoiceChannel) and not SUPPORTS_NON_STAGE_VOICE:
            await self._send_non_stage_warning(interaction, voice_channel)
            return False
        return True

    def _bot_can_use_channel(self, channel: object) -> bool:
        guild = getattr(channel, "guild", None)
        if guild is None or self.bot.user is None:
            return False
        me = guild.me or guild.get_member(self.bot.user.id)
        if me is None:
            return False
        perms = channel.permissions_for(me)
        return bool(perms.connect and perms.speak)

    async def _find_or_create_best_stage_channel(
        self,
        interaction: discord.Interaction,
        source_channel: discord.VoiceChannel,
    ) -> tuple[Optional[discord.StageChannel], bool]:
        guild = interaction.guild
        if guild is None or self.bot.user is None:
            return None, False

        current_voice = guild.voice_client
        if (
            current_voice is not None
            and current_voice.is_connected()
            and isinstance(current_voice.channel, discord.StageChannel)
            and self._bot_can_use_channel(current_voice.channel)
        ):
            return current_voice.channel, False

        stage_channels = [
            channel
            for channel in guild.channels
            if isinstance(channel, discord.StageChannel) and self._bot_can_use_channel(channel)
        ]
        if stage_channels:
            def _score(channel: discord.StageChannel) -> tuple[int, int, int, int]:
                same_category = int(channel.category_id != source_channel.category_id)
                member_count = len([member for member in channel.members if not member.bot])
                is_empty = int(member_count == 0)
                return (same_category, is_empty, -member_count, channel.position)

            stage_channels.sort(key=_score)
            return stage_channels[0], False

        me = guild.me or guild.get_member(self.bot.user.id)
        if me is None or not me.guild_permissions.manage_channels:
            return None, False

        preferred_name = os.getenv("PANOS_STAGE_CHANNEL_NAME", "Panos Music").strip() or "Panos Music"
        existing_named = discord.utils.get(guild.channels, name=preferred_name)
        if isinstance(existing_named, discord.StageChannel) and self._bot_can_use_channel(existing_named):
            return existing_named, False

        try:
            created = await guild.create_stage_channel(
                preferred_name,
                category=source_channel.category,
                reason="Panos automatic music route",
            )
        except (discord.Forbidden, discord.HTTPException) as e:
            print(f"[music] failed to create stage channel: {e}")
            return None, False
        return created, True

    async def _find_or_create_bot_stage_channel(
        self,
        interaction: discord.Interaction,
        source_channel: object,
    ) -> tuple[Optional[discord.StageChannel], bool]:
        guild = interaction.guild
        if guild is None or self.bot.user is None:
            return None, False

        current_voice = guild.voice_client
        if (
            current_voice is not None
            and current_voice.is_connected()
            and isinstance(current_voice.channel, discord.StageChannel)
            and self._bot_can_use_channel(current_voice.channel)
        ):
            return current_voice.channel, False

        preferred_name = os.getenv("PANOS_STAGE_CHANNEL_NAME", "Panos Music").strip() or "Panos Music"
        existing_named = discord.utils.get(guild.channels, name=preferred_name)
        if isinstance(existing_named, discord.StageChannel) and self._bot_can_use_channel(existing_named):
            return existing_named, False

        me = guild.me or guild.get_member(self.bot.user.id)
        if me is None or not me.guild_permissions.manage_channels:
            return None, False

        try:
            created = await guild.create_stage_channel(
                preferred_name,
                category=getattr(source_channel, "category", None),
                reason="Panos dedicated music stage",
            )
        except (discord.Forbidden, discord.HTTPException) as e:
            print(f"[music] failed to create bot stage channel: {e}")
            return None, False
        return created, True

    async def _queue_stage_route(
        self,
        interaction: discord.Interaction,
        source_channel: object,
        item: dict,
        *,
        prefer_bot_stage: bool = False,
    ) -> bool:
        if prefer_bot_stage:
            stage_channel, created = await self._find_or_create_bot_stage_channel(interaction, source_channel)
        else:
            stage_channel, created = await self._find_or_create_best_stage_channel(interaction, source_channel)
        if stage_channel is None:
            if isinstance(source_channel, discord.VoiceChannel):
                await self._send_non_stage_warning(interaction, source_channel)
            return False

        queue = self.owner.get_queue(interaction.guild_id)
        queued_item = dict(item)
        queued_item["voice_channel_id"] = stage_channel.id
        queue.append(queued_item)
        requester_voice_channel = getattr(getattr(interaction.user, "voice", None), "channel", None)
        current_voice = interaction.guild.voice_client if interaction.guild else None
        can_start_now = bool(
            (requester_voice_channel is not None and requester_voice_channel.id == stage_channel.id)
            or (
                current_voice is not None
                and current_voice.is_connected()
                and getattr(current_voice.channel, "id", None) == stage_channel.id
            )
        )

        if can_start_now:
            self.owner.pending_stage_routes.pop(interaction.guild_id, None)
        else:
            self.owner.pending_stage_routes[interaction.guild_id] = {
                "requester_id": interaction.user.id,
                "stage_channel_id": stage_channel.id,
                "announce_channel_id": interaction.channel_id,
                "title": queued_item.get("title"),
            }

        embed = discord.Embed(
            title="Bot Music Stage Ready" if prefer_bot_stage else "Music Ready",
            description=(
                "The track is ready and is starting in the selected Stage channel."
                if can_start_now
                else "The track is queued and will start as soon as you move into the suggested Stage channel."
            ),
            color=discord.Color.green(),
        )
        embed.add_field(name="Current Room", value=getattr(source_channel, "mention", str(source_channel)), inline=True)
        embed.add_field(
            name="Bot Stage" if prefer_bot_stage else "Best Route",
            value=stage_channel.mention,
            inline=True,
        )
        embed.add_field(name="Queued", value=f"`{queued_item['title']}`", inline=False)
        embed.add_field(
            name="Next Step",
            value=(
                "The bot will connect and start playback automatically in this Stage channel."
                if can_start_now
                else "Move into this Stage channel and the bot will connect and start playback automatically."
            ),
            inline=False,
        )
        if created:
            embed.set_footer(text="Panos created its own Stage channel for music playback")
        else:
            embed.set_footer(
                text=(
                    "Panos reused its dedicated Stage room"
                    if prefer_bot_stage
                    else "Panos reused the best available Stage channel"
                )
            )
        await interaction.followup.send(embed=embed, ephemeral=False)
        if can_start_now:
            await self.owner.play_next(
                guild_id=interaction.guild_id,
                announce_channel_id=interaction.channel_id,
            )
        return True

    def build_now_playing_embed(
        self,
        *,
        item: dict,
        voice_channel: Optional[object],
        guild_id: Optional[int],
    ) -> discord.Embed:
        user = item.get("requested_by")
        title = str(item.get("title", "Unknown Title"))
        webpage_url = item.get("webpage_url")

        color = discord.Color.blurple()
        if isinstance(user, discord.Member) and user.color.value:
            color = user.color

        description = title
        if isinstance(webpage_url, str) and webpage_url:
            description = f"[{title}]({webpage_url})"

        embed = discord.Embed(
            title="Now Playing",
            description=description,
            color=color,
        )

        avatar_url = self._avatar_url(user)
        if avatar_url:
            embed.set_author(name=str(user), icon_url=avatar_url)
        elif user is not None:
            embed.set_author(name=str(user))

        thumbnail_url = self._youtube_thumbnail_url(webpage_url)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        elif avatar_url:
            embed.set_thumbnail(url=avatar_url)

        speed = self.owner._get_guild_speed(guild_id)
        eq = self.owner._get_guild_eq(guild_id)
        requester_text = getattr(user, "mention", str(user) if user else "-")
        room_text = getattr(voice_channel, "mention", str(voice_channel) if voice_channel else "-")
        embed.add_field(name="Requester", value=requester_text, inline=True)
        embed.add_field(name="Room", value=room_text, inline=True)
        embed.add_field(name="Source", value="[open link](%s)" % webpage_url if webpage_url else "-", inline=True)
        embed.add_field(
            name="Profile",
            value=(
                f"speed `{speed:.2f}x`\n"
                f"bass `{eq['bass_db']:+.1f} dB`\n"
                f"treble `{eq['treble_db']:+.1f} dB`"
            ),
            inline=False,
        )
        queue_count = len(self.owner.get_queue(guild_id)) if guild_id is not None else 0
        embed.add_field(name="Up Next", value=f"`{queue_count}` track(s) queued", inline=False)
        embed.set_footer(text="Music Room • Controls are attached below")
        return embed

    def build_queue_embed(self, guild_id: Optional[int]) -> discord.Embed:
        embed = discord.Embed(title="Queue", color=discord.Color.blurple())
        if guild_id is None:
            embed.description = "No guild was provided."
            return embed

        current = self.owner.now_playing.get(guild_id)
        queue = self.owner.get_queue(guild_id)
        lines = []
        if current:
            requester = current.get("requested_by")
            requester_text = getattr(requester, "mention", str(requester) if requester else "-")
            lines.append(f"Now: `{current['title']}` • {requester_text}")

        for idx, item in enumerate(queue[:10], start=1):
            requester = item.get("requested_by")
            requester_text = getattr(requester, "mention", str(requester) if requester else "-")
            lines.append(f"{idx}. `{item['title']}` • {requester_text}")

        if len(queue) > 10:
            lines.append(f"... and {len(queue) - 10} more")

        if not lines:
            embed.description = "📭 The queue is empty."
            return embed

        embed.description = "\n".join(lines)
        embed.set_footer(text=f"{len(queue)} queued track(s)")
        return embed

    async def play(self, interaction: discord.Interaction, query: str, route: Optional[str] = None):
        await interaction.response.defer(thinking=True)

        try:
            route = self._normalize_play_route(route)
            if not self.owner._ffmpeg_is_available():
                await interaction.followup.send(
                    "❌ `ffmpeg` was not found. Install ffmpeg or set `FFMPEG_PATH`.",
                    ephemeral=True,
                )
                return

            guild = interaction.guild
            if guild is None:
                await interaction.followup.send(
                    "This command can only be used in servers.",
                    ephemeral=True,
                )
                return

            requester_voice = getattr(interaction.user, "voice", None)
            requester_voice_channel = getattr(requester_voice, "channel", None)
            active_voice = guild.voice_client
            active_stage_channel = None
            if (
                active_voice is not None
                and active_voice.is_connected()
                and isinstance(active_voice.channel, discord.StageChannel)
            ):
                active_stage_channel = active_voice.channel

            if requester_voice_channel is None and active_stage_channel is None:
                await interaction.followup.send(
                    "❌ You must be in a voice channel first, or the bot must already be connected to a Stage channel.",
                    ephemeral=True,
                )
                return

            stream_url, title, http_headers, webpage_url = await self.owner.youtube_search(query)
            local_path: Optional[str] = None
            try:
                local_path = await self.owner.download_audio_file(webpage_url)
                if local_path:
                    print(f"[music] local audio ready: {local_path}")
            except Exception as e:
                print(f"[music] local audio download failed, fallback to stream: {e}")

            queue_item = {
                "url": stream_url,
                "title": title,
                "http_headers": http_headers,
                "local_path": local_path,
                "webpage_url": webpage_url,
                "announce_channel_id": interaction.channel_id,
                "requested_by": interaction.user,
            }

            if route == PLAY_ROUTE_BOT_STAGE:
                stage_source = requester_voice_channel or active_stage_channel
                if stage_source is None:
                    await interaction.followup.send(
                        "❌ You must be in a voice channel first so the bot can choose or create its own Stage room.",
                        ephemeral=True,
                    )
                    return
                await self._queue_stage_route(
                    interaction,
                    stage_source,
                    queue_item,
                    prefer_bot_stage=True,
                )
                return

            if route == PLAY_ROUTE_JOIN:
                if requester_voice_channel is None:
                    await interaction.followup.send(
                        "❌ Route `join` requires you to already be in the room you want the bot to enter.",
                        ephemeral=True,
                    )
                    return
                if isinstance(requester_voice_channel, discord.VoiceChannel) and not SUPPORTS_NON_STAGE_VOICE:
                    await self._send_join_room_unavailable(interaction, requester_voice_channel)
                    return
                voice = await self.owner.ensure_voice(interaction)
                if voice is None:
                    return
                queue_item["voice_channel_id"] = voice.channel.id if voice.channel else None
            else:
                voice = active_voice if active_stage_channel is not None else None
                if (
                    active_stage_channel is None
                    and isinstance(requester_voice_channel, discord.VoiceChannel)
                    and not SUPPORTS_NON_STAGE_VOICE
                ):
                    await self._queue_stage_route(interaction, requester_voice_channel, queue_item)
                    return
                if active_stage_channel is not None:
                    queue_item["voice_channel_id"] = active_stage_channel.id
                else:
                    voice = await self.owner.ensure_voice(interaction)
                    if voice is None:
                        return
                    queue_item["voice_channel_id"] = voice.channel.id if voice.channel else None

            queue = self.owner.get_queue(interaction.guild_id)
            queue.append(queue_item)

            if voice and (voice.is_playing() or voice.is_paused()):
                await interaction.followup.send(f"➕ Added to queue: `{title}`")
            else:
                await interaction.followup.send(f"▶ Starting playback: `{title}`")
                await self.owner.play_next(
                    guild_id=interaction.guild_id,
                    announce_channel_id=interaction.channel_id,
                )
        except Exception as e:
            print(f"/play error: {e}")
            try:
                await interaction.followup.send(
                    f"❌ Playback failed:\n`{e}`",
                    ephemeral=True,
                )
            except discord.InteractionResponded:
                pass

    async def handle_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if not self.bot.user:
            return

        guild_id = member.guild.id
        pending_stage = self.owner.pending_stage_routes.get(guild_id)
        if member.id != self.bot.user.id:
            if (
                pending_stage
                and member.id == pending_stage.get("requester_id")
                and after.channel is not None
                and after.channel.id == pending_stage.get("stage_channel_id")
            ):
                print(
                    f"[music] stage route armed | guild={guild_id} | "
                    f"user={member.id} | channel={after.channel}"
                )
                await self.owner.play_next(
                    guild_id=guild_id,
                    announce_channel_id=pending_stage.get("announce_channel_id"),
                )
            return

        before_name = before.channel.name if before.channel else None
        after_name = after.channel.name if after.channel else None
        print(f"[voice] state update | guild={guild_id} | before={before_name} | after={after_name}")

        if after.channel is not None:
            self.owner.last_voice_channel_id[guild_id] = after.channel.id
            self.owner.intentional_voice_disconnects.discard(guild_id)
            return

        if guild_id in self.owner.intentional_voice_disconnects:
            self.owner.intentional_voice_disconnects.discard(guild_id)
            self.owner.last_voice_channel_id.pop(guild_id, None)
            self.owner.voice_recovery_attempts.pop(guild_id, None)
            task = self.owner.voice_recovery_tasks.pop(guild_id, None)
            if task and not task.done():
                task.cancel()
            return

        if before.channel is None:
            return

        self.owner.last_voice_channel_id[guild_id] = before.channel.id

        current = self.owner.now_playing.get(guild_id)
        if not current:
            return

        announce_channel_id = current.get("announce_channel_id")
        self.owner._schedule_voice_recovery(guild_id, announce_channel_id)

    async def skip(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        voice = interaction.guild.voice_client
        if voice is None or not voice.is_playing():
            await interaction.response.send_message("❌ Nothing is currently playing.", ephemeral=True)
            return
        if interaction.guild_id is not None:
            self.owner.now_playing.pop(interaction.guild_id, None)
            self.owner.intentional_track_stops[interaction.guild_id] = "skip"
        voice.stop()
        await interaction.response.send_message("⏭ Skipped the current track.", ephemeral=False)

    async def stop(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        stopped = await self.owner._stop_guild_playback(interaction.guild_id, disconnect=False)
        if not stopped:
            await interaction.response.send_message("❌ There is no active playback to stop.", ephemeral=True)
            return
        await interaction.response.send_message("⏹ Stopped playback and cleared the queue.", ephemeral=False)

    async def pause(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        voice = interaction.guild.voice_client
        if voice and voice.is_playing():
            voice.pause()
            await interaction.response.send_message("⏸ Playback paused.", ephemeral=False)
        else:
            await interaction.response.send_message("❌ There is no active playback.", ephemeral=True)

    async def resume(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        voice = interaction.guild.voice_client
        if voice and voice.is_paused():
            voice.resume()
            await interaction.response.send_message("▶ Playback resumed.", ephemeral=False)
        else:
            await interaction.response.send_message("❌ Playback is not paused.", ephemeral=True)

    async def set_speed(self, interaction: discord.Interaction, value: float):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        self.owner._set_guild_speed(interaction.guild_id, float(value))
        restarted = await self.owner._reapply_current_track(interaction)
        current_speed = self.owner._get_guild_speed(interaction.guild_id)
        message = (
            f"⚙️ Playback speed set to `{current_speed:.2f}x` "
            "(runtime only)"
        )
        if restarted:
            message += "\n🔄 The current track was restarted from the beginning to apply the new setting."
        await interaction.response.send_message(message, ephemeral=False)

    async def set_tone(self, interaction: discord.Interaction, mode: app_commands.Choice[str]):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        self.owner._set_guild_tone(interaction.guild_id, mode.value)
        restarted = await self.owner._reapply_current_track(interaction)
        tone = self.owner._get_guild_tone(interaction.guild_id)
        eq = self.owner._get_guild_eq(interaction.guild_id)
        message = (
            f"🎚 Tone preset set to `{self.owner._tone_label(tone)}` "
            f"(bass `{eq['bass_db']:+.1f}dB`, treble `{eq['treble_db']:+.1f}dB`)"
        )
        if restarted:
            message += "\n🔄 The current track was restarted from the beginning to apply the new setting."
        await interaction.response.send_message(message, ephemeral=False)

    async def set_eq(self, interaction: discord.Interaction, bass_db: float, treble_db: float):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        self.owner._set_guild_eq(interaction.guild_id, bass_db=float(bass_db), treble_db=float(treble_db))
        restarted = await self.owner._reapply_current_track(interaction)
        eq = self.owner._get_guild_eq(interaction.guild_id)
        message = (
            "🎛 Manual EQ updated.\n"
            f"- bass: `{eq['bass_db']:+.1f} dB`\n"
            f"- treble: `{eq['treble_db']:+.1f} dB`\n"
            "(this setting is persistent)"
        )
        if restarted:
            message += "\n🔄 The current track was restarted from the beginning to apply the new setting."
        await interaction.response.send_message(message, ephemeral=False)

    async def audio_profile(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        speed = self.owner._get_guild_speed(interaction.guild_id)
        tone = self.owner._get_guild_tone(interaction.guild_id)
        eq = self.owner._get_guild_eq(interaction.guild_id)
        await interaction.response.send_message(
            "🎛 Audio Profile\n"
            f"- speed: `{speed:.2f}x` (runtime only)\n"
            f"- tone preset: `{self.owner._tone_label(tone)}`\n"
            f"- bass: `{eq['bass_db']:+.1f} dB` (persistent)\n"
            f"- treble: `{eq['treble_db']:+.1f} dB` (persistent)",
            ephemeral=True,
        )

    async def queue_cmd(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        queue = self.owner.get_queue(interaction.guild_id)
        if not queue and interaction.guild_id not in self.owner.now_playing:
            await interaction.response.send_message("📭 The queue is empty.", ephemeral=True)
            return
        embed = self.build_queue_embed(interaction.guild_id)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    async def music_debug(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        voice = interaction.guild.voice_client
        if voice is None:
            await interaction.response.send_message(
                f"`voice=None` | `opus_loaded={discord.opus.is_loaded()}`",
                ephemeral=True,
            )
            return
        source_type = type(voice.source).__name__ if voice.source else "None"
        speed = self.owner._get_guild_speed(interaction.guild_id)
        tone = self.owner._get_guild_tone(interaction.guild_id)
        eq = self.owner._get_guild_eq(interaction.guild_id)
        msg = (
            f"`connected={voice.is_connected()}` "
            f"`playing={voice.is_playing()}` "
            f"`paused={voice.is_paused()}`\n"
            f"`channel={voice.channel}` "
            f"`type={type(voice.channel).__name__}` "
            f"`latency={round(voice.latency * 1000)}ms`\n"
            f"`opus_loaded={discord.opus.is_loaded()}` "
            f"`source={source_type}` "
            f"`ffmpeg={self.owner._get_ffmpeg_executable()}`\n"
            f"`speed={speed:.2f}` "
            f"`tone={tone}` "
            f"`bass={eq['bass_db']:+.1f}dB` "
            f"`treble={eq['treble_db']:+.1f}dB`\n"
            f"`allow_non_stage_unsafe={ALLOW_UNSAFE_NON_STAGE}` "
            f"`davey={VOICE_DAVE_AVAILABLE}` "
            f"`supports_non_stage={SUPPORTS_NON_STAGE_VOICE}`"
        )
        me_voice = interaction.guild.me.voice if interaction.guild.me else None
        if me_voice:
            msg += (
                f"\n`self_mute={me_voice.self_mute}` "
                f"`self_deaf={me_voice.self_deaf}` "
                f"`suppress={getattr(me_voice, 'suppress', False)}`"
            )
        await interaction.response.send_message(msg, ephemeral=True)

    async def test_tone(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not self.owner._ffmpeg_is_available():
            await interaction.followup.send("❌ ffmpeg was not found.", ephemeral=True)
            return
        if not await self._validate_voice_channel(interaction):
            return
        voice = await self.owner.ensure_voice(interaction)
        if voice is None:
            return
        if voice.is_playing():
            voice.stop()

        try:
            source = discord.FFmpegOpusAudio(
                "sine=frequency=880:sample_rate=48000:duration=8",
                executable=self.owner._get_ffmpeg_executable(),
                before_options="-f lavfi",
                options="-loglevel warning",
                stderr=sys.stderr,
            )
            voice.play(source)
            await interaction.followup.send("🔊 Playing an 8-second test tone (880Hz).", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ testtone error: `{e}`", ephemeral=True)

    async def leave(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in servers.", ephemeral=True)
            return
        if await self.owner._stop_guild_playback(interaction.guild_id, disconnect=True):
            await interaction.response.send_message("👋 Disconnected from voice.", ephemeral=False)
        else:
            await interaction.response.send_message("❌ The bot is not connected to voice.", ephemeral=True)
