import functools
from typing import Iterable
from src.helpers import *


def ss_channel(func):
    """Decorator that errors if not in the correct channel."""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        ctx = args[0]
        if '⚔' not in ctx.channel.name:
            await ctx.send('Cannot use this bot in this channel, try a channel with `⚔` in the channel name.')
            return
        return await func(self, *args, **kwargs)

    return wrapper


def has_sheet(func):
    """Decorator that errors if no battle has started."""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        ctx = args[0]
        battle = self.battle_map.get(key_string(ctx))
        if battle is None:
            await ctx.send('Battle is not started.')
            return
        # kwargs['battle'] = battle
        return await func(self, *args, **kwargs)

    return wrapper


def no_battle(func):
    """Decorator that errors if no battle has started."""

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        ctx = args[0]
        battle = self.battle_map.get(key_string(ctx))
        if battle is not None:
            await ctx.send('A battle is already going in this channel.')
            return
        # kwargs['battle'] = battle
        return await func(self, *args, **kwargs)

    return wrapper


def role_call(required: Iterable):
    """Decorator that checks if someone is in a roles list."""

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped_f(self, *args, **kwargs):
            ctx = args[0]
            if not check_roles(ctx.author, required):
                await response_message(ctx, f'You need to be one of {required} to run {ctx.command.name}')
                return
            return await func(self, *args, **kwargs)

        return wrapped_f

    return wrapper
