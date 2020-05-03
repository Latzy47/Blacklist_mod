

@run_before1(PlayerAvatar, 'onBattleEvents')
def before(self, events):
    pass # do stuff1


@run_before1(PlayerAvatar, 'onBattleEvents')
def before(self, events):
    pass # do stuff2


arena = getattr(BigWorld.player(), 'arena', None)
            if arena is not None:
                avatar = PlayerAvatar()
                avatar.onBattleEvents()