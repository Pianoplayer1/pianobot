from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ClientUser, DMChannel, GroupChannel, Guild, Member, TextChannel, User

if TYPE_CHECKING:
    from pianobot.db import ServerTable


def check_permissions(
    user: ClientUser | Member | User,
    channel: DMChannel | GroupChannel | TextChannel,
    *permissions: str,
    all_guilds: bool = True,
) -> bool:
    if not isinstance(channel, TextChannel):
        return False
    member = channel.guild.get_member(user.id)
    if member is None:
        return False

    all_permissions = [
        'create_instant_invite',
        'kick_members',
        'ban_members',
        'administrator',
        'manage_channels',
        'manage_guild',
        'add_reactions',
        'view_audit_log',
        'priority_speaker',
        'stream',
        'view_channel',
        'send_messages',
        'send_tts_messages',
        'manage_messages',
        'embed_links',
        'attach_files',
        'read_message_history',
        'mention_everyone',
        'use_external_emojis',
        'view_guild_insights',
        'connect',
        'speak',
        'mute_members',
        'deafen_members',
        'move_members',
        'use_vad',
        'change_nickname',
        'manage_nicknames',
        'manage_roles',
        'manage_webhooks',
        'manage_emojis',
        'use_slash_commands',
        'request_to_speak',
        'manage_events',
        'manage_threads',
        'create_public_threads',
        'create_private_threads',
        'use_external_stickers',
        'send_messages_in_threads',
        'start_embedded_activities',
        'moderate_members',
    ]
    value = channel.permissions_for(member).value

    existing = [perm for i, perm in enumerate(all_permissions) if value & pow(2, i) > 0]
    return (
        all(permission in existing for permission in permissions) or 'administrator' in existing
    ) and (all_guilds or channel.guild.id in (682671629213368351, 713710628258185258))


def get_prefix(servers: ServerTable, guild: Guild | None) -> str:
    if guild is not None:
        server = servers.get(guild.id)
        if server is not None:
            return server.prefix
    return '-'
