import asyncio
from artifacts import AsyncArtifactsClient
from artifacts.models.common import SimpleItemSchema
from personal import CHARACTER_TWO

char = CHARACTER_TWO

async def gathering():
    #setting up for variable gathering depending on goals
    gameitem = "ash_wood"
    gathering = 5

    info = await char.get()

    items = [SimpleItemSchema(code=gameitem, quantity = gathering)]

    goal = (
        item.code == gameitem and item.quantity >= gathering
        for item in info.inventory
    )
    #if number of logs over above quanity (20) then go to bank and deposit.
    if goal:
        char.move(x=4,y=1)
        char.bank.deposit_items(items)
        print(f'Depositing {gathering} {gameitem}.')

    char.move(x=-1, y=0)
    while not goal:
        result = char.skills.gather()
        print(f"+{result.details.xp}xp, got: {[d.code for d in result.details.items]}")
        if items:
            break
