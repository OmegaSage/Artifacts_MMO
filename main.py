import asyncio
from artifacts import AsyncArtifactsClient
import personal
from activities import gathering, crafting, combat  # etc.


async def main():
    async with AsyncArtifactsClient(token=personal.TOKEN) as client:
        chars = {
            "one":   client.character(personal.CHARACTER_ONE),
            "two":   client.character(personal.CHARACTER_TWO),
            "three": client.character(personal.CHARACTER_THREE),
            "four":  client.character(personal.CHARACTER_FOUR),
            "five":  client.character(personal.CHARACTER_FIVE),
        }

        tasks = [
            # Two gatherers with different resources
            gathering.gather_loop(chars["one"], "ash_wood", target_qty=20),
            gathering.gather_loop(chars["two"], "copper_ore", target_qty=15, resource_x=2, resource_y=0),

            # Crafter
            crafting.craft_loop(
                chars["three"],
                item_code="wooden_staff",
                quantity=1,
                materials=[
                    {"code": "ash_wood", "quantity": 4},
                    # add more materials as needed
                ]
            ),

            # Fighter
            combat.combat_loop(chars["four"], fight_x=0, fight_y=1),
        ]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
