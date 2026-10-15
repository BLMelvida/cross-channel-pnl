BRAND_NAMES: list[str] = [
    "Aurora",
    "Nordvik",
    "Lumen",
    "Vireo",
    "Cascade",
    "Kestrel",
    "Atlas",
    "Marlow",
    "Pinnacle",
    "Everline",
    "Novabright",
    "Halcyon",
    "Ridgeway",
    "Zephyr",
    "Copperleaf",
    "Brightloom",
    "Windmere",
    "Bastion",
    "Kodama",
    "Ferro",
    "Solstice",
    "Quillstone",
    "Amberfield",
    "Northgate",
]

CATEGORIES_LIST: dict[str, dict[str, list[str]]] = {
    "Electronics": {
        "items": [
            "Wireless Earbuds",
            "Bluetooth Speaker",
            "Power Bank",
            "USB-C Hub",
            "Smart Plug",
        ],
        "modifiers": ["Compact", "Rechargeable", "Noise-Cancelling", "Portable"],
    },
    "Home & Kitchen": {
        "items": [
            "Air Fryer",
            "Ceramic Mug Set",
            "Electric Kettle",
            "Storage Bin",
            "Chef Knife",
        ],
        "modifiers": ["Stainless Steel", "Non-Stick", "Stackable", "Insulated"],
    },
    "Sports & Outdoors": {
        "items": [
            "Yoga Mat",
            "Resistance Bands",
            "Camping Lantern",
            "Hiking Backpack",
            "Water Bottle",
        ],
        "modifiers": ["Non-Slip", "Waterproof", "Lightweight", "Foldable"],
    },
    "Pet Supplies": {
        "items": [
            "Dog Harness",
            "Cat Scratching Post",
            "Slow Feeder Bowl",
            "Pet Carrier",
            "Grooming Kit",
        ],
        "modifiers": ["Adjustable", "Durable", "Washable", "Reflective"],
    },
    "Beauty & Personal Care": {
        "items": [
            "Facial Cleanser",
            "Hair Dryer",
            "Beard Trimmer",
            "Body Lotion",
            "Makeup Brush Set",
        ],
        "modifiers": ["Hydrating", "Cordless", "Travel-Size", "Gentle"],
    },
    "Toys & Games": {
        "items": [
            "Building Blocks Set",
            "Wooden Puzzle",
            "RC Car",
            "Board Game",
            "STEM Kit",
        ],
        "modifiers": ["Educational", "Colorful", "Interactive"],
    },
    "Office Products": {
        "items": [
            "Desk Organizer",
            "Wireless Mouse",
            "Monitor Stand",
            "Label Maker",
            "Notebook Set",
        ],
        "modifiers": ["Ergonomic", "Recycled", "Adjustable", "Heavy-Duty"],
    },
    "Tools & Home Improvement": {
        "items": [
            "Cordless Drill",
            "Screwdriver Set",
            "Tape Measure",
            "Tool Bag",
            "Wrench Set",
        ],
        "modifiers": ["Heavy-Duty", "Precision", "Cordless", "Compact"],
    },
    "Baby": {
        "items": [
            "Baby Monitor",
            "Stroller Organizer",
            "Silicone Bib",
            "Bottle Warmer",
            "Diaper Bag",
        ],
        "modifiers": ["BPA-Free", "Portable", "Soft-Touch", "Adjustable"],
    },
    "Apparel & Accessories": {
        "items": [
            "Cotton T-Shirt",
            "Canvas Backpack",
            "Wool Beanie",
            "Rain Jacket",
            "Running Socks",
        ],
        "modifiers": ["Breathable", "Reversible", "Water-Resistant", "Unisex"],
    },
    "Health & Household": {
        "items": [
            "Air Purifier",
            "Humidifier",
            "First Aid Kit",
            "Electric Toothbrush",
            "Laundry Detergent",
        ],
        "modifiers": ["Hypoallergenic", "Concentrated", "Rechargeable", "Compact"],
    },
    "Automotive": {
        "items": [
            "Phone Mount",
            "Tire Pressure Gauge",
            "Car Vacuum",
            "Dash Cam",
            "Seat Organizer",
        ],
        "modifiers": ["Universal", "Heavy-Duty", "Quick-Install", "Waterproof"],
    },
}
