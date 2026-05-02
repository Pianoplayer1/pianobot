# Pianobot

A Discord bot for the **Eden** guild on Wynncraft.

## What it does

**For Eden members**

- **Promotion cycles.** Tracks raid, war, and guild-XP contributions per half-month cycle and posts ranked award embeds when each cycle closes, including a weighted raffle over raid completions.
- **Reward bookkeeping.** Tracks pending emerald, aspect, and XP-milestone rewards owed to each member, with slash commands to view, reset, block, and set the per-raid / per-billion-XP rates.
- **Guild tome queue.** Persistent "Join queue" button plus grant/deny commands.
- **Live event log.** Webhooks for member joins, leaves, renames, rank changes, 4-person raid-completion groups, and Eden-relevant territory captures or losses.
- **Live XP feed.** Periodic embeds showing each member's contributed-XP gain over the last few minutes.

**For everyone**

- **Player profiles.** Wynncraft profile info, plus a bar chart of a player's daily online minutes and an alt-account probability check.
- **Guild stats.** Inactivity report, weekly playtime, raid / war / XP totals over arbitrary intervals, and a line graph of any tracked guild's online member count.
- **World status.** Live world uptime list.

---

## Self-hosting

1. Install dependencies: `uv sync`
2. Export the required environment variables (see below).
3. Run the bot: `uv run client.py`

### Required environment variables

```
DISCORD_TOKEN=...
PIANOBOT_DB_URL=postgresql://user:pass@host:5432/pianobot
EDEN_DISCORD_ID=682671629213368351
EDEN_WYNN_UUID=221efb28-7f93-4d5d-b219-9ddf43f7418b
```

### Optional environment variables

```
WYNN_API_TOKEN=...              # bearer token; doubles the rate limit
MEMBER_CHANNEL_WEBHOOK=...      # join/leave/promote/demote/rename logs + award embeds
XP_CHANNEL_WEBHOOK=...          # periodic guild-XP gain embeds
RAID_CHANNEL_WEBHOOK=...        # 4-person raid-completion embeds
TERRITORY_CHANNEL_WEBHOOK=...   # Eden-relevant territory change embeds
TOME_CHANNEL_ID=...             # tome-queue log channel (id, not webhook)
TOME_MESSAGE_ID=...             # message id for the persistent "Join queue" button
```
