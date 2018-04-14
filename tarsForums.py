import TARSUtils
from robobrowser import RoboBrowser

LOGIN_PAGE = "http://www.neondragon.net/ucp.php?mode=login"

MAIN_FORUM = "http://www.neondragon.net/viewforum.php?f=178"




browser_default = RoboBrowser()


def login():

    br = browser_default
    br.open(LOGIN_PAGE)
    form = br.get_form()
    form["username"] = TARSUtils.NeonUser
    form["password"] = TARSUtils.NeonPass

    br.submit_form(form)
    print(br.url)








