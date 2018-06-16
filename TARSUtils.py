import random
import discord
import bs4
from urllib.request import urlopen
import urllib.request
from EnumProtocols import Protocols
from bs4 import BeautifulSoup as soup
from discord.ext import commands
import configparser
from autocorrect import spell
import asyncio
import math



BLAZE_RANT1 ="Litsen here you piece of shit, I'm so FUCKING angry right now, and I don't know how to explain it, but you're fucking stupid. I've never thought you were a bad player until fucking now. And now I get it. I fucking get it. I've never seen anyone sell someone out who's aligned with them. Who the fuck does that? Not even me like 4 years ago when I used to play in Werewolf. I'm getting so ffffffucking pissed. I'm kinda sad, I'm kinda irritated, I'm kinda annoyed -- as well. But I've never got this angry. I just stopped caring -- and I don't know what to do anymore. Because this shit, Ultor? This shit is the real reason you are a bad player. I'm ashamed that HATER put me in the D-rank with you, cause I would never do such a fucking big fuck-up as you would right now. I told you, word-for-word,\" Majin is mafia, don't tell him.\""
BLAZE_RANT2 ="Since I'm a neutral, I'm sided with both teams, because I got a connection in my tea -- uhh, in the village team -- and a connection in the... mafia team. I got no -- got to know both the rules, so I helped the villagers, and gave fucking Majin out. And you're fucking stupid now, after I told you like seven times yesterday in teamspeak -- about SEVEN times! -- I could remember perfectly because I counted every time. I told you every time, \"DON'T FUCKING TELL ANYONE.\" I says fucking that. And the first thing you do, you don't type it on steam to someone, you fucking put it on the forums? And you fucking openly said it? How am I supposed to be a double agent and fucking try to tr-trick the mafia with them and get to know information from that, if you're fucking telling them that I'm selling them out? How the fuck did you think like that, huh? You think \"uuuggggghhhhh, he's a neutral...who-who cares anywa--\" fuck you. That's what I got to say. FUCK YOU."
SALTY_VIDEOS = ["https://www.youtube.com/watch?v=3KquFZYi6L0", "https://youtu.be/kbBgx0BEuuI?t=66","https://youtu.be/J5GGG0PaSe4?t=31","https://youtu.be/um7QcI8-XiM?t=400"]

MAIN_SERVER_ID = "268524263768588291"

MAGIC_HOES_ID = "415601549759479809"

LOGIN_PAGE = "http://www.neondragon.net/ucp.php?mode=login"

MAIN_FORUM = "http://www.neondragon.net/viewforum.php?f=178"

AUTH_TOKEN = ""
NeonUser = ""
NeonPass = ""


game_topics = []



class ForumPost:
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.link=""


    def displayreadout(self):
        return "Post by " + self.author + ":\n\n"+ self.content + "\n\nDirect link: " + self.link


def config():
    config = configparser.ConfigParser()
    config.read('interrobang.ini')

    global AUTH_TOKEN
    global NeonUser
    global NeonPass
    AUTH_TOKEN = config['DEFAULT']['AUTH_TOKEN']
    NeonUser = config['DEFAULT']['neonuser']
    NeonPass = config['DEFAULT']['neonpass']















def findRankByName(name:str):
    for protocol in Protocols:
        if name.lower() == protocol.rankName.lower() or name.lower() == protocol.stylizedName.lower():
            return protocol
    return None






def checkHighestProtocolNumber(member:discord.Member):
    rank = checkForHighestProtocol(member.roles)
    if rank is None:
        return 0
    return rank.level

def checkForHighestProtocol(roles:list):
    if checkForProtocol(Protocols.VALHALLA.id,roles):
        return Protocols.VALHALLA
    elif checkForProtocol(Protocols.FOLKVANGR_PLUS.id,roles):
        return Protocols.FOLKVANGR_PLUS
    elif checkForProtocol(Protocols.FOLKVANGR.id,roles):
        return Protocols.FOLKVANGR
    elif checkForProtocol(Protocols.NASTROND.id,roles):
        return Protocols.NASTROND
    return None





def findCurrentGames():
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(MAIN_FORUM, None, headers)

    uClient = urlopen(request)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    stickies = page_soup.findAll("tr", {"class": "topicsticky"})

    topics = []

    for sticky in stickies:

        rows = sticky.findAll("td", {"class": "row1"})
        row = rows[1]

        auths = row.findAll("p", {"class": "topicauthor"})

        title = row.a.text
        author = auths[0].a.text
        link = row.a["href"]
        postsrow = rows[2].findAll("p", {"class": "topicdetails"})
        posts = postsrow[0].a.text
        topic = ForumTopic(title, author, link, posts)
        topics.append(topic)


    return topics




async def archiveposts(forumlink, amount):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }

    pages = int(math.ceil(amount / 15))
    posts = []
    for x in range(0, pages):

        request = urllib.request.Request(forumlink + "&start=" + str(x * 15), None, headers)

        uClient = urlopen(request)
        page_html = uClient.read()
        uClient.close()
        page_soup2 = soup(page_html, "html.parser")

        newpostsraw = page_soup2.findAll("div", {"class": "postbody"})
        newpostsauthors = page_soup2.findAll("div", {"class": "postauthor"})
        newpostslinks = page_soup2.findAll("div", {"class": "postsubject"})

        for y in range(0, len(newpostsraw)):
            post = ForumPost(newpostsauthors[y].text, newpostsraw[y].get_text("\n"))
            post.link = "http://www.neondragon.net" + newpostslinks[y].a['href'].lstrip(".").split("&sid")[0]
            post.link= post.link +"#"+ post.link.split("p=")[1]
            posts.append(post)
            asyncio.sleep(0)


    return posts


async def getnewposts(client):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(MAIN_FORUM, None, headers)

    uClient = urlopen(request)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    stickies = page_soup.findAll("tr", {"class": "topicsticky"})

    topics = []

    for sticky in stickies:
        rows = sticky.findAll("td", {"class": "row1"})
        row = rows[1]

        auths = row.findAll("p", {"class": "topicauthor"})

        title = row.a.text
        author = auths[0].a.text
        link = row.a["href"]

        postsrow = rows[2].findAll("p", {"class": "topicdetails"})
        postsnumber = int(postsrow[0].a.text)

        topic = ForumTopic(title, author, link, postsnumber)
        topics.append(topic)
        await asyncio.sleep(0)


    for topic in topics:

        stored = False
        for gametopic in game_topics:

            if topic.title == gametopic.title:

                stored = True
                if topic.posts > gametopic.posts:

                    channel = None
                    if topic.title.startswith("Mafia"):
                        channel = client.get_channel("271099667587137537")
                    elif topic.title.startswith("Assassins") or topic.title.startswith("Witch Hunt"):
                        channel = client.get_channel("271099731298615297")
                    elif topic.title.startswith("WW") or topic.title.startswith("Werewolf"):
                        channel = client.get_channel("271099779029794816")
                    if channel is not None:

                        fetch = topic.posts - gametopic.posts
                        archive = await archiveposts(topic.link, topic.posts)

                        #await client.send_message(channel, str(
                        #    fetch) + " new post(s) detected in topic: " + topic.title + " since last updated.")


                        for x in range(len(archive)-fetch,  len(archive)):
                            readout = str(archive[x].displayreadout())
                            if len(readout) > 1800:

                                reads = [readout[i:i + 1800] for i in range(0, len(readout), 1800)]
                                for read in reads:
                                    await client.send_message(channel, read)


                            else:

                                await client.send_message(channel, readout)


                        await asyncio.sleep(0)

                game_topics.remove(gametopic)
                game_topics.append(topic)


        if not stored:
            game_topics.append(topic)

























def checkForProtocol (id:str, roles:list):

    for x in range(0, len(roles)):
        if roles[x].id == id:
            return True


    return False



def sarcastify(string:str):
    for x in range(0, len(string)):
        chararray = list(string)

        r = random.randint(0, 1)
        if r == 0:

            chararray[x] = string[x].lower()
            string = ''.join(chararray)
        else:
            chararray[x] = string[x].upper()
            string = ''.join(chararray)

    return string


def getRandomMarkov():
    markovs = getMarkovs()
    r = random.randint(0, len(markovs)-1)

    return markovs[r]


def getMarkovs():
    file = open("markov.txt", "r")
    markovs = []

    for line in file:
        markovs.append(line.rstrip())

    return markovs


def getvids():
    file = open("memevids.txt", "r")
    vids = []

    for line in file:
        vids.append(line.rstrip())

    return vids


easteregg = "https://i.redd.it/raut0417tzj01.jpg"

#Use channel if the uer won't be pulled from ctx, like for targeting in PM
def getUserFromString(ctx,string,channel=None):



    if channel is None:
        channel = ctx.message.channel

    try:

        return commands.MemberConverter(ctx, string).convert()


    except commands.errors.BadArgument:
        members = channel.server.members

        string2 = string.lower()
        while len(string2) > 0:
            for member in members:
                if member.name.lower().startswith(string2):
                    return member

            for member in members:
                if string2 in member.name.lower():
                    return member
            string2 = string2[0:(len(string2)-1)]



        return None










def blazify(string):
    if string is None:
      return ""


    #split the str into words
    indexedstr = string.split(" ")

    #autocorrect the str with a shitty spellchecker
    newindex = []
    for thisword in indexedstr:
        if "." in thisword or "," in thisword or "?" in thisword or "!" in thisword or "--" in thisword or ";" in thisword:
            newword = thisword
        else:
            newword = spell(thisword)
        newindex.append(newword)




    #Set up next-to finger keys:

    keyboardlayout = ['w','q','w','e','r','t','y','i','o','p',';','l','k','j','h','g','f','d','s','a','z','x','c','v','b','n','m',',','m']


    def getnextkey(letter):
        if letter in keyboardlayout:
            index = keyboardlayout.index(letter, 1, 28)

            if random.randint(0,1) == 0:
                return keyboardlayout[(index+1)]
            return keyboardlayout[(index - 1)]




        return letter


    #throw in random typos

    wordcounter = 0
    for thisword in newindex:
        charcounter = 0

        thislist = list(thisword)


        for char in thislist:

            if random.randint(0, 12) == 0:

                thislist[charcounter] = getnextkey(char)



            charcounter =charcounter +1
        newindex[wordcounter] = "".join(thislist)
        wordcounter = wordcounter+1



    #Build the finished str

    finishedstr = ""

    for word in newindex:

        if random.randint(0,7) == 0:
            space = ""
        else:
            space = " "

        finishedstr = finishedstr + word.lower() + space

    return finishedstr.replace("?", "????").replace("!", "!!1!11").replace(".", "!!").replace("literally", "litterary").replace("listen","litsen").replace("literary", "litraelly").replace("ea", "ae")





def get8ballresponse():
    responses = ["I won't dignify that with an answer.","Yes","No","Bruh...Why would you even ask that..?","Of course, dumbass!","maybe","it's possible", "when hell freezes over", "fuck off, not now ok?", "if you're nice to me", "Why do I give a shit?","damnit blaze, you again?"]
    number = random.randint(0, len(responses) - 1)

    return responses[number]


def lookupInsult(member):
    file = open("insult.txt", "r")
    sults = []

    for line in file:
        sults.append(line.rstrip())

    number  = random.randint(0, len(sults) - 1)

    text = sults[number]
    text2 = text.replace("&NAME&",member.mention)
    return text2





class ForumTopic:
    def __init__(self, title, author, link, posts):
        self.title = title
        self.author = author
        self.link = "http://www.neondragon.net" + link.lstrip(".")
        self.posts = posts







