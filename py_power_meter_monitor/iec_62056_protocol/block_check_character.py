def get_block_check_character(data: bytes) -> bytes:
    block_check_character = 0

    for byte in data:
        block_check_character ^= byte

    return block_check_character.to_bytes(1, "big")
