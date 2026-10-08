import asyncio
from artifacts.models.common import SimpleItemSchema
from artifacts.errors import RetryExhaustedError, ArtifactsAPIError


async def find_closest_resource(client, char, resource_code: str):
    """
    Find the closest map that contains the given resource.
    Returns (x, y)
    """
    info = await char.get()
    maps = await client.maps.get_all(
        content_type="resource",
        content_code=resource_code,
        size=100,
    )

    if not maps.data:
        raise ValueError(f"No maps found containing resource: {resource_code}")

    # Calculate Manhattan distance and pick the closest
    def distance(m):
        return abs(m.x - info.x) + abs(m.y - info.y)

    closest = min(maps.data, key=distance)
    return closest.x, closest.y


async def gather_loop(char, client, item_code: str, resource_code: str = None,
                      target_qty: int = 20, bank_x: int = 4, bank_y: int = 1):
    """
    Continuously gather until target_qty, deposit at bank, repeat.

    item_code     = what appears in inventory (e.g. "ash_wood")
    resource_code = the node on the map (e.g. "ash_tree").
                    If None, assumes it's the same as item_code.
    """
    if resource_code is None:
        resource_code = item_code

    print(f"[{char.name}] Starting to gather {item_code}")

    # Find the best location once at the start
    resource_x, resource_y = await find_closest_resource(client, char, resource_code)
    print(f"[{char.name}] Closest {resource_code} is at ({resource_x}, {resource_y})")

    while True:
        try:
            info = await char.get()
            current = next((i.quantity for i in info.inventory if i.code == item_code), 0)

            if current >= target_qty:
                # Go deposit
                if info.x != bank_x or info.y != bank_y:
                    await char.move(x=bank_x, y=bank_y)

                result = await char.bank.deposit_items([
                    SimpleItemSchema(code=item_code, quantity=current)
                ])
                print(f"[{char.name}] Deposited {current}x {item_code}")
                print(f"[{char.name}] ⏳ Cooldown: {result.cooldown.total_seconds}s")
                continue

            # Need more → go gather
            if info.x != resource_x or info.y != resource_y:
                await char.move(x=resource_x, y=resource_y)

            result = await char.skills.gather()
            gained = ", ".join(f"{d.quantity}x {d.code}" for d in result.details.items)
            print(f"[{char.name}] Gathered {gained} (+{result.details.xp} xp)")
            print(f"[{char.name}] ⏳ Cooldown: {result.cooldown.total_seconds}s")

        except (RetryExhaustedError, ConnectionError, TimeoutError, OSError) as e:
            print(f"[{char.name}] Network issue: {e} → retry in 10s")
            await asyncio.sleep(10)
        except ArtifactsAPIError as e:
            print(f"[{char.name}] API error [{e.code}]: {e.message}")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"[{char.name}] Unexpected: {e}")
            await asyncio.sleep(10)
