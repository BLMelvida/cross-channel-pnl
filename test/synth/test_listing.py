import re
from decimal import Decimal

import pytest

from script.synth.catalog import Catalog, generate_catalog
from script.synth.config import Config
from script.synth.listing import generate_listings
from script.synth.reference import CHANNEL_PROFILES
from script.synth.seeding import stage_rng

MARKETPLACE_PATTERNS = {
    "amazon": re.compile(r"^B0[A-Z0-9]{8}$"),
    "ebay": re.compile(r"^[1-9]\d{11}$"),
    "woocommerce": re.compile(r"^\d+$"),
}


@pytest.fixture(scope="module")
def built() -> tuple[Config, Catalog, list]:
    cfg = Config()
    catalog = generate_catalog(cfg, stage_rng(cfg.seed, "catalog"))
    listings = generate_listings(cfg, catalog, stage_rng(cfg.seed, "listings"))
    return cfg, catalog, listings


def test_same_seed_same_output(built):
    cfg, catalog, listings = built
    re_run = generate_listings(cfg, catalog, stage_rng(cfg.seed, "listings"))
    assert re_run == listings


def test_expected_row_count(built):
    cfg, catalog, listings = built
    assert len(listings) == len(catalog.products) * len(cfg.store_channels)


def test_one_listing_per_product_channel(built):
    cfg, catalog, listings = built
    expected = {(p.id, ch) for p in catalog.products for ch in cfg.store_channels}
    actual = {(listing.product_id, listing.channel) for listing in listings}
    assert actual == expected
    assert len(actual) == len(listings)


def test_product_ids_exist(built):
    _, catalog, listings = built
    product_ids = {p.id for p in catalog.products}
    assert all(listing.product_id in product_ids for listing in listings)


def test_marketplace_id_format(built):
    _, _, listings = built
    for listing in listings:
        pattern = MARKETPLACE_PATTERNS[listing.channel]
        assert pattern.match(listing.marketplace_id), (
            listing.channel,
            listing.marketplace_id,
        )


def test_marketplace_id_unique(built):
    _, _, listings = built
    ids = [listing.marketplace_id for listing in listings]
    assert len(set(ids)) == len(ids)


def test_seller_sku_length(built):
    _, _, listings = built
    for listing in listings:
        if listing.seller_sku is None:
            continue
        max_len = CHANNEL_PROFILES[listing.channel]["sku_max_len"]
        assert len(listing.seller_sku) <= max_len


def test_price_is_decimal_positive_2dp(built):
    _, _, listings = built
    for listing in listings:
        assert isinstance(listing.price, Decimal)
        assert listing.price > 0
        assert listing.price.as_tuple().exponent == -2


def test_currency_in_fx_rates(built):
    cfg, _, listings = built
    assert all(listing.currency in cfg.fx_rates for listing in listings)
    assert {listing.currency for listing in listings} == set(
        cfg.channel_currency.values()
    )


def test_bulk_smoke():
    cfg = Config(n_products=300)
    catalog = generate_catalog(cfg, stage_rng(cfg.seed, "catalog"))
    listings = generate_listings(cfg, catalog, stage_rng(cfg.seed, "listings"))
    assert len(listings) == cfg.n_products * len(cfg.store_channels)
