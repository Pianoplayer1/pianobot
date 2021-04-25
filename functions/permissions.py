import discord

def permissions(user, channel, guild):
    perms = ['create_instant_invite', 'kick_members', 'ban_members', 'administrator', 'manage_channels', 'manage_guild', 'add_reactions', 'view_audit_log', 'priority_speaker', 'stream', 'view_channel', 'send_messages', 'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files', 'read_message_history', 'mention_everyone', 'use_external_emojis', 'view_guild_insights', 'connect', 'speak', 'mute_members', 'deafen_members', 'move_members', 'use_vad', 'change_nickname', 'manage_nicknames', 'manage_roles', 'manage_webhooks', 'manage_emojis', 'use_slash_commands', 'request_to_speak']

    if not isinstance(user,  discord.member.Member) and not isinstance(user, discord.role.Role):
        user = guild.get_member(user.id)
    if isinstance(user,  discord.member.Member):
        test = channel.permissions_for(user).value
    elif isinstance(user,  discord.role.Role):
        test = user.permissions.value
    else:
        test = None

    return [perms[perm] for perm in range(len(perms)) if test & pow(2, perm) > 0]

def check_permissions(user, channel, check_perms):
    user_perms = permissions(user, channel, channel.guild)

    return all(perm in user_perms for perm in check_perms)
