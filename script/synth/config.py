from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field


class Config(BaseModel):
    """
    Define the configuration contract for every synthetic-data generator.

    Contract:
    - Schema: Every field carries a default, so Config() validates with no arguments.
    - Domain Bounds: Drift rates belong in [0, 1] and per_day_orders_range requires low <= high; the model enforces neither bound.
    - Type Integrity: Pydantic enforces the declared type of every field at construction.
    - Nullability: No field accepts None.
    - Referential Integrity: Every channel in store_channels is assumed present in channel_currency and channel_price_multiplier, and every currency in channel_currency is assumed present in fx_rates; construction validates none of these references.
    - Temporal Alignment: start_date and end_date are inclusive dates; days returns the inclusive day count.
    - Transformation: fx_rates holds the USD value of one unit of each currency, so a USD base price divides by the rate to yield the local amount; channel_price_multiplier applies after that division; default_currency is not consulted by the price path.
    - Lineage: Category vocabulary originates in reference.CATEGORIES_LIST; channel SKU templates, length limits, and title styles originate in reference.CHANNEL_PROFILES.

    Expectations:
    - Determinism: seed fixes the stage and per-entity RNGs; identical field values reproduce identical generator output.
    - Non-Mutation: Generators read Config and never modify it; the Pydantic model itself remains mutable.

    Failures:
    - Crash: Pydantic raises ValidationError when a field violates its declared type.
    - Crash: Listing generation raises KeyError when store_channels or channel_currency references a missing channel or currency key.
    - Finding: Drift rates outside [0, 1] pass construction and saturate the corresponding drift.
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

    # USD per 1 unit of foreign currency
    default_currency: str = "USD"
    fx_rates: dict[str, float] = Field(
        default_factory=lambda: {"USD": 1.0, "EUR": 1.12, "GBP": 1.32}
    )

    channel_currency: dict[str, str] = {
        "amazon": "USD",
        "ebay": "EUR",
        "woocommerce": "GBP",
    }

    # Multiplier on top of FX-converted price
    channel_price_multiplier: dict[str, float] = Field(
        default_factory=lambda: {"amazon": 1.00, "ebay": 0.97, "woocommerce": 0.95}
    )

    sku_null_rate: float = 0.05
    separator_swap_rate: float = 0.15
    drift_channel_prefix_rate: float = 0.10
    drift_lowercase_rate: float = 0.20
    drift_titlecase_rate: float = 0.30
    drift_typo_rate: float = 0.05

    output_dir: Path = Path("data")

    # Inclusive day count and read only attribute
    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    @property
    def n_days(self) -> int:
        return self.days
