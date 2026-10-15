from script.synth.config import Config
from script.synth.catalog import generate_catalog
from script.synth.seeding import stage_rng


def test_same_seed_same_output():
    a = generate_catalog(Config(), stage_rng(42, "catalog"))
    b = generate_catalog(Config(), stage_rng(42, "catalog"))
    assert a == b


def test_adding_products_does_not_shift_existing():
    a = generate_catalog(Config(n_products=50), stage_rng(42, "catalog"))
    b = generate_catalog(Config(n_products=100), stage_rng(42, "catalog"))
    assert a.products == b.products[:50]


def test_all_prices_are_above_cost():
    cfg = Config(n_products=100)
    catalog = generate_catalog(cfg, stage_rng(42, "catalog"))

    for product in catalog.products:
        assert product.base_price > product.base_cost
