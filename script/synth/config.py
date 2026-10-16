from datetime import date
from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    """
    Single source of truth for every parameters the synthetic-data generators need.

    Injected into each generator (e.g. `generate_catalog(cfg, rng)`) so that
    changing one value here re-drives the whole simulation. Generators also
    receive an ``rng`` seeded from ``seed``, which keeps runs reproducible.

    Field groups:
        - Determinism : `seed` - master seed for reproducible output.
        - Time window : `start_date` / `end_date` (both ends inclusive;
          use the `days` property for the inclusive day count).
        - Catalog size: `n_products`, `n_brands`.
        - Demand      : `per_day_orders_range` - (low, high) orders per day.
        - Channels    : `store_channels` - marketplaces being simulated.
        - Money       : `default_currency` (base currency for prices) and
          `fx_rates` (value of 1 unit of each currency in USD).
        - Output      : `output_dir` - where generated artifacts are written.

    Note: Category list is placed in `reference.CATEGORIES_LIST`.

    Read-only helpers:
        - `days`   - inclusive number of days in the time window.
        - `n_days` - alias for `days`.
    """

    seed: int = 42

    # 18 months range
    start_date: date = date(2025, 1, 1)
    end_date: date = date(2026, 7, 1)

    store_channels: list[str] = Field(
        default_factory=lambda: ["amazon", "ebay", "woocommerce"]
    )

    n_products: int = 315
    n_brands: int = 23
    per_day_orders_range: tuple[int, int] = (50, 250)

    # price_usd = amount * fx_rates[currency]
    default_currency: str = "USD"
    fx_rates: dict[str, float] = Field(
        default_factory=lambda: {"USD": 1.0, "EUR": 1.12, "GBP": 1.32}
    )

    channel_currency: dict[str, str] = {
        "amazon": "USD",
        "ebay": "GBP",
        "woocommerce": "USD",
    }

    channel_price: dict[str, float] = {
        "amazon": 1.00,
        "ebay": 1.12,
        "woocommerce": 1.32,
    }

    sku_null_rate: float = 0.05

    output_dir: Path = Path("data")

    # Inclusive day count and read only attribute
    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    @property
    def n_days(self) -> int:
        return self.days
