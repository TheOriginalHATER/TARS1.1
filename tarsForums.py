import TARSUtils
from robobrowser import RoboBrowser

LOGIN_PAGE = "http://www.neondragon.net/ucp.php?mode=login"

MAIN_FORUM = "http://www.neondragon.net/viewforum.php?f=178"




browser_default = RoboBrowser()


def login(br:RoboBrowser):
    br.open(LOGIN_PAGE)
    form = br.get_form()
    form["username"] = TARSUtils.NeonUser #doesn't exist yet
    form["password"] = TARSUtils.NeonPass

    br.submit_form(form)
    print(str(br.url))








