import random






#base game class
class ThongGame():
    def __init__(self, channel, bot):
        self.channel = channel
        self.players = []
        self.questions = []
        self.bot = bot
        self.gamelog = "A new Game of Thongs has started -- use the ?thongjoin command to join!"

    def add_to_log(self, message = ""):
        self.gamelog = self.gamelog + message + "\n"

    async def post_logs(self, message = ""):
        await self.bot.send_message(self.channel, self.gamelog + message)
        self.gamelog = ""


    async def addplayer(self, user):
        pass







class ThongPlayer():
    def __init__(self, game):
        self.game = game
        self.score = 0
        self.response = None









