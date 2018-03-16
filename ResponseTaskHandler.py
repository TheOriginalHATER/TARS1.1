import asyncio

PROCESSED_RTPS = []
CURRENT_RUNNING_GAMES = []


def find_game_by_channel(channel):
    for game in CURRENT_RUNNING_GAMES:
        if game.channel == channel:
            return game
def find_game_by_id(id):
    for game in CURRENT_RUNNING_GAMES:
        if game.id_name.lower() == id.lower():
            return game
def find_first_game_from_user(user):
    for game in CURRENT_RUNNING_GAMES:
        for player in game.players:
            if player.member == user:
                return game


class ResponseTaskPackage:
    def __init__(self, type, user, game):
        self.type = type
        self.user = user
        self.game = game
        self.content = ""






async def catch_game_rtps(game, max, timeout):
    total = []
    counter = 0
    while len (total) > max and counter < timeout:
        await asyncio.sleep(1)

        for rtp in PROCESSED_RTPS:
            if rtp.game == game:
                total.append(rtp)
        counter += 1

    return total


