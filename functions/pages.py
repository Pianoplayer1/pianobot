import asyncio

async def paginator(client, ctx, normal_contents, message = None, reverse_contents = None):
    contents = normal_contents
    page = 1

    if message is None:
        message = await ctx.send(contents[page-1])
    else:
        await message.edit(content=contents[page-1])

    if len(contents) == 1:
        return

    await message.add_reaction('⏮️')
    await message.add_reaction('◀️')
    if reverse_contents is not None:
        await message.add_reaction('🔁')
    await message.add_reaction('▶️')
    await message.add_reaction('⏭️')

    def check(reaction, user):
        return user != client.user and str(reaction.emoji) in ['⏮️', '◀️', '🔁','▶️', '⏭️'] and reaction.message == message

    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=300, check=check)
            await message.remove_reaction(reaction, user)

            if str(reaction.emoji) == '⏭️' and page < len(contents):
                page = len(contents)
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '▶️' and page != len(contents):
                page += 1
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '🔁':
                if contents == normal_contents:
                    contents = reverse_contents
                else:
                    contents = normal_contents
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '◀️' and page > 1:
                page -= 1
                await message.edit(content=f'{contents[page-1]}')
            elif str(reaction.emoji) == '⏮️' and page > 1:
                page = 1
                await message.edit(content=f'{contents[page-1]}')

        except asyncio.TimeoutError:
            await message.remove_reaction('⏭️', client.user)
            await message.remove_reaction('▶️', client.user)
            if reverse_contents is not None:
                await message.remove_reaction('🔁', client.user)
            await message.remove_reaction('◀️', client.user)
            await message.remove_reaction('⏮️', client.user)
            await message.edit(content=f'{contents[page - 1][:-3] + " (locked)```"}')
            break