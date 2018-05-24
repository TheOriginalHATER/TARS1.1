import TARSUtils
from robobrowser import RoboBrowser

LOGIN_PAGE = "http://www.neondragon.net/ucp.php?mode=login"

MAIN_FORUM = "http://www.neondragon.net/viewforum.php?f=178"




browser_default = RoboBrowser(parser='html.parser')


async def login():

    br = browser_default
    br.open(LOGIN_PAGE)
    form = br.get_form()
    form["username"] = TARSUtils.NeonUser
    form["password"] = TARSUtils.NeonPass

    br.submit_form(form)
    br.open(MAIN_FORUM)

async def makethread(subject="", message=""):

    br = browser_default

    br.open(MAIN_FORUM)
    br.open("http://www.neondragon.net/posting.php?mode=post&f=178")

    form = br.get_form()
    form["subject"] = "Taco"
    form["message"] = "wat"


    #br.session.headers['Referer'] = "https://www.neondragon.net/posting.php?mode=post&f=178"
    br.submit_form(form, submit=form['post'])
    print(br.url)







class ForumContext():
    def __init__(self, loginpage, baseurl):
        self.loginpage = loginpage
        self.baseurl = baseurl


    def makepost(self, thread, contents):
        return False

    def checkpms(self):
        return False

    def makethread(self, title, contents):
        return False

    def makenewgame(self, title, contents):
        return False


class ForumThread():
    def __init__(self, url):
        pass










