import asyncio
from artifacts import AsyncArtifactsClient
import personal
from activities import gathering, combat, clean_inventory #, crafting # etc.


async def main():
    async with AsyncArtifactsClient(token=personal.TOKEN) as client:
        chars = {
            "one":   client.character(personal.CHARACTER_ONE),
            "two":   client.character(personal.CHARACTER_TWO),
            "three": client.character(personal.CHARACTER_THREE),
            "four":  client.character(personal.CHARACTER_FOUR),
            "five":  client.character(personal.CHARACTER_FIVE),
        }

        # ============================================
        # Clean inventory at the start of the session
        # ============================================
        print("Cleaning inventories...")
        deposit_all = clean_inventory.deposit_all
        await deposit_all(chars["one"]),
        await deposit_all(chars["two"]),
        #await deposit_all(chars["three"]),
        #await deposit_all(chars["four"]),
        #await deposit_all(chars["five"]),
        print("All characters cleaned.\n")

        # Now start the normal tasks
        tasks = [
            # Two gatherers with different resources
            gathering.gather_loop(chars["two"], "copper_ore", target_qty=20),
            #gathering.gather_loop(chars["two"], "copper_ore", target_qty=15, resource_x=2, resource_y=0),

            # Fighter
            combat.combat_loop(chars["one"], fight_x=1, fight_y=-2),

            # Crafter
            #crafting.craft_loop(
            #    chars["three"],
            #    item_code="wooden_staff",
            #    quantity=1,
            #    materials=[
            #        {"code": "ash_wood", "quantity": 4},
            #        # add more materials as needed
            #    ]
            #),
        ]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
