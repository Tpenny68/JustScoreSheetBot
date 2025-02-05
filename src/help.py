class Categories:
    cb = 'cb'
    misc = 'misc'


class HelpDoc(dict):
    def __init__(self, help_txt, brief: str, description='', usage=''):
        if not description:
            description = self.descriptify(brief)
        super().__init__(
            help=help_txt,
            brief=brief,
            description=description,
            usage=usage
        )

    def descriptify(self, s):
        return s[0].upper() + s[1:] + '.'


help_doc = dict(
    battle=HelpDoc(Categories.cb, 'Start a Mock Scoresheet in this channel with two team names and a size', '',
                   'Team1 Team2 size'),
    send=HelpDoc(Categories.cb, 'Sends in the tagged player, if this is a mock you also need to send the team name', '',
                 '@Player Optional[TeamName]'),
    replace=HelpDoc(Categories.cb, 'Replaces current player with the tagged player', '', '@Player Optional[TeamName]'),
    end=HelpDoc(Categories.cb, 'End the game with characters and stocks for both teams',
                'Example: `!end ness 3 palu 2`, you can also choose alts here. use `,char CharName` to test it',
                'Char1 StocksTaken1 Char2 StocksTaken2'),
    endlag=HelpDoc(Categories.cb,
                   'End the game with characters and stocks for both teams. '
                   'Same as end, but does not need to result in one player winning'
                   'Example: `!end ness 3 palu 2`, you can also choose alts here. use `,char CharName` to test it',
                   'Char1 StocksTaken1 Char2 StocksTaken2'),
    resize=HelpDoc(Categories.cb, 'Resize the crew battle', '', 'NewSize'),
    undo=HelpDoc(Categories.cb, 'Undo the last match',
                 'Takes no parameters and undoes the last match that was played'),
    timerstock=HelpDoc(Categories.cb, 'Your current player will lose a stock to the timer'),
    forfeit=HelpDoc(Categories.cb, 'Forfeits a crew battle'),
    status=HelpDoc(Categories.cb, 'Current status of the battle'),
    chars=HelpDoc(Categories.cb, 'Prints all characters names and their corresponding emojis'),
    clear=HelpDoc(Categories.cb, 'Clears the current cb in the channel'),
    confirm=HelpDoc(Categories.cb, 'Confirms the final score sheet is correct'),
    char=HelpDoc(Categories.cb, 'Prints the character emoji (you can use this to test before entering in the sheet)',
                 'Put a number after the character name to use an alt, EG `,char ness2`'
                 'CharName'),
    arena=HelpDoc(Categories.cb, 'Sets the stream if you are a streamer or leader, or prints it if you are not'),
    stream=HelpDoc(Categories.cb, 'Sets the stream if you are a streamer or leader, or prints it if you are not'),
    timer=HelpDoc(Categories.cb, 'Prints the time since the last match ended'),
    guide=HelpDoc(Categories.misc, 'Links to the guide'),
    coin=HelpDoc(Categories.misc, 'Flips a coin. If you mention a user it will '
                                  'prompt them to answer heads or tails before the flip.'),
    use_ext=HelpDoc(Categories.cb, 'Uses your teams time extension in a crew battle'),
    ext=HelpDoc(Categories.cb, 'Prints out extension status'),
    countdown=HelpDoc(Categories.cb, 'Counts down for x seconds (defaults to 3).'),
    thank=HelpDoc(Categories.misc, 'Thanks alexjett'),
    stagelist=HelpDoc(Categories.misc, 'Returns the stagelist'),
    invite=HelpDoc(Categories.misc, 'Returns the server invite'),
    kill=HelpDoc(Categories.misc, "Kills the bot (I advise you to let the bot runner do this)"),
    stats=HelpDoc(Categories.misc, "Shows your stats")
)
