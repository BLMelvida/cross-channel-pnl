import random
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel
from dataclasses import dataclass
from synth.config import Config


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
    docstring ...
    """

    brands: list[Brand]
    categories: list[Category]
    products: list[Product]


_BRAND_NAMES = [""]
_CATEGORY_NAMES = [""]
_PRODUCT_ADJ = [""]
_PRODUCT_NOUN = [""]


def _make_id(prefix: str, i: int) -> str:
    return f"{prefix}_{i:05d}"


def generate_catalog(cfg: Config, rng: random.Random) -> Catalog:
    """
    docstring...
    """
    brands = [
        Brand(id=_make_id("br", i), name=f"{name} Inc.")
        for i, name in enumerate(
            rng.sample(_BRAND_NAMES, k=min(cfg.n_brands, len(_BRAND_NAMES))), 1
        )
    ]
    categories = [
        Category(id=_make_id("cat", i), name=name)
        for i, name in enumerate(
            rng.sample(_CATEGORY_NAMES, k=min(cfg.n_categories, len(_CATEGORY_NAMES))),
            1,
        )
    ]

    products: list[Product] = []
    for idx in range(1, cfg.n_products + 1):
        brand = rng.choice(brands)
        category = rng.choice(categories)
        adj = rng.choice(_PRODUCT_ADJ)
        noun = rng.choice(_PRODUCT_NOUN)

        # cost range 3.00 - 80.00
        cost = Decimal(rng.randint(300, 8000)) / 100
        # markup price pct range 5% - 20%
        markup = Decimal(rng.randint(50, 200)) / 100
        # Cap to 2 decimal places with round up
        price = (cost * markup).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        products.append(
            Product(
                id=_make_id("prod", idx),
                name=f"{brand.name} {adj} {noun}",
                brand_id=brand.id,
                category_id=category.id,
                base_cost=cost,
                base_price=price,
            )
        )

    return Catalog(brands=brands, categories=categories, products=products)
