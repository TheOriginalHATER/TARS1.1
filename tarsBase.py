import random
import urllib.request
import urllib.parse
import re
import discord
import TARSUtils
import test
import markovify
from EnumProtocols import Protocols
from discord.ext import commands
from WolfUtils import PlayerMini, GameMini, GamePhases
import WolfUtils
import scrython
import asyncio
import ResponseTaskHandler
from Actions import Killtype, COMMAND_FLAGS



TARSUtils.config()
bot = commands.Bot(description="TARS is programmed to facilitate the play and hosting of Werewolf and Mafia style elimination games.", command_prefix=("?", "TARS, ","Tars, ","tars, "))





@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)




@bot.event
async def on_reaction_add(reaction, user):
    print("Reaction detected.")
    if ("🍆" in str(reaction.emoji)):
        await bot.add_reaction(reaction.message, "🍆")



@bot.event
async def on_message(message):

    if ("🍆" in str(message.content)):
        await bot.add_reaction(message, "🍆")


    await bot.process_commands(message)







@commands.cooldown(rate=1, per=60, type=commands.BucketType.server)
@bot.command(pass_context=True)
async def blazerant(ctx, *,args =""):

    if(TARSUtils.checkHighestProtocolNumber(ctx.message.author) > 1):
        if args.lower() == "tts":

            await bot.send_message(ctx.message.channel, TARSUtils.BLAZE_RANT1, tts=True)
            await bot.send_message(ctx.message.channel, TARSUtils.BLAZE_RANT2, tts=True)
        elif args.lower() == "song":

            await bot.say(" https://clyp.it/k3z2c1d1 ")
        else:
            await bot.say(TARSUtils.BLAZE_RANT1)
            await bot.say(TARSUtils.BLAZE_RANT2)
    else:
        await bot.say("You need a higher access protocol to do that.")

@commands.cooldown(rate=1, per=10, type=commands.BucketType.server)
@bot.command(pass_context=True)
async def nacl(ctx):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        randomsalt = random.randint(0,len(TARSUtils.SALTY_VIDEOS)-1)
        await bot.say(TARSUtils.SALTY_VIDEOS[randomsalt])


@bot.command(pass_context=True)
async def currentgame(ctx):

    await bot.say("Scanning topics...")
    games = TARSUtils.findCurrentGames()

    if len(games) == 0:
        await bot.say("There don't appear to be any currently running game topics.")
    elif len(games) == 1:
        await bot.say("The current game is:")
    else:
        await bot.say("The current games are:")

    for game in games:
        await bot.say(game.title + " by " + game.author + ". Link: " + game.link)


#Mentions a player
@commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
@bot.command(pass_context=True)
async def poke(ctx, member:discord.Member):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        await bot.say(ctx.message.author.name + " pokes " + member.mention)

#Waters Numble. Duh.
#Gated to admins as of 1/24/18 because people kept abusing it and numble got mad
@commands.cooldown(rate=1, per=10, type=commands.BucketType.server)
@bot.command(pass_context=True)
async def houseplant(ctx):
    if await checkPermissionRequired(Protocols.FOLKVANGR_PLUS, ctx.message.author, ctx.message.channel):
        if ctx.message.author.id == "271101897388064783":
            await bot.say("You cannot water yourself! Silly houseplant!")

        else:
            await bot.say(ctx.message.author.name + " waters " + "<@271101897388064783> .")


#Mentions a player, outputs a taco emoji, and reacts with a taco
@bot.command(pass_context=True)
async def givetaco(ctx,*, target):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):

        member = TARSUtils.getUserFromString(ctx, target)


        if member is not None:
            await bot.say(ctx.message.author.name + " gives " + member.mention + " a taco.")
            await bot.add_reaction(ctx.message, "🌮")
            await bot.say("🌮")
        else:
            await bot.say("Couldn't identify anyone in this channel by that name. Try using a @mention.")



#returns a random markov from the list of ones from the werty conversation
@commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
@bot.command(pass_context=True)
async def werty(ctx):
    chosenMarkov =  TARSUtils.getRandomMarkov()
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        await bot.send_message(ctx.message.channel,chosenMarkov,tts=True)



#runs the last several thousand messages through a markov chain. Lulz result.
@commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
@bot.command(pass_context=True)
async def markov(ctx,*,arg=None):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        if arg is not None:
            arg = arg.lower()
        else:
            arg = ""
        hard = False

        messagelimit = 4000

        if arg == "me harder daddy":
            if not await checkPermissionRequired(Protocols.FOLKVANGR, ctx.message.author, ctx.message.channel):
                #only admins allowed to use this command
                return
            messagelimit = 12000
            hard = True
            await bot.say("You want my big hard markov chain? Ohhhh yeahhhh....")
        else:
            await bot.say("Attempting...")
        chain = " "
        lastmessage = None

        async for message in bot.logs_from(ctx.message.channel, limit=messagelimit):
            if not message.author.id == "403394686816878593":
                if ":twerkriot:" not in message.content.lower():
                    lastmessage = message
                    chain = chain + message.content.lower() + "\n"

        if not arg == "oldest":

            model = markovify.NewlineText(chain)

            if hard:
                sentence = model.make_short_sentence(550, 210, tries=5000)
            elif (not arg == "") and (arg is not None) and (not arg == "quiet") and (not arg == "sarcastify"):
                sentence = await make_seeded_sentence(model, arg, 1000, 500, 30)
            else:
                sentence = model.make_short_sentence(500, 120, tries=400)




            if sentence is None:
                await bot.say("Could not construct a sentence in the given number of tries.")

            elif arg == "sarcastify":

                await bot.send_message(ctx.message.channel, TARSUtils.sarcastify(sentence), tts=True)

            elif arg == "quiet":
                await bot.send_message(ctx.message.channel, sentence)
            elif hard:

                await bot.send_message(ctx.message.channel, "OH YEAH BABY, "+sentence.upper(), tts=True)

            else:
                await bot.send_message(ctx.message.channel, sentence, tts=True)
        else:
            await bot.say("Currently the messages I'm choosing from were logged from: " + str(lastmessage.timestamp) + " to " + str(ctx.message.timestamp))


async def make_seeded_sentence(model, seed, tries, max_chars, min_chars=0):

    try:
        for _ in range(tries):
            sentence = model.make_sentence_with_start(seed, False)
            if sentence and len(sentence) <= max_chars and len(sentence) >= min_chars:
                return sentence

    #YOLO I HAD TO TRY SOMETHING
    except Exception:
        print("WARNING...!")
        return "There was definitely an error here. But hopefully the bot didn't crash, so that's good."



@bot.command(pass_context=True)
async def requestaccess(ctx, rankRaw, forumid):

    rankRaw = rankRaw.lower()

    rank = TARSUtils.findRankByName(rankRaw)
    if rank is None:
        await bot.say("Rank name not recognized. Please try inputting your requested rank name again.")
    else:
        if rank.level <= TARSUtils.checkHighestProtocolNumber(ctx.message.author):
            await bot.say("You are applying for a rank with a clearance level equal to or below one which you already have.")
            #LEL

        elif rank.level > 2:
            await bot.say("Your request has been logged. At this time there is no automatic access granted to protocols above Náströnd.")
            print(rank.stylizedName +" protocol requested by " + ctx.message.author.name + " with forum id: " + forumid)

            #LOL FUCK YOU FOR BEING POWER HUNGRY BIIIIIIIIIIITCH
        elif rank.level == 2:
            await bot.say("Your information has been logged. Request for Náströnd protocols granted.")
            id = discord.utils.get(ctx.message.server.roles, id=Protocols.NASTROND.id)
            await bot.add_roles(ctx.message.author, id)

            print("Náströnd protocol requested by " +ctx.message.author.name + " with forum id: " + forumid)
            #SO YOU KNOW YOUR FUCKING PLACE YOU GRUNT-ASS BITCH




#Returns some goddamn FUCKING HELPFUL info about ranks since these FUCKING IDIOTS can't understand...j/k lol
@bot.command(pass_context=True)
async def rankhelp(ctx):
    await bot.say("Ranks are used to determine your access level for using TARS.")
    await bot.say("Náströnd protocols provide standard access to most of the bot's functions. Náströnd protocols are automatically assigned to any member who links their Neondragon forums account with their discord account via the ?requestaccess command.")
    await bot.say("Fólkvangr protocols provide an elevated level of access to the bot's functions and data. Fólkvangr protocols are given to the host of any running game.")
    await bot.say("Fólkvangr++ protocols provide access to most of the bots functions and data. Permamods are always given this access, as well as minor developers.")
    await bot.say(
        "Valhalla protocols provide expedited priority and access to all of the bots functions and data, as well as all development tools, including the ability to execute code snippets simply by sending them in a message to the bot. This access is only given to developers.")
    await bot.say("To request a rank, use the ?requestaccess command. The syntax for the command is: ?requestaccess <rank name> <forum id>")
    await bot.say("Your forum id is the 4 or 5 digit number at the end of your forum profile's URL.")



#Returns the given string in a mix of upper and lower case letters.
@bot.command(pass_context=True)
async def sarcastify(ctx, *, string):

    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        if string == "blazerant":
            await bot.say(TARSUtils.sarcastify(TARSUtils.BLAZE_RANT1))
            await bot.say(TARSUtils.sarcastify(TARSUtils.BLAZE_RANT2))
        else:
            await bot.say(TARSUtils.sarcastify(string))



#standard foreign language greeting commands


@bot.command(pass_context=True)
async def hola(ctx):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        await bot.say("¡Hola, " + ctx.message.author.mention + "! ¡Bienvenido! (For a more detailed welcome, try the greetme command.)")


@bot.command(pass_context=True)
async def hej(ctx):
    if await checkPermissionRequired(Protocols.NASTROND,ctx.message.author, ctx.message.channel):
        await bot.say("Hej, " + ctx.message.author.mention + "! Det er godt at se dig igen! (For a more detailed welcome, try the greetme command.)")


@bot.command(pass_context=True)
async def hei(ctx):
    if await checkPermissionRequired(Protocols.NASTROND,ctx.message.author, ctx.message.channel):
        await bot.say("Velkommen, " + ctx.message.author.mention + "! Hyggelig å se deg! (For a more detailed welcome, try the greetme command.)")





#this function is our default check for permissions. Returns a boolean.
async def checkPermissionRequired(rank:Protocols,user:discord.User,feedbackChannel):
    server = bot.get_server(TARSUtils.MAIN_SERVER_ID)
    member = discord.utils.get(server.members, id=user.id)


    sideserver1 = bot.get_server(TARSUtils.MAGIC_HOES_ID)
    sideserver2 = bot.get_server("409172699634597891")
    member1 = discord.utils.get(sideserver1.members, id=user.id)
    member2 = discord.utils.get(sideserver2.members, id=user.id)
    if member1 is not None or member2 is not None:
        return True

    if member is None:
        await bot.send_message(feedbackChannel,"Something went wrong. Perhaps you are not a member of the main discord server.")
        return False

    elif (rank.level > TARSUtils.checkHighestProtocolNumber(member)):

        await bot.send_message(feedbackChannel, "I'm sorry, it appears you don't have the required rank to access this. You need a protocol level of " + rank.stylizedName +" or higher. See ?rankhelp for more information.")
        return False
    else:
        return True







#Standard greetme stuff. Most of it's automated now, but some of it's still hardcoded.
@bot.command(pass_context=True)
async def greetme(ctx):
    await bot.say("Analyzing user data...")

    roles = ctx.message.author.roles
    server = bot.get_server(TARSUtils.MAIN_SERVER_ID)
    member = discord.utils.get(server.members, id=ctx.message.author.id)

    if member is not None:
        roles = member.roles


    if ctx.message.author.id == "190892160101384203":
        await bot.say(
            "Hello, Miss Von Sperling. Fólkvangr protocols engaged. You have access to some administrative functions and data.")

    elif ctx.message.author.id == "226128331311939584" and await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        await bot.say(
            "Hello, MMage. Valhalla protocols engaged. You have access to all taco-related functions and data.")
        await bot.say("Have a 🌮 day.")

    elif ctx.message.author.id == "271294930561925120":
        await bot.say(
            "Hola, Dendee. Fólkvangr protocols engaged. You have access to some administrative functions and data.")

    elif TARSUtils.checkForProtocol(Protocols.VALHALLA.id, roles):
        await bot.say("It's good to see you, " + ctx.message.author.mention + ". Valhalla protocols engaged. You have expedited access to all administrative functions and data.")

    elif TARSUtils.checkForProtocol(Protocols.FOLKVANGR_PLUS.id, roles):
        await bot.say(
            "Hello," + ctx.message.author.mention + ". Fólkvangr++ protocols engaged. You have access to most administrative functions and data.")
    elif TARSUtils.checkForProtocol(Protocols.FOLKVANGR.id, roles):
        await bot.say(
            "Hello," + ctx.message.author.mention + ". Fólkvangr protocols engaged. You have access to some administrative functions and data.")

    elif TARSUtils.checkForProtocol(Protocols.NASTROND.id, roles):
        await bot.say(
            "Hello, " + ctx.message.author.mention + ". Náströnd protocols engaged. You have standard access to functions and data.")

    else:

        await bot.say("Hello, " + ctx.message.author.mention + ". Welcome.  You have not yet applied for protocol access, and so have restricted access to functions and data.")
        await bot.say("You may apply for standard Nastrond protocol access via the ?requestaccess command. (Syntax: ?requestaccess nastrond <forumId>. Your forum id is the 4 or 5 digit number at the end of the url of your forum profile.")










@bot.command()
async def memevid():
    vids = TARSUtils.getvids()

    r = random.randint(0, len(vids) - 1)

    await bot.say(vids[r])



@bot.command()
async def addvid(video):
    pass














#werewolf stuff

#this is stuff for actual independently-hosted bot games.



@bot.command(pass_context=True)
async def join(ctx):
    game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
    if ctx.message.channel.is_private:
        await bot.say("You can't start a game in a private channel...")
    else:
        if game is None:
            game = WolfUtils.AutoGame(bot, ctx.message.channel)
        await game.addplayer(ctx.message.author)

@bot.command(pass_context=True)
async def drop(ctx):
    game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
    if game is not None:
        if ctx.message.channel.is_private:
            await bot.say("You can't drop from a game in a private channel...")

        else:
            await game.dropplayer(ctx.message.author)
    else:
        await  bot.say("There doesn't appear to be a game running here to drop from.")




@bot.command(pass_context=True)
async def start(ctx):
    game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
    if game is None:
        await bot.say("No game currently waiting to start in this channel. You can create a new one with the ?join command.")

    elif game.started:
        await bot.say(
            "A game is already running in this channel")

    else:
        await game.start_game()

@bot.command(pass_context=True)
async def teamchat(ctx, id, *, message=""):
    game = ResponseTaskHandler.find_game_by_id(id)
    if game is None:
        game = ResponseTaskHandler.find_first_game_from_user(ctx.message.author)

        if game is None:
             await bot.say("Sorry, I couldn't find any games you are in.")
        else:
            await game.attempt_send_chat_faction(ctx.message.author, id + " " + message)
    else:
        await game.attempt_send_chat_faction(ctx.message.author, message)




@bot.command(pass_context=True)
async def shoot(ctx, targetName=None, game_id=None):
    await WolfUtils.send_remote_action(ctx, bot, COMMAND_FLAGS.SHOOT, targetName, game_id)

@bot.command(pass_context=True)
async def peek(ctx, targetName=None, game_id=None):
    await WolfUtils.send_remote_action(ctx, bot, COMMAND_FLAGS.PEEK, targetName, game_id)


@bot.command(pass_context=True)
async def vote(ctx, *, target=None):
    game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
    if game is None:
        await bot.say(
            "No game currently running in this channel.")
    elif target is None:
        await bot.say("No target selected. If you would like to remove your vote, use the ?unvote command.")

    elif target.lower() == "nolynch" or target.lower() == "no lynch":
        await game.applyvote(ctx.message.author, "no lynch")
    else:
        user = TARSUtils.getUserFromString(ctx, target)

        if user is None:
            await bot.say("No user in this server with that name. Try using a @mention.")
        else:

            player = game.getPlayerFromUser(user)
            if player is None:
                await bot.say(user.name + " doesn't appear to be playing.")

            else:
                await game.applyvote(ctx.message.author, player)

@bot.command(pass_context=True)
async def unvote(ctx):
    game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
    if game is None:
        await bot.say(
            "No game currently running in this channel.")
    else:
        await game.applyvote(ctx.message.author, None)












@bot.command(pass_context=True)
async def advertise(ctx):
    if await checkPermissionRequired(Protocols.VALHALLA,ctx.message.author, ctx.message.channel):
        await bot.say("@here TARS's Auto-Hosting feature is now in Beta. You can join games via the ?join command.")













@bot.command(pass_context = True, aliases = ["forcekill","modkill"])
async def fkill(ctx, targetname):
    if await checkPermissionRequired(Protocols.VALHALLA, ctx.message.author, ctx.message.channel):
        game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
        if game is None:
            await bot.say(
                "No game currently running or pending in this channel.")
        else:
            targ = TARSUtils.getUserFromString(ctx, targetname)
            if targ is not None:
                player = game.getPlayerFromUser(targ)
                if player is not None:
                    await game.attempt_kill_player(player, Killtype.MODKILL)
                else:
                    await bot.say(
                        targ.name + " is not in the game currently running in this channel.")
            else:
                await bot.say("Could not find a user in channel with that name.")




@bot.command(pass_context = True, aliases = ["forcestop","killswitch"])
async def fstop(ctx):
    if await checkPermissionRequired(Protocols.VALHALLA, ctx.message.author, ctx.message.channel):
        game = ResponseTaskHandler.find_game_by_channel(ctx.message.channel)
        if game is None:
            await bot.say(
                "No game currently running or pending in this channel.")
        else:
            await bot.say("Attempting to force game shutdown...")
            await game.self_destruct()
            await bot.say("Game forcibly stopped by " + ctx.message.author.name)















#mini stuff


#these are our global variables:    

#whatever game is currently going on
currentmini = None

#whatever host is next in the queue to be approved (if any)
pendinghost = None

#whether the pending host had Folkvangr protocols before starting the game (so the bot knows whether or not to take away the rank after the game ends)
had_rank = False


#The thing that starts it all. This runs a couple checks then puts in the player as the pendinghost if everything's all good
@bot.command(pass_context=True)
async def hostmini(ctx):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        global pendinghost
        global currentmini
        if currentmini is not None:

            await bot.say("Please wait for the current Mini to be finished before signing up to host a new one.")

        elif pendinghost is not None:

            # HOW ABOUT WAITING YOUR FUCKING TURN DUMBASS
            await bot.say("There is already a host pending approval. Wait for them to be accepted or declined first.")

        else:
            await bot.say("You are now waiting to be approved or declined to host WW Mini.")
            pendinghost = ctx.message.author



#This lets a permamod, discord mod, or developer approve hosts for a mini
@bot.command(pass_context=True)
async def approvehost(ctx):
    if await checkPermissionRequired(Protocols.FOLKVANGR_PLUS, ctx.message.author, ctx.message.channel):
        global currentmini
        global pendinghost
        global had_rank

        if currentmini is None:

            #First check to see whether you have to give them a rank
            if TARSUtils.checkHighestProtocolNumber(pendinghost) > 3:
                had_rank = True
            else:
                id = discord.utils.get(ctx.message.server.roles, id=Protocols.FOLKVANGR.id)
                await bot.add_roles(pendinghost, id)
                await bot.say(
                    pendinghost.mention + " has been cleared for and assigned temporary Folkvangr Protocol access.")


            #Crate a new instance of GameMini, passing in the pendinghost as the argument for host.

            currentmini= GameMini(pendinghost)
            await bot.say(pendinghost.mention + " has started a WW Mini! Use ?joinmini to join it!")
        else:
            await bot.say("There is already a game in progress with an approved host.")



#same thing but this time denying.
@bot.command(pass_context=True)
async def denyhost(ctx):
    if await checkPermissionRequired(Protocols.FOLKVANGR_PLUS, ctx.message.author, ctx.message.channel):
            global currentmini
            global pendinghost
            if (not currentmini == None ) and pendinghost == None:
                await bot.say(ctx.message.author.mention + " has been declined for hosting.")


                #resetting the pendinghost so others can try
                pendinghost = None

            else:
                await bot.say("Game already in progress or no host pending approval.")




#lets players join the WW Mini
@bot.command(pass_context=True)
async def joinmini(ctx):
    if await checkPermissionRequired(Protocols.NASTROND, ctx.message.author, ctx.message.channel):
        global currentmini

        if currentmini == None:
            await bot.say("No mini in progress. Please sign up for hosting approval via the ?hostmini command")
        else:
            await bot.say(currentmini.addplayer(ctx.message.author))


#leaving the WW mini
@bot.command(pass_context=True)
async def leavemini(ctx):

    global currentmini

    if currentmini == None:
        await bot.say("No mini in progress to leave!")

    else:

        await bot.say(currentmini.dropplayer(ctx.message.author))
        await bot.say(currentmini.getPlayerList())



@bot.command(pass_context=True)
async def startmini(ctx):
    if await checkPermissionRequired(Protocols.FOLKVANGR, ctx.message.author, ctx.message.channel):
        if currentmini is None:
            await bot.say("There is no game currently in signups to run!")
        elif currentmini.started:
            await bot.say("Already a game in progress!")
        else:
            await bot.say("The game has started! It is now Round 0...")
            currentmini.started = True
            for player in currentmini.players:
                    print(player.member.name)
                    print(WolfUtils.LIVING_MINI_ID)
                    print(str(len(ctx.message.server.roles)))

                    livingplayerid = discord.utils.get(ctx.message.server.roles,name="Living WWM Player")
                    print(str(livingplayerid))


                    await bot.add_roles(player.member, livingplayerid)







#command to vote other player IN PROGRESS
@bot.command(pass_context=True)
async def votemini(ctx, member:discord.Member):
    if currentmini is None:
        await bot.say("There is no game currently in progress.")

    elif currentmini.getPlayerFromMember(ctx.message.author) is None:
        await bot.say("You aren't even in the game -- stop it!")
    elif currentmini.getPlayerFromMember(member) is None:
        await bot.say("That player isn't in the game.")
    else:
        await bot.say(currentmini.applyvote(currentmini.getPlayerFromMember(ctx.message.author),currentmini.getPlayerFromMember(member)))



#command to vote other player IN PROGRESS
@bot.command(pass_context=True)
async def unvotemini(ctx):
    if currentmini is None:
        await bot.say("There is no game currently in progress.")

    elif currentmini.getPlayerFromMember(ctx.message.author) is None:
        await bot.say("You aren't even in the game -- stop it!")
    else:
        await bot.say(currentmini.applyvote(currentmini.getPlayerFromMember(ctx.message.author),None))


#command to vote other player IN PROGRESS
@bot.command(pass_context=True)
async def nolynchmini(ctx):
    if currentmini is None:
        await bot.say("There is no game currently in progress.")

    elif currentmini.getPlayerFromMember(ctx.message.author) is None:
        await bot.say("You aren't even in the game -- stop it!")
    else:
        await bot.say(currentmini.applyvote(currentmini.getPlayerFromMember(ctx.message.author),"no lynch"))




#command to vote other player IN PROGRESS
@bot.command(pass_context=True)
async def tallymini(ctx):
    if currentmini is None:
        await bot.say("There is no game currently in progress.")
    elif not currentmini.started:
        await bot.say("The game hasn't started yet.")
    else:
        await bot.say(currentmini.gettally())


#command to advance to the next round IN PROGRESS
@bot.command(pass_context=True)
async def nextround(ctx):
    if await checkPermissionRequired(Protocols.FOLKVANGR, ctx.message.author, ctx.message.channel):
        if currentmini is None:
            await bot.say("There is no game currently running.")
        elif not currentmini.started:
            await bot.say("The game hasn't started yet -- use ?startmini when all players have join to start the game.")
        else:
            await bot.say(currentmini.advanceround())


# command to kill players
@bot.command(pass_context=True)
async def killmini(ctx, member: discord.Member, *, method=""):
    if await checkPermissionRequired(Protocols.FOLKVANGR, ctx.message.author, ctx.message.channel):
        if currentmini is None:
            await bot.say("There is no game currently running.")
        else:
            response = currentmini.killplayer(member, method)
            if "was" in response:
                livingplayerid = discord.utils.get(ctx.message.server.roles, name="Living WWM Player")
                await bot.remove_roles(member, livingplayerid)
            await bot.say(response)





# command to revive players
@bot.command(pass_context=True)
async def revivemini(ctx, member: discord.Member):
    if await checkPermissionRequired(Protocols.FOLKVANGR, ctx.message.author, ctx.message.channel):
        if currentmini is None:
            await bot.say("There is no game currently running.")
        else:
            response = currentmini.reviveplayer(member)
            if "was" in response:
                livingplayerid = discord.utils.get(ctx.message.server.roles, name="Living WWM Player")
                await bot.add_roles(member, livingplayerid)
            await bot.say(response)



#command to end the mini
@bot.command(pass_context=True)
async def endmini(ctx):
    if await checkPermissionRequired(Protocols.FOLKVANGR, ctx.message.author, ctx.message.channel):
        global currentmini
        global pendinghost
        global had_rank
        if currentmini == None:
            await bot.say("No mini currently in progress!")
        else:
            if not had_rank:
                id = discord.utils.get(ctx.message.server.roles, id=Protocols.FOLKVANGR.id)
                await bot.remove_roles(currentmini.host, id)
                await bot.say("Temporary Folkvangr access protocol removed from " + currentmini.host.name)

            for player in currentmini.players:
                livingplayerid = discord.utils.get(ctx.message.server.roles, name="Living WWM Player")
                await bot.remove_roles(player.member, livingplayerid)

            had_rank = False
            pendinghost = None
            currentmini = None

            await bot.say(ctx.message.author.name + " ended the game.")











bot.run(TARSUtils.AUTH_TOKEN)

