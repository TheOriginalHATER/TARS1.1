from enum import Enum
class Protocols(Enum):
    VALHALLA = ("403645223630012417",10, "valhalla", "Valhalla")
    FOLKVANGR_PLUS = ("403645258434478080",8, "folkvangr++","Fólkvangr++")
    FOLKVANGR = ("403645266273763338",6,"folkvangr","Fólkvangr")
    NASTROND = ("403645269247524865",2,"nastrond", "Náströnd")

    def __init__(self, id, level, rankName, stylizedName):
        self.id = id
        self.level = level
        self.rankName = rankName
        self.stylizedName = stylizedName
