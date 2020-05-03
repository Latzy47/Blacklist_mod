

@run_before(PlayerAvatar, 'onBattleEvents')
def before1(self, events):
    pass # do stuff1


@run_before(PlayerAvatar, 'onBattleEvents')
def before2(self, events):
    pass # do stuff2


arena = getattr(BigWorld.player(), 'arena', None)
            if arena is not None:
                avatar = PlayerAvatar()
                avatar.onBattleEvents()