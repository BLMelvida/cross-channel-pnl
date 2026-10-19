import random
import string
from decimal import Decimal, ROUND_HALF_UP
from turtle import st
from pydantic import BaseModel
from .reference import CHANNEL_PROFILES, CATEGORIES_LIST
from .catalog import Brand, Category, Product, generate_catalog
from .config import Config

_ASIN_ALPHABET = string.ascii_uppercase + string.digits


class Listing(BaseModel):
    listing_id: str
    channel: str
    product_id: str
    marketplace_id: str
    seller_sku: str | None
    title: str
    price: Decimal
    currency: str


# ------------------------------------------------------------
# CHANNEL MARKETPLACE IDs
# ------------------------------------------------------------


def _amazon_asin(rng: random.Random) -> str:
    # B0 +ASIN (10chars) + 8 characters mix upper case alphabet-number
    return "B0" + "".join(rng.choice(_ASIN_ALPHABET) for _ in range(8))


def _ebay_item_id(rng: random.Random) -> str:
    # 12 digits no leading zeroes (starts with 1-9)
    rand_id = rng.randint(10**11, 10**12 - 1)
    return str(rand_id)


def _woo_product_id(rng: random.Random) -> str:
    # starts with 1 up to 1 million
    return str(rng.randint(1, 10**6))


# ------------------------------------------------------------
# SELLER DEFINED SKUs
# ------------------------------------------------------------


def _base_sku(product: Product, brand: Brand) -> str:

    # Create original seller SKU before platform specific formatting
    no_brand = product.name[len(brand.name) :].strip()
    concat_words = "-".join(word.upper() for word in no_brand)
    return f"{brand.name.upper()}-{concat_words}"

    ...


def _render_seller_sku(
    channel: str, base: str, cfg: Config, rng: random.Random
) -> str | None:

    # TODO:
    # 1) missing SKU: if rng.random() < cfg.sku_null_rate: return None
    # 2) template from CHANNEL_PROFILES[channel]  (e.g. '{BRAND}-{ITEM}-{CODE}')
    # 3) drift: casing, '-' vs '_', channel prefix, truncate to channel max len, w/ occasional typo.
    ...
