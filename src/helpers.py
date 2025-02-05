import discord
import asyncio

from typing import Union, Iterable
#from discord.ext import menus
from src.battle import *
from src.constants import *

Context = discord.ext.commands.Context


def key_string(ctx: Context) -> str:
    return str(ctx.guild) + '|' + str(ctx.channel.id)

'''class PlayerStatsPaged(menus.ListPageSource):
    def __init__(self, member: discord.Member, bot: 'ScoreSheetBot'):
        season_stats = discord.Embed(title=f"Season Stats for {str(member)}", color=member.color)
        weighted, taken, lost, mvps = player_stocks(member, True)
        total, wins = player_record(member, True)
        title = f'Crew Battle Stats for {str(member)}'
        season_stats.add_field(name='Crews record while participating', value=f'{wins}/{total - wins}', inline=True)

        season_stats.add_field(name='MVPs', value=f'{mvps}', inline=True)
        season_stats.add_field(name='Stocks', value=f'(See .weighted)', inline=False)
        season_stats.add_field(name='Taken', value=f'{taken}', inline=True)
        season_stats.add_field(name='Lost', value=f'{lost}', inline=True)
        season_stats.add_field(name='Weighted Taken', value=f'{round(weighted, 2)}', inline=True)
        season_stats.add_field(name='Ratio', value=f'{round(taken / max(lost, 1), 2)}', inline=True)
        season_stats.add_field(name='Weighted Ratio', value=f'{round(weighted / max(lost, 1), 2)}', inline=True)
        pc = player_chars(member, True)
        season_stats.add_field(name='Characters played', value='how many battles played in ', inline=False)
        for char in pc:
            emoji = string_to_emote(char[1], bot.bot)
            season_stats.add_field(name=emoji, value=f'{char[0]}', inline=True)
        weighted, taken, lost, mvps = player_stocks(member)
        total, wins = player_record(member)
        title = f'Crew Battle Stats for {str(member)}'
        cb_stats = discord.Embed(title=title, color=member.color)
        cb_stats.add_field(name='Crews record while participating', value=f'{wins}/{total - wins}', inline=True)

        cb_stats.add_field(name='MVPs', value=f'{mvps}', inline=True)
        cb_stats.add_field(name='Stocks', value=f'(See .weighted)', inline=False)
        cb_stats.add_field(name='Taken', value=f'{taken}', inline=True)
        cb_stats.add_field(name='Lost', value=f'{lost}', inline=True)
        cb_stats.add_field(name='Weighted Taken', value=f'{round(weighted, 2)}', inline=True)
        cb_stats.add_field(name='Ratio', value=f'{round(taken / max(lost, 1), 2)}', inline=True)
        cb_stats.add_field(name='Weighted Ratio', value=f'{round(weighted / max(lost, 1), 2)}', inline=True)
        pc = player_chars(member)
        cb_stats.add_field(name='Characters played', value='how many battles played in ', inline=False)
        for char in pc:
            emoji = string_to_emote(char[1], bot.bot)
            cb_stats.add_field(name=emoji, value=f'{char[0]}', inline=True)

        ba_stats = discord.Embed(title=f'Battle Arena Stats for {str(member)}', color=member.color)
        elo = ba_elo(member)
        if elo:

            wins, losses = ba_record(member)
            elo = ba_elo(member)
            ba_stats.add_field(name='record', value=f'{wins}/{losses}', inline=True)
            ba_stats.add_field(name='winrate', value=f'{round(wins / (losses + wins), 2) * 100}%', inline=True)

            ba_stats.add_field(name='Rating', value=f'{elo}', inline=False)
            # TODO Add ranking here

            ba_stats.add_field(name='Characters played', value='how many matches played in ', inline=False)
            chars = ba_chars(member)
            for char in chars:
                emoji = string_to_emote(char[1], bot.bot)
                ba_stats.add_field(name=emoji, value=f'{char[0]}', inline=True)
        else:
            ba_stats.description = 'This member has no battle arena history.'
        data = [season_stats, cb_stats, ba_stats]
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries) -> discord.Embed:
        return entries'''


async def update_channel_open(prefix: str, channel: discord.TextChannel):
    if channel.name.startswith(YES) or channel.name.startswith(NO):
        new_name = prefix + channel.name[1:]
    else:
        new_name = prefix + channel.name
    try:
        await asyncio.wait_for(channel.edit(name=new_name), timeout=2)
    except asyncio.TimeoutError:
        return


def split_on_length_and_separator(string: str, length: int, separator: str) -> List[str]:
    ret = []
    while len(string) > length:
        idx = length - 1
        while string[idx] != separator:
            if idx == 0:
                raise ValueError
            idx -= 1
        ret.append(string[:idx + 1])
        string = string[idx + 1:]
    ret.append(string)
    return ret


def split_embed(embed: discord.Embed, length: int) -> List[discord.Embed]:
    ret = []
    desc = embed.description
    desc_split = split_on_length_and_separator(desc, length, '\n')
    ret.append(discord.Embed(title=embed.title, color=embed.color, description=desc_split.pop(0)))

    for split in desc_split:
        ret.append(discord.Embed(color=embed.color, description=split))
    total_fields = len(embed.fields)
    if len(ret) <= total_fields // 25:
        ret.append(discord.Embed(colour=embed.colour))
    for i, split in enumerate(ret):
        top = min(total_fields, (i + 1) * 25)
        if i * 25 < total_fields:
            for f in embed.fields[i * 25:top]:
                split.add_field(name=f.name, value=f.value, inline=f.inline)

    return ret


async def send_sheet(channel: Union[discord.TextChannel, Context], battle: Battle) -> discord.Message:
    embed_split = split_embed(embed=battle.embed(), length=2000)
    if battle.battle_over():
        if not all(battle.confirms):
            footer = ''
            footer += '\nPlease confirm: '
            if battle.battle_type == BattleType.MOCK:
                footer += 'anyone can confirm or clear a mock.'
            else:
                if not battle.confirms[0]:
                    footer += f'\n {battle.team1.name}: '
                    for leader in battle.team1.leader:
                        footer += f'{leader}, '
                    footer = footer[:-2]
                    footer += ' please `,confirm`.'
                if not battle.confirms[1]:
                    footer += f'\n {battle.team2.name}: '
                    for leader in battle.team2.leader:
                        footer += f'{leader}, '
                    footer = footer[:-2]
                    footer += ' please `,confirm`.'
            await channel.send(footer)
    first = None
    for embed in embed_split:
        if not first:
            first = await channel.send(embed=embed)
        else:
            await channel.send(embed=embed)
    return first


def escape(string: str) -> str:
    special = ['\\', '>', '`', '_', '*', '|']
    out = string[:]
    for char in special:
        if char in out:
            out = out.replace(char, '\\' + char)
    return out


async def wait_for_reaction_on_message(confirm: str, cancel: Optional[str],
                                       message: discord.Message, author: discord.Member, bot: discord.Client,
                                       timeout: float = 30.0) -> bool:
    await message.add_reaction(confirm)
    await message.add_reaction(cancel)

    def check(reaction, user):
        return user == author and str(reaction.emoji) == confirm or cancel

    while True:
        try:
            react, reactor = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            return False
        if react.message.id != message.id:
            continue
        if str(react.emoji) == confirm and reactor == author:
            return True
        elif str(react.emoji) == cancel and reactor == author:
            return False


def is_usable_emoji(text: str, bot):
    if text.startswith('<:'):
        text = text[2:]
        if text.endswith('>'):
            text = text[:-1]
        name = text[:text.index(':')]
        emoji_id = text[text.index(':') + 1:]
        emoji = discord.utils.get(bot.emojis, name=name)
        if emoji:
            return emoji.available
    return False


async def send_long(ctx: Context, message: str, sep: str):
    output = split_on_length_and_separator(message, length=2000, separator=sep)
    for put in output:
        await ctx.send(put)


def check_roles(user: discord.Member, roles: Iterable) -> bool:
    return any((role.name in roles for role in user.roles))

async def response_message(ctx: Context, msg: str) -> discord.Message:
    msg = await ctx.send(f'{ctx.author.mention}: {msg}')
    await ctx.message.delete(delay=1)
    return msg
