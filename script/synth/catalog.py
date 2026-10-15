import random
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pydantic import BaseModel
from .config import Config
from .reference import BRAND_NAMES, CATEGORIES_LIST


class Brand(BaseModel):
    id: str
    name: str


class Category(BaseModel):
    id: str
    name: str


class Product(BaseModel):
    id: str
    name: str
    brand_id: str
    category_id: str
    base_cost: Decimal  # supplier unit cost
    base_price: Decimal  # MSRP before channel adjustments


@dataclass
class Catalog:
    """
    Plain container for the generated reference data.
    """

    brands: list[Brand]
    categories: list[Category]
    products: list[Product]


def _make_id(prefix: str, i: int) -> str:
    return f"{prefix}_{i:05d}"


def generate_catalog(cfg: Config, rng: random.Random) -> Catalog:
    """
    Generate brands, categories and products for the simulated catalog.
    """
    brands = [
        Brand(id=_make_id("br", i), name=name)
        for i, name in enumerate(
            rng.sample(BRAND_NAMES, k=min(cfg.n_brands, len(BRAND_NAMES))), 1
        )
    ]

    categories = [
        Category(id=_make_id("categ", idx), name=name)
        for idx, name in enumerate(CATEGORIES_LIST.keys(), 1)
    ]

    products: list[Product] = []
    for idx in range(1, cfg.n_products + 1):
        brand = rng.choice(brands)
        category = rng.choice(categories)

        preset = CATEGORIES_LIST[category.name]
        mod = rng.choice(preset["modifiers"])
        item = rng.choice(preset["items"])

        # Integer cents to stay exact: (300 - 8000)/100 -> 3.00 - 80.00 USD.
        cost = Decimal(rng.randint(300, 8000)) / 100

        # Initial margin covers marketplace fees, ads, and refunds.
        # Retail price = 1.8x to 2.5x the supplier cost (80% - 150% markup).
        markup_pct = Decimal(rng.randint(80, 150)) / 100
        price = (cost * (1 + markup_pct)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        assert price > cost, "product priced below cost"

        products.append(
            Product(
                id=_make_id("prod", idx),
                name=f"{brand.name} {mod} {item} {idx:04d}",
                brand_id=brand.id,
                category_id=category.id,
                base_cost=cost,
                base_price=price,
            )
        )

    return Catalog(brands=brands, categories=categories, products=products)
