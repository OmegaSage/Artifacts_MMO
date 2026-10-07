from artifacts.models.common import SimpleItemSchema

async def deposit_all(char, keep: list[str] | None = None):
    """
    Deposit everything in the character's inventory to the bank,
    except items listed in `keep`.
    """
    if keep is None:
        keep = []          # e.g. ["healing_potion", "cooked_chicken"]

    info = await char.get()

    items_to_deposit = [
        SimpleItemSchema(code=item.code, quantity=item.quantity)
        for item in info.inventory
        if item.code not in keep and item.quantity > 0
    ]

    if not items_to_deposit:
        print(f"[{char.name}] Nothing to deposit")
        return

    # Make sure we're at the bank
    if info.x != 4 or info.y != 1:          # adjust bank coordinates if needed
        await char.move(x=4, y=1)

    await char.bank.deposit_items(items_to_deposit)
    print(f"[{char.name}] Deposited {len(items_to_deposit)} stacks")
