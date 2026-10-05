import asyncio
from artifacts import AsyncArtifactsClient
import personal

async def main():
    async with AsyncArtifactsClient(token=personal.TOKEN) as client:
        char = client.character(personal.CHARACTER_ONE)
        char2 = client.character(personal.CHARACTER_TWO)
        char3 = client.character(personal.CHARACTER_THREE)
        char4 = client.character(personal.CHARACTER_FOUR)
        char5 = client.character(personal.CHARACTER_FIVE)

        while True:
            # Get fresh character info
            info = await char.get()
            print(f"HP: {info.hp}/{info.max_hp}")

            # Heal if HP is low
            if info.hp < 30:
                has_potion = any(
                    item.code == "healing_potion" and item.quantity > 0
                    for item in info.inventory
                )

                if has_potion:
                    print("Using healing potion...")
                    await char.inventory.use(code="healing_potion", quantity=1)
                else:
                    print("No potion left – resting instead")
                    await char.rest()

            # Fight
            result = await char.fight()
            if result.fight.result.value == "lose":
                print("Died! Stopping.")
                break

            # Optional: small delay or other async work
            # await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
