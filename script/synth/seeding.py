import hashlib
import random
from faker import Faker


def _stage_int(seed: int, stage: str) -> int:
    """
    Derive a stable integer seed from a (seed, stage) pair.

    Uses hashlib rather than builtin `hash()`: `hash()` is salted per
    process (PYTHONHASHSEED), so it is not stable across runs.
    """
    digest = hashlib.sha256(f"{seed}:{stage}".encode()).digest()
    return int.from_bytes(digest[:8], "little")


def stage_faker(seed: int, stage: str) -> Faker:
    """
    Return a Faker instance seeded deterministically for `stage`.

    Faker keeps its own internal RNG, so `random.Random` does not control
    it; seeding here is what makes Faker output reproducible.
    """
    f = Faker()
    Faker.seed(_stage_int(seed, stage))
    return f


def stage_rng(seed: int, stage: str) -> random.Random:
    """
    Return a `random.Random` seeded deterministically for `stage`.

    Use one distinct `stage` name per generation step (e.g. "catalog") so
    that changing one stage does not disturb the random stream of another.
    """
    return random.Random(f"{seed}:{stage}")
