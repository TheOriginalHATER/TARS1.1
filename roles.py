from enum import Enum
import WolfUtils
from Actions import COMMAND_FLAGS
import Actions




class Role:

    def __init__(self, faction):
        self.name = "Default"
        self.description = "This is the default role without any alignment. If you're seeing this, something went wrong. Contact a member of Valhalla Procotol immediately."
        self.alignment = None
        self.player = None
        self.nightly_message = "It is now night. Sit tight and wait for morning -- and hope you don't die in the meantime!"


        self.toughness = 0
        self.indestructible = False


        self.flags = []

        #True if needs a target OTHER than factional kill
        self.needs_target = False

        self.faction = faction
        self.speaks_with_faction = False


        #Alignment peeks return modified or false
        self.tinker = None



    def create_action(self, flag, target):
        #Returns None on Normal Villagers
        return None







    def do_vote(self):
        pass



    async def onDeath(self, killtype):
        self.player.alive = False
        await self.player.game.post_log(self.player.name + " " + killtype.tensename)
        await self.player.game.post_log(self.player.name + " Died")

        if self.player.game.reveal_rule == WolfUtils.DeathReveal.FULL_REVEAL:

            await self.player.game.post_log(self.player.name + " was a "+ self.player.role.name + " aligned with the " + self.player.faction.name)

        elif self.player.game.reveal_rule == WolfUtils.DeathReveal.ALIGNMENT_REVEAL:

            await self.player.game.post_log((self.player.name + " was aligned with the " + self.player.faction.name))

        if await self.player.game.check_wincons():
            await self.player.game.self_destruct()

    def onRevive(self):
        pass






class Villager(Role):
    def __init__(self, faction):
        super(Villager, self).__init__(faction)
        self.name = "Normal Villager"
        self.alignment = Alignment.VILLAGE
        self.description = "You are a Normal Villager. Through your vote and your voice, you wield enormous power and influence in the game. Use your power wisely..."


class MafiaGoon(Role):
    def __init__(self, faction):
        super(MafiaGoon, self).__init__(faction)
        self.name = "Mafia Goon"
        self.alignment = Alignment.MAFIA
        self.factional_kill = True
        self.speaks_with_faction = True
        self.description = "You are a Mafia Goon. You may collaborate with your team by using the ?teamchat command in private chat. During the night, use the ?shoot <name> command to set the factional kill target."
        self.nightly_message = "It is now night. Plan with your buddies to kill a player using ?teamchat <message> Send in the kill using ?shoot <target>."


class Cop(Role):
    def __init__(self, faction):
        super(Cop, self).__init__(faction)
        self.description = "You are a Village Cop. You may peek a player each night using ?peek <target name>. "
        self.name = "Cop"
        self.alignment = Alignment.VILLAGE
        self.needs_target = True
        self.nightly_message = "It is now night. You may see a player's alignment by using the ?peek <player> command."
        self.flags.append(COMMAND_FLAGS.PEEK)
        self.peektype = Actions.PeekTypes.BINARY

    def create_action(self, flag, target):
        #Returns an ActionPeek
        if flag == COMMAND_FLAGS.PEEK:
            print("Peek action created...")
            return Actions.ActionPeek(flag, self.player.game, self.player, target, self.peektype)


        else:
            return None

class Miller(Role):
    def __init__(self, faction):
        super(Miller, self).__init__(faction)
        self.name = "Miller"
        self.alignment = Alignment.VILLAGE
        self.description = "You are a Normal Villager. Through your vote and your voice, you wield enormous power and influence in the game. Use your power wisely..."
        self.tinker = True




class Doctor(Role):
    def __init__(self, faction):
        super(Doctor, self).__init__(faction)
        self.description = "You are a Village Doctor. You may peek a player each night using ?peek <target name>. "
        self.name = "Doctor"
        self.alignment = Alignment.VILLAGE
        self.needs_target = True
        self.nightly_message = "It is now night. You may attempt to protect a player by using the ?protect <target> command."
        self.flags.append(COMMAND_FLAGS.PROTECT)
        self.peektype = Actions.PeekTypes.BINARY

    def create_action(self, flag, target):

        if flag == COMMAND_FLAGS.PROTECT:
            return Actions.ActionProtect(flag, self.player.game, self.player, target)


        else:
            return None



















class Alignment(Enum):

    VILLAGE = ("You are aligned with the Village, meaning you win when all evil factions are dead.", 1)
    WOLF = ("You are aligned with the Wolf team, meaning you win when your team has reached parity with the village and all opposing evil factions are dead.",2)
    MAFIA = ("You are aligned with the Mafia team, meaning you win when your team has reached parity with the village and all opposing evil factions are dead.",3)
    SERIAL_KILLER = ("You are aligned with yourself, and you win when you are alive and there is one or fewer other players alive in the game.",4)
    CULT = ("You are aligned with the Cult. You win when the cult has reached parity with the village and all other evil factions are dead.",5)
    NEUTRAL = ("You are neutral, meaning you have an alternate wincon.",6)


    def __init__(self, wincon, number):
        self.wincon = wincon
        self.number = number















