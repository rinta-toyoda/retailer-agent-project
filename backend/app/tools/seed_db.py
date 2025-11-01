"""
Database Seed Script
Populates database with initial products and inventory.

Usage:
    Local development (with LocalStack):
        python -m app.tools.seed_db

    Production (with AWS S3 and RDS):
        export DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/dbname"
        export S3_BUCKET_NAME="your-prod-bucket"
        export AWS_ACCESS_KEY_ID="your-access-key"
        export AWS_SECRET_ACCESS_KEY="your-secret-key"
        export AWS_REGION="us-east-1"
        unset S3_ENDPOINT_URL  # Important: don't use LocalStack
        python -m app.tools.seed_db --production

    Force reseed:
        python -m app.tools.seed_db --force
"""

import mimetypes
import os
import random
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from app.domain.inventory_item import InventoryItem
from app.domain.product import Product
from app.domain.user import User
from app.infra.database import SessionLocal, init_db
from app.infra.s3_client import get_s3_client
from app.services.auth_service import AuthService

BASE_DIR = Path(__file__).resolve().parents[3]
_LOCAL_ABSOLUTE_ASSET_DIR = Path("/Users/rintabocek/work/Usyd/Agent/assets/product_images")
if _LOCAL_ABSOLUTE_ASSET_DIR.exists():
    ASSET_DIR = _LOCAL_ABSOLUTE_ASSET_DIR
else:
    ASSET_DIR = BASE_DIR / "assets" / "product_images"
FRONTEND_IMAGE_DIR = BASE_DIR / "frontend" / "public" / "product-images"
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def seed_products(db: Session) -> List[Product]:
    """Seed products into database and return the created rows."""
    products = [
        # Running Shoes
        Product(sku="RUN-001", name="CloudRunner Pro", description="Breathable red mesh road runner with cloud cushioning, moisture control lining, reflective heel tabs, and light rain protection for daily training",
                price=Decimal("129.99"), category="running shoes", brand="SpeedFit", color="red", features="breathable,lightweight,cushioned,reflective,water-resistant"),
        Product(sku="RUN-002", name="AeroFlex Runners", description="Featherweight blue knit marathon shoe with responsive foam midsole, reinforced eyestays, and ventilated toe box for long-distance road work",
                price=Decimal("149.99"), category="running shoes", brand="SpeedFit", color="blue", features="lightweight,durable,responsive,ventilated,long-distance"),
        Product(sku="RUN-003", name="TrailBlaze Elite", description="Black trail runner with waterproof bootie, rock plate, aggressive lug outsole, and abrasion-resistant toe guard for wet, muddy climbs",
                price=Decimal("159.99"), category="running shoes", brand="TrailMaster", color="black", features="durable,waterproof,grippy,rock-plate,trail-ready"),

        # Sneakers
        Product(sku="SNK-001", name="Urban Flex Sneakers", description="White leather cupsole sneaker with cushioned collar, stain-resistant coating, and breathable side vents for all-day city wear",
                price=Decimal("89.99"), category="sneakers", brand="UrbanStyle", color="white", features="comfortable,stylish,stain-resistant,padded,versatile"),
        Product(sku="SNK-002", name="Classic Canvas", description="Black retro canvas low-top with vulcanized rubber sole, reinforced eyelets, and arch-support footbed for easy casual styling",
                price=Decimal("59.99"), category="sneakers", brand="RetroKicks", color="black", features="stylish,breathable,lightweight,vulcanized,retro"),

        # Shirts
        Product(sku="SHT-001", name="Performance Tee", description="Red micro-mesh athletic tee with moisture-wicking yarns, anti-odor finish, flatlock seams, and reflective shoulder strip",
                price=Decimal("34.99"), category="shirt", brand="AthleticWear", color="red", features="breathable,moisture-wicking,anti-odor,quick-dry,stretch"),
        Product(sku="SHT-002", name="Casual Cotton Shirt", description="Blue garment-washed 100% cotton shirt with soft-hand feel, chest pocket, and relaxed silhouette for laid-back days",
                price=Decimal("29.99"), category="shirt", brand="CasualCo", color="blue", features="comfortable,breathable,soft-touch,versatile,relaxed-fit"),
        Product(sku="SHT-003", name="Cooling Polo", description="Graphite perforated recycled-poly polo with cooling yarns, bonded placket, and UPF 40 sun protection for warm tee times",
                price=Decimal("54.99"), category="shirt", brand="AthleticWear", color="gray", features="breathable,cooling,anti-odor,uv-protection,stretch"),
        Product(sku="SHT-004", name="Linen Camp Shirt", description="Natural linen-blend camp shirt with coconut buttons, vented hem, and relaxed resort silhouette",
                price=Decimal("64.99"), category="shirt", brand="CoastalLife", color="beige", features="lightweight,breathable,relaxed-fit,wrinkle-resistant,summer-ready"),

        # Jackets
        Product(sku="JKT-001", name="WindShield Jacket", description="Black ripstop shell with windproof membrane, packable hood, stretch cuffs, and reflective piping for breezy night runs",
                price=Decimal("119.99"), category="jacket", brand="WeatherGear", color="black", features="windproof,lightweight,packable,reflective,stretch-cuff"),
        Product(sku="JKT-002", name="RainGuard Pro", description="Green seam-sealed waterproof shell with adjustable storm flap, underarm vents, and soft fleece collar for wet commutes",
                price=Decimal("139.99"), category="jacket", brand="WeatherGear", color="green", features="waterproof,breathable,seam-sealed,ventilated,adjustable-hood"),
        Product(sku="JKT-003", name="Summit Puffer", description="Charcoal lightweight puffer insulated with recycled fill, helmet-compatible hood, and DWR coating for alpine layering",
                price=Decimal("179.99"), category="jacket", brand="PeakLine", color="gray", features="insulated,packable,dwr-coated,helmet-compatible,recycled-fill"),
        Product(sku="JKT-004", name="Commuter Softshell", description="Navy double-weave softshell with fleece backing, articulated elbows, and secure interior media pocket",
                price=Decimal("149.99"), category="jacket", brand="MetroMotion", color="navy", features="water-resistant,wind-resistant,stretch,articulated,media-pocket"),

        # Pants
        Product(sku="PNT-001", name="FlexFit Joggers", description="Gray 4-way stretch knit jogger with tapered leg, zippered media pockets, and ankle zips for easy on-off",
                price=Decimal("69.99"), category="pants", brand="AthleticWear", color="gray", features="comfortable,flexible,4-way-stretch,tapered,zip-pockets"),
        Product(sku="PNT-002", name="Classic Denim Jeans", description="Blue indigo denim jean with reinforced knees, contrast stitching, coin pocket, and soft brushed interior",
                price=Decimal("79.99"), category="pants", brand="DenimCo", color="blue", features="durable,stylish,reinforced,mid-rise,classic-fit"),
        Product(sku="PNT-003", name="Tech Travel Chinos", description="Olive tech-twill chino with hidden drawcord waist, stain-resistant finish, and wrinkle-free stretch panels",
                price=Decimal("84.99"), category="pants", brand="Voyager", color="olive", features="wrinkle-resistant,stretch,stain-resistant,travel-ready,hidden-drawcord"),
        Product(sku="PNT-004", name="Thermal Run Leggings", description="Black brushed interior running tight with compressive panels, drop-in phone pocket, and reflective calf tape",
                price=Decimal("74.99"), category="pants", brand="AthleticWear", color="black", features="thermal,compressive,reflective,pocketed,moisture-wicking"),

        # Accessories
        Product(sku="ACC-001", name="Sport Headband", description="Red recycled-poly headband with moisture-channel weave, anti-slip silicone interior, and quick-dry finish",
                price=Decimal("14.99"), category="accessories", brand="AthleticWear", color="red", features="breathable,comfortable,moisture-wicking,anti-slip,quick-dry"),
        Product(sku="ACC-002", name="Running Socks 3-Pack", description="White cushioned running socks with arch support band, blister-guard heel tabs, mesh vents, and antimicrobial yarns",
                price=Decimal("24.99"), category="accessories", brand="SpeedFit", color="white", features="comfortable,durable,cushioned,anti-blister,odor-control"),
        Product(sku="ACC-003", name="Trail Daypack", description="26L graphite trail pack with hydration sleeve, trekking pole loops, waterproof bottom panel, and ventilated back panel",
                price=Decimal("129.99"), category="accessories", brand="PeakLine", color="gray", features="hydration-compatible,water-resistant,ventilated,gear-loops,lightweight"),
        Product(sku="ACC-004", name="Insulated Running Gloves", description="Black softshell gloves with touchscreen pads, reflective knuckle print, and windproof membrane",
                price=Decimal("39.99"), category="accessories", brand="SpeedFit", color="black", features="touchscreen,windproof,insulated,reflective,grip-palm"),
        Product(sku="ACC-005", name="Compression Calf Sleeves", description="Royal blue graduated compression sleeves with targeted shin support and mesh cooling vents",
                price=Decimal("34.99"), category="accessories", brand="AthleticWear", color="blue", features="compression,moisture-wicking,cooling,shin-support,quick-dry"),
        Product(sku="ACC-006", name="Weekender Duffel", description="Midnight navy 45L travel duffel with water-repellent shell, shoe garage, padded shoulder strap, and luggage passthrough",
                price=Decimal("149.99"), category="accessories", brand="Voyager", color="navy", features="water-repellent,shoe-compartment,padded-strap,luggage-sleeve,carry-on"),
    ]

    # Add products to database
    for product in products:
        db.add(product)

    db.commit()
    print(f"Seeded {len(products)} products")
    return products


def _seed_users(db: Session):
    """Seed initial users if they don't exist."""
    existing_users = db.query(User).count()
    if existing_users > 0:
        print(f"Users already exist ({existing_users} users), skipping user seed")
        return

    print("Seeding initial users...")
    users_data = [
        {
            "username": "admin",
            "email": "admin@retailer.demo",
            "password": "admin123",
            "full_name": "Admin User",
            "is_superuser": True
        },
        {
            "username": "demo1",
            "email": "demo1@retailer.demo",
            "password": "demo123",
            "full_name": "Demo User 1",
            "is_superuser": False
        },
        {
            "username": "demo2",
            "email": "demo2@retailer.demo",
            "password": "demo123",
            "full_name": "Demo User 2",
            "is_superuser": False
        }
    ]

    for user_data in users_data:
        password = user_data.pop("password")
        user = User(
            **user_data,
            hashed_password=AuthService.get_password_hash(password),
            is_active=True
        )
        db.add(user)

    db.commit()
    print(f"Created {len(users_data)} initial users")
    print("\nDefault Login Credentials:")
    print("   Admin: username=admin, password=admin123")
    print("   Demo1: username=demo1, password=demo123")
    print("   Demo2: username=demo2, password=demo123")
    print("\nIMPORTANT: Change these passwords in production!\n")


def ensure_seed_data(force: bool = False) -> None:
    """Ensure products/inventory/images exist; optionally force reseed."""
    print("Ensuring demo catalog is populated...")
    init_db()
    db = SessionLocal()
    try:
        # Seed users first
        _seed_users(db)

        # Then seed products and inventory
        existing_products = db.query(Product).count()
        products_to_seed: Optional[List[Product]] = None

        if existing_products == 0 or force:
            if existing_products and force:
                print("Force mode enabled — reseeding products.")
            products_to_seed = seed_products(db)
            _seed_inventory(db, products_to_seed)
        else:
            print(f"Database already contains {existing_products} products. Skipping inserts.")

        _attach_product_images(db, products_to_seed)
        print("Seed data ready")
    except Exception as exc:
        print(f"Error ensuring seed data: {exc}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def _seed_inventory(db: Session, products: Iterable[Product]) -> None:
    """Create inventory rows for all provided products."""
    count = 0
    for product in products:
        inventory = InventoryItem(
            sku=product.sku,
            product_id=product.id,
            quantity=100,
            reserved_quantity=0,
            low_stock_threshold=10
        )
        db.add(inventory)
        count += 1

    db.commit()
    print(f"Seeded inventory for {count} products")


def _generate_placeholder_svg(product_name: str, color: str) -> str:
    """Generate a simple SVG placeholder image for products."""
    # Map color names to hex values
    color_map = {
        "red": "#EF4444",
        "blue": "#3B82F6",
        "green": "#10B981",
        "yellow": "#F59E0B",
        "purple": "#8B5CF6",
        "pink": "#EC4899",
        "orange": "#F97316",
        "black": "#1F2937",
        "white": "#F3F4F6",
        "gray": "#6B7280",
        "grey": "#6B7280",
        "brown": "#92400E",
    }
    
    bg_color = color_map.get(color.lower(), "#9CA3AF")
    
    # Truncate product name if too long
    display_name = product_name if len(product_name) <= 20 else product_name[:17] + "..."
    
    svg = f'''<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="400" fill="{bg_color}" opacity="0.2"/>
  <rect x="50" y="50" width="300" height="300" fill="{bg_color}" opacity="0.4" rx="20"/>
  <text x="200" y="180" font-family="Arial, sans-serif" font-size="18" font-weight="bold" 
        text-anchor="middle" fill="#1F2937">{display_name}</text>
  <text x="200" y="220" font-family="Arial, sans-serif" font-size="14" 
        text-anchor="middle" fill="#6B7280">Product Image</text>
  <circle cx="200" cy="260" r="30" fill="{bg_color}" opacity="0.6"/>
</svg>'''
    
    return svg


def _attach_product_images(db: Session, products: Optional[Iterable[Product]] = None) -> None:
    """Attach per-product images when an asset matches the SKU; otherwise fall back to generic images or placeholders."""
    image_files = sorted(
        path for path in ASSET_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    )

    try:
        s3_client = get_s3_client()
    except Exception as exc:  # pragma: no cover - network/deps issues handled at runtime
        print(f"Unable to connect to S3/LocalStack ({exc}). Using placeholder URLs only.")
        s3_client = None

    if products is None:
        products = db.query(Product).all()

    products = [product for product in products if not product.image_url]

    if not products:
        print("All products already have images. Skipping upload.")
        return

    if not image_files:
        print(f"No product images found in {ASSET_DIR}. Generating placeholder images in S3...")

    sku_slugs = {product.sku.lower() for product in products}
    specific_image_map = {
        path.stem.lower(): path
        for path in image_files
        if path.stem.lower() in sku_slugs
    }
    generic_images = [path for path in image_files if path.stem.lower() not in sku_slugs]

    for product in products:
        image_url = None
        sku_key = product.sku.lower()
        image_path = specific_image_map.get(sku_key)

        if not image_path and generic_images:
            image_path = random.choice(generic_images)

        if not image_path:
            if image_files:
                print(f"No asset matched {product.sku}. Generating placeholder image.")
            # Generate a simple placeholder image as SVG
            filename = f"{sku_key}-placeholder.svg"
            svg_content = _generate_placeholder_svg(product.name, product.color or "gray")
            
            if s3_client:
                try:
                    image_url = s3_client.upload_image(
                        svg_content.encode('utf-8'),
                        "image/svg+xml",
                        filename=filename,
                    )
                    print(f"Generated placeholder for {product.sku}")
                except ValueError as exc:
                    print(f"Failed to upload placeholder for {product.sku}: {exc}")
        else:
            content_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
            filename = image_path.name
            if image_path.stem.lower() != sku_key:
                filename = f"{sku_key}-{image_path.name}"

            with image_path.open("rb") as file_obj:
                file_bytes = file_obj.read()

            if s3_client:
                try:
                    image_url = s3_client.upload_image(
                        file_bytes,
                        content_type,
                        filename=filename,
                    )
                    print(f"Uploaded {image_path.name} for {product.sku}")
                except ValueError as exc:
                    print(f"Failed to upload image for {product.sku}: {exc}")
            
            if not image_url:
                image_url = _copy_placeholder_to_public(image_path)
                print(f"Using local placeholder for {product.sku}: {image_url}")

        product.image_url = image_url

    db.commit()


def main():
    """Main entry point with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed database with products and inventory")
    parser.add_argument(
        "--production",
        action="store_true",
        help="Production mode: Use real AWS S3 and RDS endpoint from environment"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reseed even if products already exist"
    )
    
    args = parser.parse_args()
    
    if args.production:
        print("Running in PRODUCTION mode")
        print("  - Using AWS S3 (not LocalStack)")
        print("  - Using RDS endpoint from DATABASE_URL")
        print("  - Will upload real images to S3 bucket\n")
        
        # Validate production environment variables
        required_vars = ["DATABASE_URL", "S3_BUCKET_NAME", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables for production:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\nSet these environment variables before running --production mode")
            sys.exit(1)
        
        # Ensure S3_ENDPOINT_URL is NOT set (to use real AWS)
        if os.getenv("S3_ENDPOINT_URL"):
            print("WARNING: S3_ENDPOINT_URL is set, which will use LocalStack instead of AWS S3")
            print("  Unset S3_ENDPOINT_URL to use real AWS S3")
            response = input("   Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    ensure_seed_data(force=args.force)


if __name__ == "__main__":
    main()


def _copy_placeholder_to_public(image_path: Path) -> str:
    """Copy placeholder into Next.js public folder and return relative URL."""
    FRONTEND_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    target_path = FRONTEND_IMAGE_DIR / image_path.name
    shutil.copy(image_path, target_path)
    return f"/product-images/{image_path.name}"
