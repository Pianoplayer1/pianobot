from discord import Member, Role

def permissions(target, channel):
    perms = ['create_instant_invite', 'kick_members', 'ban_members', 'administrator', 'manage_channels', 'manage_guild', 'add_reactions', 'view_audit_log', 'priority_speaker', 'stream', 'view_channel', 'send_messages', 'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files', 'read_message_history', 'mention_everyone', 'use_external_emojis', 'view_guild_insights', 'connect', 'speak', 'mute_members', 'deafen_members', 'move_members', 'use_vad', 'change_nickname', 'manage_nicknames', 'manage_roles', 'manage_webhooks', 'manage_emojis', 'use_slash_commands', 'request_to_speak']

    if isinstance(target, Member):
        value = channel.permissions_for(target).value
    elif isinstance(target, Role):
        value = target.permissions.value
    else:
        return []

    return [perms[perm] for perm in range(len(perms)) if value & pow(2, perm) > 0]

def check_permissions(member, channel, perms):

    if not isinstance(member, Member):
        member = channel.guild.get_member(member.id)
        if member is None:
            return False

    user_perms = permissions(member, channel)

    return member.id == 667445845792391208 or all(perm in user_perms for perm in perms)
