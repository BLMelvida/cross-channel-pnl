import random
import string
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel

from .catalog import Brand, Catalog, Category, Product
from .config import Config
from .reference import CATEGORIES_LIST, CHANNEL_PROFILES

# mimic amazon standard identificaiton format
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
    # 'B0' + 8 characters mix upper case alphabet-number
    return "B0" + "".join(rng.choice(_ASIN_ALPHABET) for _ in range(8))


def _ebay_item_id(rng: random.Random) -> str:
    # 12 digits no leading zeroes (starts with 1-9)
    rand_id = rng.randint(10**11, 10**12 - 1)
    return str(rand_id)


def _woo_product_id(rng: random.Random) -> str:
    # starts with 1 up to 1 billion
    return str(rng.randint(1, 10**9))


# ------------------------------------------------------------
# SELLER DEFINED SKUs
# ------------------------------------------------------------


def _format(value: str) -> str:
    # Format values like 'ABCD, 123_EFG!' to 'ABCD-123-EFG'
    cleaned = "".join(val if val.isalnum() else " " for val in value)
    return "-".join(cleaned.split()).upper()


def _sku_fields(product: Product, brand: Brand, category: Category) -> dict[str, str]:
    """
    Transform a product into the SKU field mapping used by channel templates.

    Contract:
    - Domain Bounds: item is one of CATEGORIES_LIST[category.name]["items"].
    - Transformation: product.name splits as brand, modifier, item, and trailing code; brand, category, and item normalize through _format.

    Expectations:
    - Determinism: The same product, brand, and category produce identical fields.
    - Non-Mutation: product, brand, and category are never modified.

    Outputs:
    - Shape: A mapping with exactly brand, category, item, and code.

    Failures:
    - Crash: category.name is absent from CATEGORIES_LIST.
    - Crash: No category item matches product.name.
    """
    category_items = CATEGORIES_LIST[category.name]["items"]

    item = next((itm for itm in category_items if itm in product.name), None)
    if item is None:
        raise ValueError(f"No known item matched {product.name}")

    prod_code = product.name.rsplit(" ", 1)[-1]
    return {
        "brand": _format(brand.name),
        "category": _format(category.name),
        "item": _format(item),
        "code": prod_code,
    }


def _render_seller_sku(
    channel: str, fields: dict[str, str], cfg: Config, rng: random.Random
) -> str | None:
    """
    Transform SKU fields into a channel-formatted, drifted seller SKU.

    Contract:
    - Nullability: seller_sku is None when the null draw falls below cfg.sku_null_rate.
    - Domain Bounds: A non-null SKU renders from the channel sku_template and is at most sku_max_len characters.
    - Transformation: Separator swap, channel prefix, casing, and adjacent-character typo drift apply independently before truncation.
    - Type Integrity: The result is str or None.

    Expectations:
    - Determinism: The same fields, cfg, and rng state produce the same seller_sku.
    - Non-Mutation: fields and cfg are never modified.

    Outputs:
    - Shape: A string within the channel sku_max_len, with no trailing separator, or None.

    Failures:
    - Crash: channel is absent from CHANNEL_PROFILES.
    - Crash: A sku_template placeholder is absent from fields.
    """

    if rng.random() < cfg.sku_null_rate:
        return None

    ch_profile = CHANNEL_PROFILES[channel]
    sku = ch_profile["sku_template"].format(**fields)

    # Injecting data chaos: missing sku, seprator swap, data drifts
    if rng.random() < cfg.separator_swap_rate:
        sku = sku.replace("-", "_")

    if rng.random() < cfg.drift_channel_prefix_rate:
        sku = f"{channel[:3].upper()}_{sku}"

    roll = rng.random()
    if roll < cfg.drift_lowercase_rate:
        sku = sku.lower()
    elif roll < cfg.drift_titlecase_rate:
        sku = sku.title()

    if rng.random() < cfg.drift_typo_rate and len(sku) > 4:
        idx = rng.randrange(len(sku) - 1)
        # skip identical adjacent characters
        if sku[idx] != sku[idx + 1]:
            sku = sku[:idx] + sku[idx + 1] + sku[idx] + sku[idx + 2 :]

    # Strip dangling separator
    sku = sku[: ch_profile["sku_max_len"]].rstrip("-_")

    return sku


# ------------------------------------------------------------
# CHANNEL DRIFTS (PRICING AND TITLE)
# ------------------------------------------------------------


def _channel_price(
    base_price: Decimal, channel: str, cfg: Config, rng: random.Random
) -> Decimal:
    """
    Transform a USD base price into a channel-currency repriced amount.

    Contract:
    - Transformation: base_price divides by fx_rates[channel_currency[channel]], then multiplies by channel_price_multiplier[channel] and an integer-basis-point fluctuation in [-200, 200].
    - Type Integrity: The result is a Decimal quantized to two decimal places.
    - Domain Bounds: base_price, fx_rate, and multiplier are positive; this function does not validate them.
    - Nullability: The result is never None.

    Expectations:
    - Determinism: The same base_price, channel, cfg, and rng state produce the same Decimal.
    - Non-Mutation: base_price and cfg are never modified.

    Outputs:
    - Shape: A Decimal with exponent -2.

    Failures:
    - Crash: channel is absent from channel_currency, fx_rates, or channel_price_multiplier.
    """
    currency = cfg.channel_currency[channel]
    fx_rate = Decimal(str(cfg.fx_rates[currency]))  # USD per 1 unit of foreign currency
    multiplier = Decimal(str(cfg.channel_price_multiplier[channel]))
    foreign_price = base_price / fx_rate  # USD to foreign price

    # (10000 + fluctuation)/10000 converts to scale: +/-200 -> 1.02/0.98 or +/-2%.
    fluctuation = Decimal(10000 + rng.randint(-200, 200)) / Decimal(10000)
    price = foreign_price * multiplier * fluctuation
    return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


_AMAZON_KEYWORDS = ["Fast Shipping", "Premium Quality", "Easy to Use", "Gift Ready"]


def _truncate_words(text, limit) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" ,-|")


def _channel_title(
    channel: str, product: Product, category: str, rng: random.Random
) -> str:
    """
    Transform a product into a channel-specific product title.

    Contract:
    - Domain Bounds: The result length never exceeds the channel title_max_len.
    - Transformation: amazon appends sampled keywords and two category modifiers; ebay optionally prefixes NEW and uppercases; woocommerce returns product.name.
    - Nullability: The result is never None.

    Expectations:
    - Determinism: The same product, channel, and rng state produce the same title.
    - Non-Mutation: product and category are never modified.

    Outputs:
    - Shape: A string truncated at a word boundary.

    Failures:
    - Crash: channel is absent from CHANNEL_PROFILES.
    - Crash: category is absent from CATEGORIES_LIST.
    """
    ch_profile = CHANNEL_PROFILES[channel]
    ch_mods = CATEGORIES_LIST[category]["modifiers"]
    style = ch_profile["title_style"]
    max_len = ch_profile["title_max_len"]
    base = product.name

    if style == "amazon":
        extras = rng.sample(_AMAZON_KEYWORDS, k=rng.randint(2, 3))
        mods = rng.sample(ch_mods, k=2)
        title = f"{base} - {' '.join(extras)}| {mods[0]} | {mods[1]}"

    elif style == "ebay":
        prefix = "NEW " if rng.random() < 0.3 else ""
        title = f"{prefix}{base.upper()}"
    else:
        title = base

    return _truncate_words(title, max_len)


# ------------------------------------------------------------
# GENERATE LISTING
# ------------------------------------------------------------


def generate_listings(
    cfg: Config, catalog: Catalog, rng: random.Random
) -> list[Listing]:
    """
    Coordinate listing generation across every product and channel.

    Workflow:
    1. Initialize: Create the listing accumulator, the marketplace-id uniqueness set, and the sequence counter.
    2. Hydrate: Resolve the brand and category for each product.
    3. Transform: Resolve SKU fields per product; per channel, delegate to the marketplace-id helpers, _render_seller_sku, _channel_title, and _channel_price.
    4. Validate: Enforce marketplace_id uniqueness across all listings before append.

    Expectations:
    - Determinism: The same cfg and catalog produce identical Listing rows in identical order.
    - Non-Mutation: catalog is never modified.
    - Grain: Exactly one Listing per product_id and channel.
    - Lineage: Every Listing carries product_id as the ground-truth link to the catalog product.

    Outputs:
    - Shape: A list of Listing models ordered by catalog product order, then configured channel order.

    Failures:
    - Crash: A marketplace_id repeats across listings.
    - Crash: A product has no matching category item.
    """

    seen_marketplace_ids: set[str] = set()
    listings: list[Listing] = []
    sequence = 0

    for p_idx, product in enumerate(catalog.products, 1):
        brand = next(b for b in catalog.brands if b.id == product.brand_id)
        category = next(c for c in catalog.categories if c.id == product.category_id)
        fields = _sku_fields(product, brand, category)

        for channel in cfg.store_channels:
            # Per-entity randomization
            rng_e = random.Random(f"{cfg.seed}:listing:{p_idx}:{channel}")
            ch_currency = cfg.channel_currency[channel]
            sequence += 1

            if channel == "amazon":
                marketplace_id = _amazon_asin(rng_e)
            elif channel == "ebay":
                marketplace_id = _ebay_item_id(rng_e)
            else:
                marketplace_id = _woo_product_id(rng_e)

            if marketplace_id in seen_marketplace_ids:
                raise ValueError(f"duplicate marketplace_id {marketplace_id}")

            seen_marketplace_ids.add(marketplace_id)

            seller_sku = _render_seller_sku(channel, fields, cfg=cfg, rng=rng_e)
            ch_title = _channel_title(
                channel, product, category=category.name, rng=rng_e
            )
            ch_price = _channel_price(
                product.base_price, channel=channel, cfg=cfg, rng=rng_e
            )

            listings.append(
                Listing(
                    listing_id=f"lst_{sequence:05d}",
                    channel=channel,
                    product_id=product.id,
                    marketplace_id=marketplace_id,
                    seller_sku=seller_sku,
                    title=ch_title,
                    price=ch_price,
                    currency=ch_currency,
                )
            )

    return listings
