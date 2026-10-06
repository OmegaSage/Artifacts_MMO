import asyncio
from artifacts import AsyncArtifactsClient
from personal import CHARACTER_TWO

char = CHARACTER_TWO

async def gathering():
    info = await char.get()
    ashelogs = any(
        item.code == "ash_wood" and item.quantity < 20
        for item in info.inventory
    )

    #if number of logs over above quanity (20) then go to bank and deposit.
    if ashelogs:
        char.move(4,1)
