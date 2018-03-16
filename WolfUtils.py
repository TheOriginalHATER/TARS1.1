import discord
import random
import ResponseTaskHandler
import asyncio
import roles
import TARSUtils
from Actions import Action, COMMAND_FLAGS
import Actions
from enum import Enum



ID_NAMES = ["Scandium","Titanium","Vanadium","Chromium","Maganese","Iron","Cobalt","Nickel","Copper","Zinc","Yttrium","Zirconium","Niobium","Technetium","Molybdenum","Ruthenium",
"Rhodium","Palladium","Silver","Cadmium","Hafnium","Tantalum","Tungsten","Rhenium","Osmium","Iridium","Platinum","Gold","Mercury"]





async def send_remote_action(ctx,client, flag, targetname=None, game_id = None):
    #Finding the game the player is in
    game:AutoGame = None
    if game_id is not None:
        game = ResponseTaskHandler.find_game_by_id(game_id)
        if game.getPlayerFromUser(ctx.message.author) == None:
            await client.send_message(ctx.message.author,"You're not in this game.")
            return

    if game is None:
        game = ResponseTaskHandler.find_first_game_from_user(ctx.message.author)

        if game is None:
            await client.send_message(ctx.message.author,"Sorry, I couldn't find any games you are in...")
            return

    #Game has been found, meaning the user is already in the game. Get their player object next.

    source = game.getPlayerFromUser(ctx.message.author)

    target_user = TARSUtils.getUserFromString(ctx, targetname, game.channel)
    if target_user is None:
        await client.send_message(ctx.message.author, "No targets found that match with the name: " + targetname)
        return
    target = game.getPlayerFromUser(target_user)
    if target is None:
        await client.send_message(ctx.message.author, target_user.name + " is not playing in the game with ID:" + game.id_name)
        return





    #Find out if it's a factional action
    if flag in source.role.faction.faction_commands and source.role.speaks_with_faction:
        faction = source.role.faction

        action = faction.create_action(flag, source, target)

        if await action.target_valid():

            string = "None"
            if faction.target_action is not None:
                string = faction.target_action.target.name

            faction.target_action = action
            for player in faction.players:
                if player.role.speaks_with_faction:

                    await player.send_logs(source.name + " submitted the factional action " + flag.name + " targeting " + target.name + ". (Previous submitted target: " + string + ")" )


    elif flag in source.role.flags:
        action = source.role.create_action(flag, target)
        if await action.target_valid():
            string = "None"

            for prev in source.submitted_actions:
                if prev.flag == flag:
                    source.submitted_actions.remove(prev)
                string = prev.target.name

            source.submitted_actions.append(action)
            await source.send_logs(flag.name + " action targeting " + target.name + " submitted successfuly. (Previous submitted target: " + string + ")")








    else:
        client.send_message(ctx.message.author, "It doesn't appear that you can use this command keyword. Try a different one?")




















class AutoPlayer:
    def __init__(self, member: discord.member, game):
        self.member = member
        self.name = member.name
        self.alive = True
        self.currentvotes= 0
        self.votingfor = None
        self.arevoting = []
        self.role = None
        self.game = game
        self.faction = None

        self.submitted_actions = []

        #State-based
        self.is_blocked = False
        self.is_protected = False
        self.redirect_to = None
        self.injured = False



        self.event_log = "Welcome to the game! This game's ID is: "+ self.game.id_name+"\n"


    def add_to_log(self, message):
        self.event_log = self.event_log + message + "\n"



    async def send_logs(self, message):
        if message is None:
            message = ""

        self.add_to_log(str(message))
        await self.game.bot.send_message(self.member, self.event_log)
        self.event_log = ""

    def clear_states(self):
        self.is_blocked = False
        self.is_protected = False
        self.redirect_to = None
        self.submitted_actions = []
        self.injured = False









class AutoFaction:
    def __init__(self, name, alignment, is_evil, has_alt_wincon, nightkill, commands = []):
        self.name = name
        self.alignment = alignment
        self.has_alt_wincon = has_alt_wincon
        self.is_evil = is_evil
        self.has_nightly_kill = nightkill

        self.faction_commands = commands


        self.target_action = None




        self.players =[]

    def clear_target(self):
        self.kill_target = None

    def fetch_living_players_in_faction(self):
        living = []

        for player in self.players:
            if player.alive:
                living.append(player)

        return living

    def check_alt_wincon(self):
        pass


    def create_action(self, flag, source, target):

        if flag == COMMAND_FLAGS.SHOOT:
            return Actions.ActionKill(flag, source.game, source, target, Actions.Killtype.SHOT, 40, True)
















class AutoGame:
    def __init__(self, bot, channel):
        self.setup = None

        #Gamerule defaults for simplest games
        self.reveal_rule = DeathReveal.FULL_REVEAL
        self.r0_kill = RoundZeroKill.HOST_SAVE
        self.r0_peeks = RoundZeroPeek.NO_PEEKS



        self.round = 0
        self.is_day = False

        self.started = False
        self.lhlv = None
        self.roles = []


        self.factions = []


        #Currently running instance of bot
        #Use sparingly
        #HAHAHAHAHA I REMEMBER WHEN I WROTE THAT LOL FUCK THAT LEL
        # use that bitch whenever i fukken want lellll
        #I regret this.
        # LOL DRUNK AGAIN  NO YOU FUCKIN DONT PUSSY

        self.bot = bot

        self.players = []


        self.channel= channel

        self.id_name = self.get_new_id_name()

        self.game_log = "A new game has been started-- Use the ?join command to join it! This game's ID is: " + self.id_name + "\n"


        #Holds all submitted actions
        self.submitted_actions = []
        self.resolved_actions = []


        ResponseTaskHandler.CURRENT_RUNNING_GAMES.append(self)


    def get_new_id_name(self):
        random.shuffle(ID_NAMES)

        for name in ID_NAMES:
            available = True

            for game in ResponseTaskHandler.CURRENT_RUNNING_GAMES:
                if game.id_name == name:
                    if available:
                        available = False

            if available == True:
                return name





    def add_to_log(self, message):
        self.game_log = self.game_log + message + "\n"



    async def post_log(self, message):
        if message is None:
            message = ""

        self.add_to_log(str(message))
        await self.bot.send_message(self.channel,self.game_log)
        self.game_log = ""



    #function to add players to a game. returns a string that basically functions as what the bot needs to say when it happens, yolo
    async def addplayer(self, member:discord.member):

        if self.started:
            await self.post_log("The game has already started. Please try again after the current game has concluded.")

        elif self.getPlayerFromUser(member) is not None:
            await self.post_log("You are already in this game!")
        else:
            self.players.append(AutoPlayer(member,self))
            await self.post_log(member.name + " has been added to the game. \n" + self.getPlayerListText())


    #same with this one add the add one really
    async def dropplayer(self, member:discord.member):

        if self.started:
            await self.post_log("The game has already started. Please ask a moderator to modkill you instead if you cannot stay.")

        elif self.getPlayerFromUser(member) is None:
            await self.post_log("You are not in this game!")
        else:
            self.players.remove(self.getPlayerFromUser(member))

            await self.post_log(member.name + " has left the game.")

            if (len(self.players ) < 1):
                await self.post_log("No more players in queue. Closing game.")
                ResponseTaskHandler.CURRENT_RUNNING_GAMES.remove(self)











    #returns ONLY A TEXT VERSION of the playerlist used for determining players in the game at the start. Use game.players for the actual list of player objects, duh
    def getPlayerListText(self):
        playerlist = ""
        for player in self.players:
                playerlist = playerlist + player.member.name +", "


        return "The current players are: " + playerlist.rstrip(", ") + "."



    def gettally(self):

        newlist = sorted(self.players, key=lambda player : len(player.arevoting), reverse=True)

        deadpeople = []
        playersvotingnone =[]
        playersvotingnolynch = []
        finalstring = "Round " + str(self.round) + " tally:\n\n"

        for player in newlist:
            if not len(player.arevoting) == 0 and player.alive:
                finalstring = finalstring + player.member.name + " - " + str(len(player.arevoting)) + " - "
                stringenemies = ""
                for enemy in player.arevoting:
                    stringenemies = stringenemies + enemy.member.name + ", "

                finalstring = finalstring +stringenemies.rstrip(", ") + "\n"

            if player.alive and player.votingfor is None:
                playersvotingnone.append(player)
            elif player.alive and player.votingfor == "no lynch":
                playersvotingnolynch.append(player)
            elif not player.alive:
                deadpeople.append(player)

        stringnolynchers = ""
        for nolyncher in playersvotingnolynch:
            stringnolynchers = stringnolynchers + nolyncher.member.name + ", "

        if not stringnolynchers == "":
            finalstring = finalstring + "No Lynch - " + str(len(playersvotingnolynch)) + " - "+ stringnolynchers.rstrip(", ") + "\n"


        stringnovoters = ""
        for novoter in playersvotingnone:
            stringnovoters = stringnovoters + novoter.member.name + ", "


        if not stringnovoters == "":
            finalstring = finalstring + "No Vote - " + str(len(playersvotingnone)) + " - " + stringnovoters.rstrip(", " +"\n")


        self.updatelhlv()
        stringlhlv = "\n\nLHLV: "
        if self.lhlv is None:
            stringlhlv = stringlhlv + "No Lynch\n\n"
        else:
            stringlhlv = stringlhlv + self.lhlv.member.name +"\n\n"

        finalstring = finalstring + stringlhlv

        stringdeadpeople = ""
        for corpse in deadpeople:
            stringdeadpeople = stringdeadpeople + corpse.member.name + ", "

        if not stringdeadpeople == "":
            finalstring = finalstring + "\nDead players: " + stringdeadpeople.rstrip(", " )+"."





        return finalstring + "\nTotal living players in game: "+ str(len(self.players)-len(deadpeople))








    async def applyvote(self, source_user, target):

        source = self.getPlayerFromUser(source_user)

        if source == None:
            await self.post_log("You aren't in this game.")
        elif self.started is False:
            await self.post_log("The game hasn't even started yet!")
        elif not self.is_day:
            await self.post_log("It is not daytime yet.")
        elif not source.alive:
            await self.post_log("You are dead, and cannot vote from the grave.")
        elif source.votingfor == target:
            await self.post_log("You are already voting this target.")
        elif source.injured:
            await self.post_log("You are injured this round, and cannot vote.")



        elif target == None:
            self.removepreviousvote(source)
            source.votingfor = None
            source.role.do_vote()
            await self.post_log( source.member.name + "  unvotes." + "\n"+ self.gettally())

        elif target == "no lynch":
            self.removepreviousvote(source)
            source.votingfor = "no lynch"
            source.role.do_vote()
            await self.post_log( source.member.name +" votes for no lynch."+ "\n"+ self.gettally())

        elif target == None:
            await self.post_log("That user is not in this game.")

        elif not target.alive:
            await self.post_log("Your target is dead. Leave them in the grave, please.")

        elif target.alive:
            self.removepreviousvote(source)
            source.votingfor = target
            target.arevoting.append(source)
            source.role.do_vote()
            await self.post_log( source.member.name +  " voted for " + target.member.name + "."+ "\n"+self.gettally())

        else:
            print("Problem applying vote from "+ source.member.name +", on target: " + str(target))
            await self.post_log( "Something went horribly wrong, and I have no idea what...")




    def updatelhlv(self):

        newlist = sorted(self.players, key=lambda player: len(player.arevoting), reverse=True)
        topvote = len(newlist[0].arevoting)

        tiedfortop=[]

        nolynchvotes = 0
        for player in newlist:

            if player.votingfor == "no lynch":
                nolynchvotes = nolynchvotes+1

            if len(player.arevoting) == topvote:
                tiedfortop.append(player)

        if nolynchvotes >= topvote:
            self.lhlv = None
        elif len(tiedfortop) == 1:
            self.lhlv = newlist[0]



    def removepreviousvote(self, source):
        for player in self.players:
            if source in player.arevoting:
                player.arevoting.remove(source)



    #searches for the current player in the game based on the member being passed in
    def getPlayerFromUser(self, member:discord.member):
        for player in self.players:
            if member.id == player.member.id:
                return player
        return None


    #TODO Needs work.
    def make_roleset(self):


        # Default roleset
        if self.setup is None:
            player_number = len(self.players)
            mafia = 0
            detnum = player_number % 4

            if detnum == 0:
                mafia = player_number / 4
            elif detnum == 1:
                mafia = (player_number-1) / 4
            elif detnum == 2:
                if player_number >9:
                    mafia = (player_number+2) / 4
                else:
                    mafia = (player_number-2) / 4

            elif detnum == 3:
                mafia = (player_number+1) / 4

            mafia = int(mafia)

            print("Expected number of mafia in a " + str(player_number) + " player game: " + str(mafia))


                                    #name, alignment, is_evil, has_alt_wincon, nightkill, commands = []
            maffaction = AutoFaction("Mafia Team", roles.Alignment.MAFIA, True, False, True, [COMMAND_FLAGS.SHOOT])
            self.factions.append(maffaction)

            for i in range (mafia):

                self.roles.append(roles.MafiaGoon(maffaction))

                                    #name, alignment, is_evil, has_alt_wincon, nightkill, commands = []
            vilfaction = AutoFaction("Village Team", roles.Alignment.VILLAGE, False, False, False)
            self.factions.append(vilfaction)



            if player_number > 3:

                #Add a cop
                self.roles.append(roles.Cop(vilfaction))

                self.r0_peeks = RoundZeroPeek.R0_NEG_PEEK
                self.r0_kill = RoundZeroKill.INJURY



                if player_number > 4:
                    #Add a Miller
                    self.roles.append(roles.Miller(vilfaction))

                    if player_number > 6:
                        self.roles.append(roles.Doctor(vilfaction))








            #Fill the rest of the role list with normals

            while len(self.roles) < player_number:
                self.roles.append(roles.Villager(vilfaction))



    async def assign_roles(self):
        self.make_roleset()
        random.shuffle(self.roles)
        for x in range(len(self.players)):
            player = self.players[x]
            role = self.roles[x]
            role.player = player
            player.role = role
            player.faction = role.faction
            role.faction.players.append(player)


        #Send role pms
        for player in self.players:

            #"You are a villager, blah blah blah"

            await player.send_logs(player.role.description)
            await player.send_logs(player.role.alignment.wincon)
            if player.role.speaks_with_faction:
                message = "Your teammates are: "

                for teammate in player.role.faction.players:
                    if teammate.role.speaks_with_faction:

                        message = message + teammate.member.name + ", "

                message = message.rstrip(", ") + ". You can chat with them via the ?teamchat command."
                await player.send_logs(message)










    async def start_game(self):

        if len(self.players) > 2:
            await self.assign_roles()
            self.started = True
            await self.post_log("The game has started! Everyone should have received a private message detailing their role and alignment.")
            await self.do_round_zero()
            await self.do_day()

            while self.started and not await self.check_wincons():
                #If it was previously day, start a night round
                if self.is_day:
                    await self.do_night()
                else:
                    await self.do_day()
            await self.bot.send_message(self.channel, "The game has ended. Goodbye.")
            await self.self_destruct()



        else:
            await self.post_log("Need at least 3 players to start")




    async def do_round_zero(self):
        await self.post_log(
            "It is now Round 0, Night. The current R0 Kill Rule is: " + self.r0_kill.name + ". The current R0 Peek Rule is: "+ self.r0_peeks.name)
        for faction in self.factions:
            if faction.has_nightly_kill:
                for player in faction.players:
                    if player.role.speaks_with_faction:
                        await player.send_logs("Your faction needs to submit a Round 0 " + self.r0_kill.name + " target.")

        if self.r0_peeks == RoundZeroPeek.FREEWILL:
            for player in self.players:
                if COMMAND_FLAGS.PEEK in player.role.flags:
                    player.send_logs("Round 0 peek rule is freewill. Please submit a target.")



        await self.post_log("Round 0 night will last approximately 60 seconds")
        await asyncio.sleep(50)
        await self.post_log("Approximately 10 seconds left until Round 0 Night ends.")
        await asyncio.sleep(10)



        for faction in self.factions:
            if faction.target_action is not None:
                if faction.target_action.is_r0_action:
                    self.submitted_actions.append(faction.target_action)
                    print ("r0 factional detected")

        for player in self.players:

            #Action catching for r0 negs

            if player.role.flags == COMMAND_FLAGS.PEEK and self.r0_peeks == RoundZeroPeek.R0_NEG_PEEK:
                notsent = True
                print("Peek search started")

                for action in player.submitted_actions:
                    if action.flag == COMMAND_FLAGS.PEEK:
                        notsent = False


                if notsent:
                    player.submitted_actions.append(player.role.create_action(COMMAND_FLAGS.PEEK, player))
                    print("appending new action")




            if len(player.submitted_actions) > 0:
                for action in player.submitted_actions:
                    if action.is_r0_action:
                        self.submitted_actions.append(action)
                        print("r0 indiv detected")
        await self.post_log("Round 0 Results:")
        await self.resolve_sumbitted_actions()






    async def attempt_kill_player(self, player, killtype):
        #attempts to kill the selected player with the killtype specified. if it happens, calls player.role.on_death.
        if player.alive:
            if player.is_protected and not killtype.ignores_doctor:

                await self.post_log(player.name + " " + killtype.tensename)
                await self.post_log(player.name + " Survived")

                return False

            elif player.role.toughness > 0 and not killtype.ignores_tough:
                player.role.toughness = player.role.toughness - 1
                await self.post_log(player.name + " " + killtype.tensename)
                await self.post_log(player.name + " Survived")

                return False


            elif player.role.indestructible and not (killtype == Actions.Killtype.MODKILL):

                await self.post_log(player.name + " " + killtype.tensename)
                await self.post_log(player.name + " Survived")

                return False

            else:
                await player.role.onDeath(killtype)
                return True


        else:
            await self.post_log("Something went wrong attempting a kill of type:  "+ killtype.name + " on " + player.name + ". (Player not alive)")
            return False





    def queue_actions(self):
        for faction in self.factions:
            if faction.target_action is not None:
                self.submitted_actions.append(faction.target_action)


        for player in self.players:
            if len(player.submitted_actions) > 0:
                for action in player.submitted_actions:
                    self.submitted_actions.append(action)
        print("Queueing actions managed.")





    async def resolve_sumbitted_actions(self):
        for phase in GamePhases:
            await self.resolve_phase_actions(phase)









    async def resolve_phase_actions(self, phase):


        needs_resolving = self.submitted_actions

        if phase == GamePhases.KILLING:

            needs_resolving = []

            for action in self.submitted_actions:
                if action.phase == phase:
                    needs_resolving.append(action)

            needs_resolving = sorted(needs_resolving, key=lambda killaction: killaction.priority, reverse = True)




        for action in needs_resolving:
            if action.phase == phase:

                if action.is_r0_action:
                    successful = await action.round_zero()
                    print("action.round_zero called for " + action.flag.name)


                else:
                    successful = await action.resolve_effects()


                if successful:
                    self.resolved_actions.append(action)


                self.submitted_actions.remove(action)








    #TODO Add in checks for 3rd party wincons
    async def check_wincons(self):


        async def declarewin(fact):
            winstring = ""
            for player in fact.players:
                winstring = winstring + player.name + ", "

            await self.post_log("The " + fact.name + " has won. Winner(s): " + winstring.rstrip(", ") + ".")



        livingplayers = []
        for player in self.players:
            if player.alive:
                livingplayers.append(player)

        if len(livingplayers) < 1:
            for faction in self.factions:
                if faction.alignment == roles.Alignment.SERIAL_KILLER:

                    await declarewin(faction)
                    return True
            await self.post_log("For some reason, everyone is dead... There doesn't appear to be a winner. ")
            return True



        for faction in self.factions:

            other_evils_dead = True
            for fac2 in self.factions:
                if fac2.is_evil and (len(fac2.fetch_living_players_in_faction())) and (fac2.alignment is not faction.alignment):
                    other_evils_dead = False




            facplayers = len(faction.fetch_living_players_in_faction())

            if facplayers > 0:
                if faction.alignment == roles.Alignment.SERIAL_KILLER:
                    if facplayers >= (len(livingplayers) - facplayers) :
                        await declarewin(faction)
                        return True


                elif faction.is_evil:
                    if ( facplayers >= (len(livingplayers) - facplayers) ) and other_evils_dead:


                        await declarewin(faction)
                        return True


                elif faction.alignment == roles.Alignment.VILLAGE:
                    if other_evils_dead:
                        await declarewin(faction)
                        return True



        return False










    #Post day results, reset votes, and perform night actions.
    async def do_night(self):
        self.is_day = False
        for player in self.players:
            player.votingfor = None
            player.arevoting = []

        await self.post_log( "Round " +str(self.round) +" day has ended. Round " +str(self.round)+ " night has begun.")
        await self.post_log("The night phase will last for 2 minutes.")
        for player in self.players:
            if player.alive:
                await player.send_logs(player.role.nightly_message)

        await asyncio.sleep(90)
        await self.post_log("30 seconds remaining in the night phase.")
        await asyncio.sleep(30)
        await self.post_log("Deadline for night actions reached. Calculating...")
        self.queue_actions()
        await self.resolve_sumbitted_actions()

        for player in self.players:
            player.clear_states



    #TODO will eventually need to switch the asyncio.sleep() to a task in the event loop to account for hammering.
    #TODO Also game.hammering:boolean should be declared. Don't get me started on vote locking...
    async def do_day(self):
        self.is_day = True
        self.round += 1

        await self.post_log(
            "Round " + str(self.round-1) + " night has ended. Round " + str(self.round) + " day has begun.\nDay will last for 2 minutes (accelerated day phase. You may begin voting now.")
        await asyncio.sleep(60)
        await self.post_log("60 seconds left in the day.")
        await asyncio.sleep(50)
        await self.post_log("10 seconds left in the day.")
        await asyncio.sleep(10)

        if self.lhlv is None or self.lhlv == "No Lynch":
            await self.post_log("There was no lynch.")
        else:
            await self.attempt_kill_player(self.lhlv, Actions.Killtype.LYNCH)
        self.lhlv = None
        for player in self.players:
            player.clear_states()






    async def attempt_send_chat_faction(self, source, message):

        source = self.getPlayerFromUser(source)


        if source is not None:
            if source.role is not None:
                if self.started:
                    if source.role.speaks_with_faction:
                        for player in source.role.faction.players:
                            await self.bot.send_message(player.member, "["+ self.id_name.upper() +" - FACTION CHAT]"+source.member.name + ": " + message)
                    else:
                        await self.bot.send_message(source.member, "This action isn't allowed for your role.")
                else:
                    await self.bot.send_message(source.member, "The game hasn't started yet")
            else:
                await self.bot.send_message(source.member, "It doesn't appear you've been assigned a role.")
        else:
            await self.bot.send_message(source.member, "It doesn't appear you're in this game. Check to make sure you're using the correct ID.")




    async def self_destruct(self):
        self.roles = []
        self.players = []
        self.factions = []
        ResponseTaskHandler.CURRENT_RUNNING_GAMES.remove(self)
        self.started = False
        self = None











class DeathReveal(Enum):
    FULL_REVEAL = 1
    ALIGNMENT_REVEAL = 2
    NO_REVEAL = 3
    ROLE_BASED = 4





class RoundZeroKill(Enum):
    HOST_SAVE = 1
    INJURY = 2
    MURDER = 3






class RoundZeroPeek(Enum):
    NO_PEEKS = 1
    R0_NEG_PEEK = 2
    FREEWILL = 3


class GamePhases(Enum):
    BLOCKING = 1
    REDIRECTION = 2
    PROTECTION = 3
    KILLING = 4
    INVESTIGATION = 5
    TRACKING_PHASE_1 = 6
    TRACKING_PHASE_2 = 7


































































LIVING_MINI_ID = "406548119816241162"

class PlayerMini:
    def __init__(self, member: discord.member):
        self.member = member
        self.alive = True
        self.currentvotes= 0
        self.votingfor = None

        self.arevoting = []





class GameMini:
    def __init__(self, host=None):
        self.players = []
        self.round = 0
        self.started = False
        self.host = host
        self.lhlv = None



    #function to add players to a game. returns a string that basically functions as what the bot needs to say when it happens, yolo
    def addplayer(self, member:discord.member):

        if self.started:
            return "The game has already started. Please try again after the current game has concluded."

        elif self.getPlayerFromMember(member) is not None:
            return "You are already in this game!"
        else:
            self.players.append(PlayerMini(member))



            return member.name + " has been added to the game. \n" + self.getPlayerList()

    #same with this one add the add one really
    def dropplayer(self, member:discord.member):

        if self.started:
            return "The game has already started. Please ask the host to modkill you instead if you cannot stay."

        elif self.getPlayerFromMember(member) is None:
            return "You are not in this game!"
        else:
            self.players.remove(self.getPlayerFromMember(member))


            return member.name + " has left the game."

    #returns ONLY A TEXT VERSION of the playerlist used for determining players in the game at the start. Use game.players for the actual list of player objects, duh
    def getPlayerList(self):
        playerlist = ""
        for player in self.players:

                playerlist = playerlist + player.member.name +", "


        return "The current players are: " + playerlist.rstrip(", ") + "."




    def gettally(self):

        newlist = sorted(self.players, key=lambda player : len(player.arevoting), reverse=True)

        deadpeople = []
        playersvotingnone =[]
        playersvotingnolynch = []
        finalstring = "Round " + str(self.round) + " tally:\n\n"

        for player in newlist:
            if not len(player.arevoting) == 0 and player.alive:
                finalstring = finalstring + player.member.name + " - " + str(len(player.arevoting)) + " - "
                stringenemies = ""
                for enemy in player.arevoting:
                    stringenemies = stringenemies + enemy.member.name + ", "

                finalstring = finalstring +stringenemies.rstrip(", ") + "\n"

            if player.alive and player.votingfor is None:
                playersvotingnone.append(player)
            elif player.alive and player.votingfor == "no lynch":
                playersvotingnolynch.append(player)
            elif not player.alive:
                deadpeople.append(player)

        stringnolynchers = ""
        for nolyncher in playersvotingnolynch:
            stringnolynchers = stringnolynchers + nolyncher.member.name + ", "

        if not stringnolynchers == "":
            finalstring = finalstring + "No Lynch - " + str(len(playersvotingnolynch)) + " - "+ stringnolynchers.rstrip(", ") + "\n"


        stringnovoters = ""
        for novoter in playersvotingnone:
            stringnovoters = stringnovoters + novoter.member.name + ", "


        if not stringnovoters == "":
            finalstring = finalstring + "No Vote - " + str(len(playersvotingnone)) + " - " + stringnovoters.rstrip(", " +"\n")


        self.updatelhlv()
        stringlhlv = "\n\nLHLV: "
        if self.lhlv is None:
            stringlhlv = stringlhlv + "No Lynch\n\n"
        else:
            stringlhlv = stringlhlv + self.lhlv.member.name +"\n\n"

        finalstring = finalstring + stringlhlv

        stringdeadpeople = ""
        for corpse in deadpeople:
            stringdeadpeople = stringdeadpeople + corpse.member.name + ", "

        if not stringdeadpeople == "":
            finalstring = finalstring + "\nDead players: " + stringdeadpeople.rstrip(", " )+"."





        return finalstring + "\nTotal living players in game: "+ str(len(self.players)-len(deadpeople))




    def applyvote(self, source, target):
        if self.started is False:
            return "The game hasn't even started yet!"
        elif self.round == 0:
            return "There is no voting during round zero."
        elif not source.alive:
            return "You are dead, and cannot vote from the grave."
        elif source.votingfor == target:
            return "You are already voting this target."
        elif target == None:

            self.removepreviousvote(source)
            source.votingfor = None
            return source.member.name + "  unvotes." + "\n"+ self.gettally()
        elif target == "no lynch":
            self.removepreviousvote(source)
            source.votingfor = "no lynch"
            return source.member.name +" votes for no lynch."+ "\n"+ self.gettally()
        elif not target.alive:
            return "Your target is dead. Leave them in the grave, please."
        elif target.alive:
            self.removepreviousvote(source)
            source.votingfor = target
            target.arevoting.append(source)
            return source.member.name +  " voted for " + target.member.name + "."+ "\n "+self.gettally()



        else:
            print(str(source) +", on target: " + str(target))
            return "Something went horribly wrong, and I have no idea what..."




    def updatelhlv(self):

        newlist = sorted(self.players, key=lambda player: len(player.arevoting), reverse=True)
        topvote = len(newlist[0].arevoting)

        tiedfortop=[]

        nolynchvotes = 0
        for player in newlist:

            if player.votingfor == "no lynch":
                nolynchvotes = nolynchvotes+1

            if len(player.arevoting) == topvote:
                tiedfortop.append(player)

        if nolynchvotes >= topvote:
            self.lhlv = None
        elif len(tiedfortop) == 1:
            self.lhlv = newlist[0]



    def removepreviousvote(self, source):
        for player in self.players:
            if source in player.arevoting:
                player.arevoting.remove(source)



    #searches for the current player in the game based on the member being passed in
    def getPlayerFromMember(self, member:discord.member):
        for player in self.players:
            if member.id == player.member.id:
                return player
        return None


    def advanceround(self):
        for player in self.players:
            player.votingfor = None
            player.arevoting = []

        self.round = self.round + 1
        return "Round " +str(self.round-1) +" has ended. Round " +str(self.round)+ " has begun."


    def killplayer(self, player, method):

        if method is None or method == "":

            verb = "killed"
        else:
            verb = method

        player = self.getPlayerFromMember(player)

        if player is None:
            return "That player isn't in the game."
        elif not self.started:
            return "The game hasn't started yet!"
        elif not player.alive:
            return "https://i.imgur.com/MPbX6OD.jpg"
        else:
            player.alive = False
            return player.member.name +" was " +verb +"."

    def reviveplayer(self, player):

        player = self.getPlayerFromMember(player)

        if player is None:
            return "That player isn't in the game."
        elif not self.started:
            return "The game hasn't started yet!"
        elif player.alive:
            return "That player is already alive!"
        else:
            player.alive = True
            return player.member.name + " was revived."







# Backup tallying function
#

    def gettallymage(self):
        # Create a dict to map player/statement ("No Vote") names with names voting for them
        votes = {}
        # Populate with players and voted by lists
        for current in self.players:
            votes.setdefault(current.member.name, [])
        votes.setdefault("No Lynch", [])
        votes.setdefault("No Vote", [])

        # Update voted by lists
        for current in self.players:
            if current.votingfor is None:
                # Since None is default, dead players have that as their votingfor. However, dead people can't vote
                if current.alive:  # Ignore dead people tryin to pull a fast one on Tars
                    votes.get("No Vote").append(current.member.name)
            else:
                # Should only be met by voting "No Lynch" or "No Vote" (instead of none somehow)
                if current.votingfor in votes.keys():
                    votes.get(current.votingfor).append(current.name)
                else:
                    votes.get(current.votingfor.member.name).append(current.member.name)

        # Initalize vars for formatting output string (Java OP)
        talleyOutput = []
        noLynchString = ""
        noVoteString = ""
        playerSearchInt = len(votes.keys())

        for i in range(playerSearchInt):  # once for every player and nolynch/novote
            mostVotes = 0
            votedPlayer = ""

            # find the highest voted player (ties aren't dealt with atm
            for current in votes.keys():
                if len(votes.get(current)) > mostVotes:
                    mostVotes = len(votes.get(current))
                    votedPlayer = current

            # add the highest voted player to the output ary
            if mostVotes != 0:
                votedString = str(votedPlayer) + " - " + str(mostVotes) + " - "
                # add all the voting players to the talley
                for j in range(len(votes.get(votedPlayer))):
                    votedString += votes.get(votedPlayer)[j]
                    # add commas and spaces if it isn't the last player
                    if j != len(votes.get(votedPlayer)) - 1:
                        votedString += ", "

                # Intercept the No Lynch/No Vote lines as they should always be at the bottom
                if votedPlayer == "no lynch":
                    noLynchString = votedString
                elif votedPlayer == "No Vote":
                    noVoteString = votedString
                else:
                    talleyOutput.append(votedString)
                # Remove the voted player so the algorithm doesn't find it again
                votes.pop(votedPlayer, None)

        # Add the No Lynch and No Vote to the end of the talleyOutput
        if noLynchString != "":
            talleyOutput.append(noLynchString)
        if noVoteString != "":
            talleyOutput.append(noVoteString)

        # Concatenate the strings into a single output string
        finishedTalley = ""
        for i in range(len(talleyOutput)):
            finishedTalley += talleyOutput[i]
            if i != len(talleyOutput) - 1:  # if not last line
                finishedTalley += "\n"

        return finishedTalley