from artifacts.models.common import SimpleItemSchema

async def deposit_all(char, client, keep: list[str] | None = None):
    """
    Deposit everything in the character's inventory to the bank,
    except items listed in `keep`.
    Withdraw items in 'keep' from bank
    """
    if keep is None:
        keep = []          # e.g. ["healing_potion", "cooked_chicken"]

    # --- Character Inventory ---
    info = await char.get()

    items_to_deposit = [
        SimpleItemSchema(code=item.code, quantity=item.quantity)
        for item in info.inventory
        if item.code not in keep and item.quantity > 0
    ]

    # --- Bank Inventory ---
    bank = await client.my_account.get_bank_items()
    bank_dict = {item.code: item.quantity for item in bank.data}

    items_to_withdraw = []
    for code in keep:
        if code in bank_dict and bank_dict[code] > 0:
            items_to_withdraw.append(
                SimpleItemSchema(code=code, quantity=bank_dict[code])
            )

    # Nothing to do at all?
    if not items_to_deposit and not items_to_withdraw:
        print(f"[{char.name}] Nothing to deposit or withdraw")
        return

    # We have work → go to bank if needed
    if info.x != 4 or info.y != 1:
        print(f"[{char.name}] Moving to the Bank...")
        await char.move(x=4, y=1)

    # Deposit junk
    if items_to_deposit:
        await char.bank.deposit_items(items_to_deposit)
        print(f"[{char.name}] Deposited {len(items_to_deposit)} stacks")

    # Withdraw important items
    if items_to_withdraw:
        await char.bank.withdraw_items(items_to_withdraw)
        print(f"[{char.name}] Withdrew {len(items_to_withdraw)} important stacks")
