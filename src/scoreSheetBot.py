import logging
import os
import sys
import time
import traceback
from asyncio import sleep
from typing import Dict

from discord.ext import commands
from dotenv import load_dotenv

from src.character import all_emojis, string_to_emote, all_alts
from src.decorators import *
from src.help import help_doc

logging.basicConfig(level=logging.INFO)

Context = discord.ext.commands.Context


class ScoreSheetBot(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.battle_map: Dict[str, Battle] = {}
        self.cache_time = time.time()
        self._gambit_message = None

    def _current(self, ctx) -> Battle:
        if key_string(ctx) in self.battle_map:
            return self.battle_map[key_string(ctx)]
        else:
            return None

    async def _set_current(self, ctx: Context, battle: Battle):
        self.battle_map[key_string(ctx)] = battle
        await update_channel_open(NO, ctx.channel)

    async def _clear_current(self, ctx):
        self.battle_map.pop(key_string(ctx), None)
        # await unlock(ctx.channel)
        await update_channel_open('', ctx.channel)

    @commands.command(help='Shows this command')
    async def help(self, ctx, *group):
        """Gets all categories and commands of mine."""
        staff = False  # check_roles(main_user, STAFF_LIST)
        if not group:
            halp = discord.Embed(title='Group Listing and Uncategorized Commands',
                                 description=f'Use `{self.bot.command_prefix}help *group*` to find out more about them!')
            groups_desc = ''
            for cmd in self.bot.walk_commands():
                if isinstance(cmd, discord.ext.commands.Group):
                    groups_desc += ('{} - {}'.format(cmd, cmd.brief) + '\n')
            halp.add_field(name='Cogs', value=groups_desc[0:len(groups_desc) - 1], inline=False)
            cmds_desc = ''
            for y in self.bot.walk_commands():
                if y.name == 'help':
                    cmds_desc += ('{} - {}'.format(y.name, y.help) + '\n')
            halp.add_field(name='Help Commands', value=cmds_desc[0:len(cmds_desc) - 1], inline=False)
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send(embed=halp)
        else:
            if len(group) > 1:
                halp = discord.Embed(title='Error!', description='You can only send 1 group or command name!',
                                     color=discord.Color.red())
                await ctx.message.author.send(embed=halp)
                return
            else:
                found = False
                for cmd in self.bot.walk_commands():
                    for grp in group:
                        if cmd.name == grp:
                            if isinstance(cmd, discord.ext.commands.Group) and not cmd.hidden:
                                cmds = []
                                halp = discord.Embed(title=group[0] + ' Command Listing',
                                                     description=cmd.brief)
                                for c in self.bot.walk_commands():
                                    if c.help == cmd.name:
                                        if staff or not c.hidden:
                                            cmds.append(c)
                                cmds.sort(key=lambda c: c.name)
                                for c in cmds:
                                    halp.add_field(name=c.name, value=c.brief, inline=False)
                            else:
                                if staff or not cmd.hidden:
                                    halp = discord.Embed(title=group[0],
                                                         description=f'{cmd.description}\n'
                                                                     f'{self.bot.command_prefix}{cmd.name} {cmd.usage}')
                                else:
                                    await ctx.author.send('That command is hidden.')
                            found = True
                if not found:
                    halp = discord.Embed(title='Error!', description=f'Command {group} not found.',
                                         color=discord.Color.red())
                else:
                    if not isinstance(ctx.channel, discord.channel.DMChannel):
                        await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('', embed=halp)

    ''' **********************************CB COMMANDS ******************************************'''

    @commands.group(name='cb', brief='Commands for running a crew battle', invoke_without_command=True)
    async def cb(self, ctx):
        await self.help(ctx, 'cb')

    # Perhaps modify this for two roles.
    # @commands.command(**help_doc['lock'], aliases=['mohamed', 'nohamed', 'lk'])
    # @main_only
    # @role_call([MINION, ADMIN, DOCS, LEADER, ADVISOR])
    # @ss_channel
    # async def lock(self, ctx: Context, streamer: Optional[discord.Member]):
    #
    #     try:
    #         current = self._current(ctx)
    #     except ValueError:
    #         await ctx.send('There needs to be a ranked battle running to use this command.')
    #         return
    #     if current and not current.battle_type == BattleType.MOCK:
    #         if not check_roles(ctx.author, STAFF_LIST):
    #             await self._reject_outsiders(ctx)
    #         overwrites: Dict = ctx.channel.overwrites
    #         muted_overwite = discord.PermissionOverwrite(send_messages=False, add_reactions=False,
    #                                                      manage_messages=False)
    #
    #         crew_overwrite = discord.PermissionOverwrite(send_messages=True, add_reactions=True)
    #         if crew_lookup(current.team1.name, self).overflow:
    #             _, mems, _ = members_with_str_role(current.team1.name, self)
    #             for mem in mems:
    #                 if not check_roles(mem, [MUTED]):
    #                     overwrites[mem] = crew_overwrite
    #         else:
    #             cr_role_1 = discord.utils.get(ctx.guild.roles, name=current.team1.name)
    #             overwrites[cr_role_1] = crew_overwrite
    #             for mem in overlap_members(MUTED, current.team1.name, self):
    #                 overwrites[mem] = muted_overwite
    #         if crew_lookup(current.team2.name, self).overflow:
    #             _, mems, _ = members_with_str_role(current.team2.name, self)
    #             for mem in mems:
    #                 if not check_roles(mem, [MUTED]):
    #                     overwrites[mem] = crew_overwrite
    #         else:
    #             cr_role_2 = discord.utils.get(ctx.guild.roles, name=current.team2.name)
    #             overwrites[cr_role_2] = crew_overwrite
    #             for mem in overlap_members(MUTED, current.team2.name, self):
    #                 overwrites[mem] = muted_overwite
    #         everyone_overwrite = discord.PermissionOverwrite(send_messages=False, manage_messages=False,
    #                                                          add_reactions=False, create_public_threads=False,
    #                                                          create_private_threads=False)
    #         overwrites[self.cache.roles.everyone] = everyone_overwrite
    #         out = f'Room Locked to only {current.team1.name} and {current.team2.name}.'
    #         if streamer:
    #             if check_roles(streamer, [MUTED]):
    #                 out += f'{streamer.mention} is muted and does not get speaking perms.'
    #             else:
    #                 overwrites[streamer] = crew_overwrite
    #                 out += f' As the streamer, {streamer.display_name} also can talk.'
    #
    #         await ctx.channel.edit(overwrites=overwrites)
    #         await ctx.send(out)
    #     else:
    #         await ctx.send('There needs to be a ranked battle running to use this command.')
    #         return

    # @commands.command(**help_doc['unlock'])
    # @main_only
    # @role_call([MINION, ADMIN, DOCS, LEADER, ADVISOR])
    # @ss_channel
    # async def unlock(self, ctx: Context):
    #     await unlock(ctx.channel)
    #     await ctx.send('Unlocked the channel for all crews to use.')
    #
    # @commands.command(**help_doc['battle'], aliases=['challenge'], group='CB')
    # @main_only
    # @no_battle
    # @is_lead
    # @ss_channel
    # async def battle(self, ctx: Context, user: discord.Member, size: int):
    #     if size < 1:
    #         await ctx.send('Please enter a size greater than 0.')
    #         return
    #     user_crew = crew(ctx.author, self)
    #     opp_crew = crew(user, self)
    #     if not user_crew:
    #         await ctx.send(f'{ctx.author.name}\'s crew didn\'t show up correctly. '
    #                        f'They might be in an overflow crew or no crew. '
    #                        f'Please contact an admin if this is incorrect.')
    #         return
    #     if not opp_crew:
    #         await ctx.send(f'{user.name}\'s crew didn\'t show up correctly. '
    #                        f'They might be in an overflow crew or no crew. '
    #                        f'Please contact an admin if this is incorrect.')
    #         return
    #     if user_crew != opp_crew:
    #         user_actual = crew_lookup(user_crew, self)
    #         opp_actual = crew_lookup(opp_crew, self)
    #         if user_actual.destiny_opponent == opp_actual.name:
    #             msg = await ctx.send(f'{ctx.author.mention}:{user_actual.name} has '
    #                                  f'{opp_actual.name} as a destiny opponent, '
    #                                  f'do you want to continue as a destiny battle?')
    #             if await wait_for_reaction_on_message(YES, NO, msg, ctx.author, self.bot):
    #                 await ctx.send('Destiny battle confirmed.')
    #                 await self._set_current(ctx, Battle(user_crew, opp_crew, size, BattleType.DESTINY))
    #                 await send_sheet(ctx, battle=self._current(ctx))
    #                 return
    #             else:
    #                 await ctx.send('Battle will start as a normal ranked.')
    #
    #         await self._set_current(ctx, Battle(user_crew, opp_crew, size))
    #         await send_sheet(ctx, battle=self._current(ctx))
    #     else:
    #         await ctx.send('You can\'t battle your own crew.')

    @commands.command(**help_doc['battle'])
    @no_battle
    @ss_channel
    async def battle(self, ctx: Context, team1: str, team2: str, size: int):
        if size < 1:
            await ctx.send('Please enter a size greater than 0.')
            return
        await self._set_current(ctx, Battle(team1, team2, size, BattleType.MOCK))
        await ctx.send(embed=self._current(ctx).embed())

    @commands.command(**help_doc['countdown'])
    @ss_channel
    async def countdown(self, ctx: Context, seconds: Optional[int] = 10):
        if seconds > 10 or seconds < 1:
            await ctx.send('You can only countdown from 10 or less!')
        await ctx.send(f'Counting down from {seconds}')
        while seconds > 0:
            await ctx.send(f'{seconds}')
            seconds -= 1
            await sleep(1)
        await ctx.send('Finished!')

    @commands.command(**help_doc['send'], aliases=['s'])
    @has_sheet
    @ss_channel
    async def send(self, ctx: Context, user: discord.Member, team: str = None):
        if not team:
            team = self._current(ctx).team_from_member(ctx.author.mention)
        if team:
            self._current(ctx).add_player(team, escape(user.display_name), ctx.author.mention, user.id)
        else:
            await ctx.send(f'During a mock you need to send with a teamname, like this'
                           f' `,send @playername teamname`.')
            return

        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['use_ext'])
    @has_sheet
    @ss_channel
    async def use_ext(self, ctx: Context, team: str = None):
        if not team:
            team = self._current(ctx).team_from_member(ctx.author.mention)
        if team:
            if self._current(ctx).ext_used(team):
                await ctx.send(f'{team} has already used their extension.')
                return
            else:
                await ctx.send(f'{team} just used their extension. '
                               f'They now get 5 more minutes for their next player to be in the arena.')
        else:
            await ctx.send(f'During a mock you need to use your extension, like this'
                           f' `,ext teamname`.')
            return
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['forfeit'])
    @has_sheet
    @ss_channel
    async def forfeit(self, ctx: Context, team: str = None):
        if not team:
            team = self._current(ctx).team_from_member(ctx.author.mention)
        if team:
            msg = await ctx.send(f'{ctx.author.mention}:{team} has {self._current(ctx).lookup(team).stocks} stocks '
                                 f'left, are you sure you want to forfeit?')
            if not await wait_for_reaction_on_message(YES, NO, msg, ctx.author, self.bot):
                await ctx.send(f'{ctx.author.mention}: {ctx.command.name} canceled or timed out!')
                return
            self._current(ctx).forfeit(team)
        else:
            await ctx.send(f'During a mock you need to forfeit, like this'
                           f' `,forfeit teamname`')
            return
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['ext'])
    @has_sheet
    @ss_channel
    async def ext(self, ctx):
        await ctx.send(self._current(ctx).ext_str())

    @commands.command(**help_doc['replace'], aliases=['r'])
    @has_sheet
    @ss_channel
    async def replace(self, ctx: Context, user: discord.Member, team: str = None):
        if not team:
            team = self._current(ctx).team_from_member(ctx.author.mention)
        if team:
            self._current(ctx).replace_player(team, escape(user.display_name), ctx.author.mention, user.id)
        else:
            await ctx.send(f'During a mock you need to replace with a teamname, like this'
                           f' `,replace @playername teamname`.')
            return
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['end'], aliases=['e'])
    @has_sheet
    @ss_channel
    async def end(self, ctx: Context, char1: Union[str, discord.Emoji], stocks1: int, char2: Union[str, discord.Emoji],
                  stocks2: int):

        self._current(ctx).finish_match(stocks1, stocks2,
                                        Character(str(char1), self.bot, is_usable_emoji(char1, self.bot)),
                                        Character(str(char2), self.bot, is_usable_emoji(char2, self.bot)))
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['endlag'])
    @has_sheet
    @ss_channel
    async def endlag(self, ctx: Context, char1: Union[str, discord.Emoji], stocks1: int,
                     char2: Union[str, discord.Emoji],
                     stocks2: int):

        self._current(ctx).finish_lag(stocks1, stocks2,
                                      Character(str(char1), self.bot, is_usable_emoji(char1, self.bot)),
                                      Character(str(char2), self.bot, is_usable_emoji(char2, self.bot)))
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['resize'], aliases=['extend'])
    @has_sheet
    @ss_channel
    async def resize(self, ctx: Context, new_size: int):
        if new_size > 9999:
            await ctx.send('Too big. Pls stop')
            return
        self._current(ctx).resize(new_size)
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['arena'], aliases=['id', 'arena_id', 'lobby'])
    @has_sheet
    @ss_channel
    async def arena(self, ctx: Context, id_str: str = ''):
        # if id_str and (check_roles(ctx.author, [LEADER, ADVISOR, ADMIN, MINION, STREAMER, CERTIFIED]
        #                            ) or self._current(ctx).battle_type == BattleType.MOCK):
        if id_str:
            self._current(ctx).id = id_str
            await ctx.send(f'Updated the id to {id_str}')
            return
        await ctx.send(f'The lobby id is {self._current(ctx).id}')

    @commands.command(**help_doc['stream'], aliases=['streamer', 'stream_link'])
    @has_sheet
    @ss_channel
    async def stream(self, ctx: Context, stream: str = ''):
        # if stream and (check_roles(ctx.author, [LEADER, ADVISOR, ADMIN, MINION, STREAMER, CERTIFIED]
        #                            ) or self._current(ctx).battle_type == BattleType.MOCK):
        if stream:
            if '/' not in stream:
                stream = 'https://twitch.tv/' + stream
            self._current(ctx).stream = stream
            await ctx.send(f'Updated the stream to {stream}')
            return
        await ctx.send(f'The stream is {self._current(ctx).stream}')

    @commands.command(**help_doc['undo'])
    @has_sheet
    @ss_channel
    async def undo(self, ctx):
        if not self._current(ctx).undo():
            await ctx.send('Note: undoing a replace on the scoresheet doesn\'t actually undo the replace, '
                           'you need to use `,replace @player` with the original player to do that.')

        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['confirm'])
    @has_sheet
    @ss_channel
    async def confirm(self, ctx: Context):
        current = self._current(ctx)
        if current.battle_over():

            await self._clear_current(ctx)
            await ctx.send(f'This battle was confirmed by {ctx.author.mention}.')

        else:
            await ctx.send('The battle is not over yet, wait till then to confirm.')

    @commands.command(**help_doc['clear'])
    @has_sheet
    @ss_channel
    async def clear(self, ctx):
        await ctx.send('If you just cleared a crew battle to troll people, be warned this is a bannable offence.')

        msg = await ctx.send(f'Are you sure you want to clear this crew battle?')
        if not await wait_for_reaction_on_message(YES, NO, msg, ctx.author, self.bot):
            resp = await ctx.send(f'{ctx.author.mention}: {ctx.command.name} canceled or timed out!')
            await resp.delete(delay=10)
            await ctx.message.delete()
            await msg.delete(delay=5)
            return

        await self._clear_current(ctx)
        await ctx.send(f'{ctx.author.mention} cleared the crew battle.')

    @commands.command(**help_doc['status'])
    @has_sheet
    @ss_channel
    async def status(self, ctx):
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['timer'])
    @has_sheet
    @ss_channel
    async def timer(self, ctx):
        await ctx.send(self._current(ctx).timer())

    @commands.command(**help_doc['timerstock'])
    @has_sheet
    @ss_channel
    async def timerstock(self, ctx, team: str = None):
        if not team:
            team = self._current(ctx).team_from_member(ctx.author.mention)
        if team:
            self._current(ctx).timer_stock(team, ctx.author.mention)
        else:
            await ctx.send(f'You need to take a timer_stock with a teamname, like this'
                           f' `,timer_stock teamname`.')
            return
        await send_sheet(ctx, battle=self._current(ctx))

    @commands.command(**help_doc['char'])
    async def char(self, ctx: Context, emoji):
        if is_usable_emoji(emoji, self.bot):
            await ctx.send(emoji)
        else:
            await ctx.send(f'What you put: {string_to_emote(emoji, self.bot)}')
            await ctx.send(f'All alts in order: {all_alts(emoji, self.bot)}')

    @commands.command(**help_doc['chars'])
    @ss_channel
    async def chars(self, ctx):
        emojis = all_emojis(self.bot)
        out = []
        for emoji in emojis:
            out.append(f'{emoji[0]}: {emoji[1]}\n')

        await send_long(ctx.author, "".join(out), ']')

    @commands.group(name='misc', brief='Miscellaneous commands', invoke_without_command=True)
    async def misc(self, ctx):
        await self.help(ctx, 'misc')

    @commands.command(**help_doc['stagelist'])
    async def stagelist(self, ctx: Context):
        await ctx.send('https://cdn.discordapp.com/attachments/760303456757350400/815364853291286628/stagelist-1.png')

    @commands.command(**help_doc['invite'])
    async def invite(self, ctx: Context):
        await ctx.send('https://smashcrewserver.com')

    @commands.command(**help_doc['thank'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def thank(self, ctx: Context):

        await ctx.send(f'Thanks for all the hard work you do on the bot alexjett!\n'
                       f'(If you want to thank him with money you can do so here. '
                       f'https://www.buymeacoffee.com/alexjett)')

    @commands.command(**help_doc['coin'])
    async def coin(self, ctx: Context, member: discord.Member = None):

        flip = bool(random.getrandbits(1))
        if member:
            msg = await ctx.send(f'{ctx.author.display_name} has asked you to call a coin {member.mention} '
                                 f'what do you choose'
                                 f'({YES} for heads {NO} for tails?)')
            choice = await wait_for_reaction_on_message(YES, NO, msg, member, self.bot, 60)
            choice_name = 'heads' if choice else 'tails'
            if choice == flip:
                await ctx.send(f'{member.display_name} chose {choice_name} and won the flip!')
            else:
                await ctx.send(f'{member.display_name} chose {choice_name} and lost the flip!')
        res = 'heads' if flip else 'tails'
        await ctx.send(f'Your coin flip landed on {res}', file=discord.File(f'img/{res}.png'))

    @commands.command(**help_doc['guide'])
    async def guide(self, ctx):
        await ctx.send('INSERT GUIDE HERE')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = ()

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        # if isinstance(error, ignored):
        #     return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f'{str(error)}, try ",help" for a list of commands.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(error))
        elif isinstance(error, StateError):
            await ctx.send(f'"{ctx.command}" did not work because:{error.message}')
        elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
            await ctx.send(f'{ctx.author.mention}: {ctx.command.name} failed because:{str(error)}\n'
                           f'Try using `{self.bot.command_prefix}{ctx.command.name} @Member`.')
        elif str(error) == 'The read operation timed out':
            await ctx.send('The google sheets API isn\'t responding, wait 60 seconds and try again')
        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            await ctx.send(f'{ctx.author.mention}: {ctx.command.name} failed because:{str(error)}')
            logfilename = 'logs.log'
            if os.path.exists(logfilename):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not
            lf = open(logfilename, append_write)
            traceback.print_exception(type(error), error, error.__traceback__, file=lf)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            lf.close()


async def main():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    bot = commands.Bot(command_prefix=os.getenv('PREFIX'), intents=discord.Intents.all(), case_insensitive=True,
                       allowed_mentions=discord.AllowedMentions(everyone=False))
    async with bot:
        bot.remove_command('help')
        await bot.add_cog(ScoreSheetBot(bot))
        await bot.start(token)


if __name__ == '__main__':
    main()
