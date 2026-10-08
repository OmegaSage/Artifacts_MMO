import asyncio
from artifacts.errors import RetryExhaustedError, ArtifactsAPIError


# Define the healing items you want to consider, in priority order
HEAL_PRIORITY = ["healing_potion", "apple", "cooked_chicken"]  # add more as needed

# Cache so we don't fetch item data every loop
_heal_cache = {}

async def get_heal_amount(client, code: str) -> int:
    if code not in _heal_cache:
        item = await client.items.get(code)
        heal_value = 0
        for effect in item.effects:
            # Works with both possible attribute names
            if getattr(effect, "code", None) == "heal" or getattr(effect, "name", "").lower() == "heal":
                heal_value = effect.value
                break
        _heal_cache[code] = heal_value
    return _heal_cache[code]


async def try_heal(char, client, heal_threshold: int) -> bool:
    """
    Try to heal using available items.
    Returns True if we used something, False if we should rest instead.
    """
    info = await char.get()
    missing_hp = heal_threshold - info.hp

    if missing_hp <= 0:
        return False  # already healthy

    # Build a quick lookup of what we have
    inventory = {item.code: item.quantity for item in info.inventory if item.quantity > 0}

    for code in HEAL_PRIORITY:
        qty = inventory.get(code, 0)
        if qty == 0:
            continue

        heal_per_item = await get_heal_amount(client, code)
        if heal_per_item <= 0:
            continue

        # How many do we need?
        needed = (missing_hp + heal_per_item - 1) // heal_per_item  # round up
        use_qty = min(needed, qty)

        # Only use it if it actually helps us reach the threshold
        if info.hp + (use_qty * heal_per_item) >= heal_threshold:
            await char.inventory.use(code=code, quantity=use_qty)
            print(f"[{char.name}] Using {use_qty}x {code} (heals {heal_per_item} each)")
            await asyncio.sleep(0.1)
            return True

    # Nothing useful found
    return False


async def combat_loop(char, client, fight_x: int = 0, fight_y: int = 1, heal_threshold: int = 90):
    """
    Fight on a specific tile. Different characters can have different locations.
    """
    print(f"[{char.name}] Fighting at ({fight_x}, {fight_y})!")

    while True:
        try:
            info = await char.get()

            # Move to fight tile if needed
            if info.x != fight_x or info.y != fight_y:
                await char.move(x=fight_x, y=fight_y)

            # Healing loop
            while True:
                info = await char.get()
                if info.hp >= heal_threshold:
                    break

                used_item = await try_heal(char, client, heal_threshold)

                print(f'[{char.name}]Attempting to heal...')

                if not used_item:
                    result = await char.rest()
                    print(f"[{char.name}] Resting for {result.cooldown.total_seconds}s...")
                    await asyncio.sleep(0.1)

            #fight only after healing loop is done
            result = await char.fight()
            fight = result.fight
            my_stats = fight.characters[0]
            cd = result.cooldown

            # Result line
            status = "🏆 Fight won!" if fight.result.value == "win" else "💀 Fight lost!"
            print(f"[{char.name}] {status} | XP: {my_stats.xp} | HP: {my_stats.final_hp}/{info.max_hp} | CD: {cd.total_seconds}s")

            # Loot + gold (only if something dropped)
            loot_parts = []
            if my_stats.drops:
                drops_str = ", ".join(f"{d.quantity}x {d.code}" for d in my_stats.drops)
                loot_parts.append(drops_str)
            if my_stats.gold:
                loot_parts.append(f"{my_stats.gold} gold")

            if loot_parts:
                print(f"[{char.name}] 🎁 {', '.join(loot_parts)}")
            await asyncio.sleep(0.1)



        except (RetryExhaustedError, ConnectionError, TimeoutError, OSError) as e:
            print(f"[{char.name}] Network error: {e}. Retrying in 10s...")
            await asyncio.sleep(10)
        except ArtifactsAPIError as e:
            print(f"[{char.name}] API error [{e.code}]: {e.message}. Waiting 20s...")
            await asyncio.sleep(20)
        except Exception as e:
            print(f"[{char.name}] Unexpected error: {e}. Waiting 15s...")
            await asyncio.sleep(15)
