import random
import discord
import bs4
from urllib.request import urlopen
import urllib.request
from EnumProtocols import Protocols
from bs4 import BeautifulSoup as soup
from discord.ext import commands
import configparser



BLAZE_RANT1 ="Litsen here you piece of shit, I'm so FUCKING angry right now, and I don't know how to explain it, but you're fucking stupid. I've never thought you were a bad player until fucking now. And now I get it. I fucking get it. I've never seen anyone sell someone out who's aligned with them. Who the fuck does that? Not even me like 4 years ago when I used to play in Werewolf. I'm getting so ffffffucking pissed. I'm kinda sad, I'm kinda irritated, I'm kinda annoyed -- as well. But I've never got this angry. I just stopped caring -- and I don't know what to do anymore. Because this shit, Ultor? This shit is the real reason you are a bad player. I'm ashamed that HATER put me in the D-rank with you, cause I would never do such a fucking big fuck-up as you would right now. I told you, word-for-word,\" Majin is mafia, don't tell him.\""
BLAZE_RANT2 ="Since I'm a neutral, I'm sided with both teams, because I got a connection in my tea -- uhh, in the village team -- and a connection in the... mafia team. I got no -- got to know both the rules, so I helped the villagers, and gave fucking Majin out. And you're fucking stupid now, after I told you like seven times yesterday in teamspeak -- about SEVEN times! -- I could remember perfectly because I counted every time. I told you every time, \"DON'T FUCKING TELL ANYONE.\" I says fucking that. And the first thing you do, you don't type it on steam to someone, you fucking put it on the forums? And you fucking openly said it? How am I supposed to be a double agent and fucking try to tr-trick the mafia with them and get to know information from that, if you're fucking telling them that I'm selling them out? How the fuck did you think like that, huh? You think \"uuuggggghhhhh, he's a neutral...who-who cares anywa--\" fuck you. That's what I got to say. FUCK YOU."
SALTY_VIDEOS = ["https://www.youtube.com/watch?v=3KquFZYi6L0", "https://youtu.be/kbBgx0BEuuI?t=66","https://youtu.be/J5GGG0PaSe4?t=31","https://youtu.be/um7QcI8-XiM?t=400"]

MAIN_SERVER_ID = "268524263768588291"

MAGIC_HOES_ID = "415601549759479809"

LOGIN_PAGE = "http://www.neondragon.net/ucp.php?mode=login"

MAIN_FORUM = "http://www.neondragon.net/viewforum.php?f=178"

AUTH_TOKEN = ""




def config():
    config = configparser.ConfigParser()
    config.read('interrobang.ini')

    global AUTH_TOKEN
    AUTH_TOKEN = config['DEFAULT']['AUTH_TOKEN']














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
        topic = ForumTopic(title, author, link)
        topics.append(topic)

    return topics




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
            print(string2)


        return None





















def lookupInsult(member:discord.Member):
    if member.id == 3:
        return "lol"

    else:
        return "ayyluhmayoh"


class ForumTopic:
    def __init__(self, title, author, link):
        self.title = title
        self.author = author
        self.link = "http://www.neondragon.net" + link.lstrip(".")






