from enum import Enum
import WolfUtils
import roles
import random


class COMMAND_FLAGS(Enum):
    SHOOT = 1
    PEEK = 2
    MAUL = 3
    PROTECT = 4





class Action:

    def __init__(self, flag, game, source, target):
        self.game = game
        self.source = source
        self.target = target
        self.phase = None
        self.unblockable = False
        self.is_r0_action = False
        self.flag = flag
        self.factionbased = False


    # Standard targeting for standard stuff
    async def target_valid(self):
        if not self.source.alive:
            await self.source.send_logs("You cannot use this action whilst dead.")
            return False
        elif not self.target.alive:
            await self.source.send_logs("You cannot use this action on a dead target.")
            return False
        elif self.game.is_day:
            await self.source.send_logs("You cannot use this action in the daytime.")
            return False
        else:
            await self.source.send_logs("Target logged successfully")
            return True

    def resolve_valid(self):
        if not self.source.alive:

            return False
        elif not self.target.alive:

            return False
        elif self.source.is_blocked and (not self.unblockable):
            return False

        else:
            return True

    # The method that will run once the correct phase of the game is reached and it the action is valid to resolve
    async def resolve_effects(self):
        return False

    async def round_zero(self):
        return False






class ActionProtect(Action):
    def __init__(self,flag,game,source,target):
        super(ActionProtect, self).__init__(flag, game, source, target)

        #Declare the gamephase that this action resolves in
        self.phase = WolfUtils.GamePhases.PROTECTION


    #When this action is called to resolve via game.resolve_phase_actions() for GamePhases.PROTECTION
    async def resolve_effects(self):
        if self.resolve_valid():
            self.target.is_protected = True
            return True
        return False






class ActionPeek(Action):
    def __init__(self, flag, game, source, target, type):
        super(ActionPeek, self).__init__(flag, game, source, target)

        self.peektype = type
        if self.game.round == 0:
            print("peek flagged as r0")
            self.is_r0_action = True

        self.phase = WolfUtils.GamePhases.INVESTIGATION


    async def resolve_effects(self):
        if self.resolve_valid():
            print("Resolving normal effects")

            if self.peektype == PeekTypes.BINARY:
                print("Initiated binary peektype")

                if self.target.role.alignment == roles.Alignment.VILLAGE or self.target.role.alignment == roles.Alignment.NEUTRAL:
                    result = "Not Guilty"
                    if self.target.role.tinker:
                        result = "Guilty"
                else:
                    result = "Guilty"
                    if self.target.role.tinker:
                        result = "Not Guilty"

                print("Peek returned:" + result)
                await self.source.send_logs("Your investigation finds " + self.target.member.name + " " + result + ".")
            elif self.peektype == PeekTypes.ALIGNMENT:
                if self.target.faction.is_evil and self.target.role.tinker:
                    await self.source.send_logs(
                        "Your investigation finds " + self.target.member.name + " is aligned with the Village Team.")

                elif self.target.role.tinker:
                    evilfaction = None
                    for faction in self.game.factions:
                        if faction.is_evil:
                            evilfaction = faction
                    if evilfaction is not None:
                        await self.source.send_logs(
                            "Your investigation finds " + self.target.member.name + " is aligned with the " + evilfaction.name + ".")
                else:
                    await self.source.send_logs(
                        "Your investigation finds " + self.target.member.name + " is aligned with the " + self.target.faction.name + ".")
            elif self.peektype == PeekTypes.FULL_ROLE:
                await self.source.send_logs(
                    "Your investigation finds " + self.target.member.name + " is a " + self.target.role.name + " aligned with the " + self.target.faction.name + ".")

            return True
        else:
            return False



    # TODO: peektypes.FULL_ROLE
    async def round_zero(self):
        print("r0 peek method resolve called")

        if self.resolve_valid():

            if self.game.r0_peeks == WolfUtils.RoundZeroPeek.FREEWILL:
                return self.resolve_effects()
            elif self.game.r0_peeks == WolfUtils.RoundZeroPeek.R0_NEG_PEEK:



                if self.peektype == PeekTypes.BINARY or self.peektype == PeekTypes.ALIGNMENT:
                    counter = 0
                    r0neg = None
                    while r0neg is None:

                        r = random.randint(0, len(self.game.players)-1)
                        player = self.game.players[r]
                        if not player == self.source:
                            if (not player.role.tinker) and (not player.role.faction.is_evil):
                                r0neg = player
                            elif player.role.tinker and player.role.faction.is_evil:
                                r0neg = player

                        counter += 1
                        if counter > 1000:
                            print(
                                "Something went wrong with r0 peek: " + self.source.name + "targeting " + r0neg.name)
                            return False
                    if self.peektype == PeekTypes.BINARY:
                        await self.source.send_logs(
                            "Your investigation finds " + r0neg.member.name + " Not Guilty.")
                        return True
                    await self.source.send_logs(
                        "Your investigation finds " + r0neg.member.name + " is aligned with the " + r0neg.faction.name + ".")
                    return True

                elif self.peektype == PeekTypes.FULL_ROLE:
                    # TODO: implement this
                    pass

        return False


class ActionKill(Action):
    def __init__(self, flag, game, source, target, killtype, priority, factionbased = False):
        super(ActionKill, self).__init__(flag, game, source, target)

        self.killtype = killtype
        self.priority = priority
        self.factionbased = factionbased
        self.phase = WolfUtils.GamePhases.KILLING


        #R0 Kills are factionbased
        if self.factionbased and self.game.round == 0:
            self.is_r0_action = True


        # Kill priority guidelines:
        # Higher numbers happen first
        # 0 = Default number
        #
        # 20 = Death by poison
        # 25 = Vigilante Nightly Kill
        # 30 = Wolf Factional Kill
        # 40 = Mafia Factional Kill (Mafia usually have a smaller team, so faster kill)
        # 50 = Serial Killer Standard Kill
        # 60 = Vigilante X-Shot Kill
        # 70 = Wolf Extra Kill (Usually Alpha Wolf or similar)
        # 80 = Mafia Extra Kill (Usually Hitman or Similar)
        #

    async def resolve_effects(self):

        if self.resolve_valid():

            await self.game.attempt_kill_player(self.target, self.killtype)

            return True


        else:
            return False




    async def round_zero(self):
        if self.resolve_valid():
            if self.game.r0_kill == WolfUtils.RoundZeroKill.HOST_SAVE:
                await self.game.post_log(self.target.name + " " + self.killtype.tensename)
                await self.game.post_log(self.target.name + " Surivived (Host Save)")



                return True
            elif self.game.r0_kill == WolfUtils.RoundZeroKill.INJURY:
                await self.game.post_log(self.target.name + " " + self.killtype.tensename)
                await self.game.post_log(self.target.name + " Injured")
                self.target.injured = True

                return True
            elif self.game.r0_kill == WolfUtils.RoundZeroKill.MURDER:

                return self.resolve_effects()








        return False


class PeekTypes(Enum):
    BINARY = 1
    ALIGNMENT = 2
    ROLE = 3
    FULL_ROLE = 4


class Killtype(Enum):
    # Standard factional kills
    LYNCH = ("Lynch", "Lynched", True, False)
    SHOT = ("Shot", "Shot", False, False)
    MAUL = ("Maul", "Mauled", False, False)
    STAB = ("Stab", "Stabbed", False, False)
    ASSASSINATE = ("Assassinate", "Assassinated", False, False)
    DRAIN = ("Drain", "Drained", False, False)

    # Rarer killtypes
    POISON = ("Poison", "Poisoned", False, False)

    SUICIDE = ("Suicide", "Took their own life", True, True)
    OVERDOSE = ("Overdose", "Overdosed", True, False)
    BRUTAL = ("Brutal", "Brutal'd", False, False)
    RAVAGE = ("Ravage", "Ravaged", False, False)

    MODKILL = ("Modkill", "Modkilled", True, True)

    def __init__(self, typename, tensename, noprotect, notoughness):
        self.typename = typename
        self.tensename = tensename
        self.ignores_tough = notoughness
        self.ignores_doctor = noprotect
