# activities/gathering.py
import asyncio
from artifacts.models.common import SimpleItemSchema
from artifacts.errors import RetryExhaustedError, ArtifactsAPIError


async def gather_loop(char, item_code: str, target_qty: int = 20,
                      resource_x: int = -1, resource_y: int = 0,
                      bank_x: int = 4, bank_y: int = 1):
    """
    Continuously gather until target_qty, deposit at bank, repeat.
    """
    print(f"[{char.name}] Starting continuous gather of {item_code}")

    while True:
        try:
            info = await char.get()
            current = next((i.quantity for i in info.inventory if i.code == item_code), 0)

            if current >= target_qty:
                # Go deposit
                if info.x != bank_x or info.y != bank_y:
                    await char.move(x=bank_x, y=bank_y)
                await char.bank.deposit_items([SimpleItemSchema(code=item_code, quantity=current)])
                print(f"[{char.name}] Deposited {current}x {item_code}")
                continue

            # Need more → go gather
            if info.x != resource_x or info.y != resource_y:
                await char.move(x=resource_x, y=resource_y)

            result = await char.skills.gather()
            gained = ", ".join(f"{d.quantity}x {d.code}" for d in result.details.items)
            print(f"[{char.name}] Gathered {gained} (+{result.details.xp} xp)")

        except (RetryExhaustedError, ConnectionError, TimeoutError, OSError) as e:
            print(f"[{char.name}] Network issue: {e} → retry in 10s")
            await asyncio.sleep(10)
        except ArtifactsAPIError as e:
            print(f"[{char.name}] API error [{e.code}]: {e.message}")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"[{char.name}] Unexpected: {e}")
            await asyncio.sleep(10)
