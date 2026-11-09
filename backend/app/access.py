LEVELS = ("public", "internal", "confidential", "secret")
RANK = {name: i for i, name in enumerate(LEVELS)}


def can_read(clearance: str, classification: str) -> bool:
    return RANK[clearance] >= RANK[classification]
