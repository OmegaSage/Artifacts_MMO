import asyncio
from artifacts.errors import RetryExhaustedError, ArtifactsAPIError


async def combat_loop(char, fight_x: int = 0, fight_y: int = 1, heal_threshold: int = 30):
    """
    Fight on a specific tile. Different characters can have different locations.
    """
    print(f"[{char.name}] Combat loop on ({fight_x}, {fight_y})")

    while True:
        try:
            info = await char.get()
            print(f"[{char.name}] HP: {info.hp}/{info.max_hp}")

            # Move to fight tile if needed
            if info.x != fight_x or info.y != fight_y:
                await char.move(x=fight_x, y=fight_y)

            # Heal
            if info.hp < heal_threshold:
                has_potion = any(i.code == "healing_potion" and i.quantity > 0 for i in info.inventory)
                if has_potion:
                    await char.inventory.use(code="healing_potion", quantity=1)
                else:
                    await char.rest()
                    await asyncio.sleep(0.1)

            result = await char.fight()
            if result.fight.result.value == "lose":
                print(f"[{char.name}] Died!")
                # Optional: break or continue after respawn
                await asyncio.sleep(5)

        except (RetryExhaustedError, ConnectionError, TimeoutError, OSError) as e:
            print(f"[{char.name}] Network error: {e}. Retrying in 10s...")
            await asyncio.sleep(10)
        except ArtifactsAPIError as e:
            print(f"[{char.name}] API error [{e.code}]: {e.message}. Waiting 20s...")
            await asyncio.sleep(20)
        except Exception as e:
            print(f"[{char.name}] Unexpected error: {e}. Waiting 15s...")
            await asyncio.sleep(15)