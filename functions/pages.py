import asyncio

async def paginator(client, ctx, contents, message = None):
    pages = len(contents)
    page = 1

    if message is None:
        message = await ctx.send(contents[page-1])
    else:
        await message.edit(content=contents[page-1])

    if pages == 1:
        return

    await message.add_reaction('⏮️')
    await message.add_reaction('◀️')
    await message.add_reaction('▶️')
    await message.add_reaction('⏭️')

    def check(reaction, user):
        return user != client.user and str(reaction.emoji) in ['⏮️', '◀️', '▶️', '⏭️'] and reaction.message == message

    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=300, check=check)

            if str(reaction.emoji) == '⏭️' and page < pages:
                page = pages
                await message.edit(content=f'{contents[pages-1]}')
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '▶️' and page != pages:
                page += 1
                await message.edit(content=f'{contents[page-1]}')
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '◀️' and page > 1:
                page -= 1
                await message.edit(content=f'{contents[page-1]}')
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '⏮️' and page > 1:
                page = 1
                await message.edit(content=f'{contents[0]}')
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            await message.remove_reaction('⏭️', client.user)
            await message.remove_reaction('▶️', client.user)
            await message.remove_reaction('◀️', client.user)
            await message.remove_reaction('⏮️', client.user)
            await message.edit(content=f'{contents[page - 1][:-3] + " (locked)```"}')
            break