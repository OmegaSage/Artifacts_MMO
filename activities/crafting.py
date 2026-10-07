# activities/crafting.py
import asyncio
from artifacts.models.common import SimpleItemSchema
from artifacts.errors import RetryExhaustedError, ArtifactsAPIError


async def craft_loop(char, item_code: str, quantity: int = 1,
                     workshop_x: int = 2, workshop_y: int = 1,
                     bank_x: int = 4, bank_y: int = 1,
                     materials: list[dict] = None):
    """
    Generic craft loop:
    1. Go to bank and withdraw required materials
    2. Go to workshop and craft
    3. Deposit the finished item
    4. Repeat

    materials example:
    [{"code": "ash_wood", "quantity": 4}, {"code": "copper_ore", "quantity": 2}]
    """
    if materials is None:
        materials = []

    print(f"[{char.name}] Crafting loop for {item_code}")

    while True:
        try:
            # --- 1. Get materials from bank ---
            info = await char.get()
            if info.x != bank_x or info.y != bank_y:
                await char.move(x=bank_x, y=bank_y)

            for mat in materials:
                await char.bank.withdraw_items([
                    SimpleItemSchema(code=mat["code"], quantity=mat["quantity"] * quantity)
                ])
                print(f"[{char.name}] Withdrew {mat['quantity'] * quantity}x {mat['code']}")

            # --- 2. Go craft ---
            if info.x != workshop_x or info.y != workshop_y:
                await char.move(x=workshop_x, y=workshop_y)

            for _ in range(quantity):
                result = await char.skills.craft(code=item_code)
                print(f"[{char.name}] Crafted {item_code} (+{result.details.xp} xp)")

            # --- 3. Deposit finished product ---
            await char.move(x=bank_x, y=bank_y)
            await char.bank.deposit_items([
                SimpleItemSchema(code=item_code, quantity=quantity)
            ])
            print(f"[{char.name}] Deposited {quantity}x {item_code}")

        except (RetryExhaustedError, ConnectionError, TimeoutError, OSError) as e:
            print(f"[{char.name}] Network issue: {e} → retry in 10s")
            await asyncio.sleep(10)
        except ArtifactsAPIError as e:
            print(f"[{char.name}] API error [{e.code}]: {e.message}")
            await asyncio.sleep(20)
        except Exception as e:
            print(f"[{char.name}] Unexpected: {e}")
            await asyncio.sleep(15)
