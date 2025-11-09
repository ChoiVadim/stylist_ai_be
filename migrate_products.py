"""
Product migration script.
Loads product data from CSV file into the database.
"""
import csv
from pathlib import Path
from sqlalchemy.orm import Session
from src.database.user_db import SessionLocal, Product, init_db
from src.utils.logger import get_logger

logger = get_logger("migrate_products")


def migrate_products_from_csv(csv_path: Path, update_existing: bool = False, clear_first: bool = False) -> tuple[int, int, int]:
    """
    Migrate products from CSV file to database.
    
    Args:
        csv_path: Path to the CSV file
        update_existing: If True, update existing products instead of skipping
        clear_first: If True, clear all products before migration
        
    Returns:
        Tuple of (migrated_count, updated_count, skipped_count)
    """
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Initialize database
    init_db()
    
    db: Session = SessionLocal()
    migrated_count = 0
    updated_count = 0
    skipped_count = 0
    
    try:
        # Clear all products if requested
        if clear_first:
            logger.info("Clearing all existing products...")
            deleted = db.query(Product).delete()
            db.commit()
            logger.info(f"Cleared {deleted} existing products")
        
        logger.info(f"Reading products from CSV: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Extract data from CSV row
                    external_id = int(row.get('id', 0))
                    
                    # Check if product already exists
                    existing = db.query(Product).filter(
                        Product.external_id == external_id
                    ).first()
                    
                    if existing:
                        if update_existing:
                            # Update existing product
                            existing.description = row.get('description', '').strip() or None
                            existing.price = row.get('price', '').strip() or None
                            existing.image_url = row.get('imageUrl', '').strip() or None
                            existing.color_hex = row.get('colorHex', '').strip() or None
                            existing.product_url = row.get('productUrl', '').strip() or None
                            existing.color_name = row.get('colorName', '').strip() or None
                            existing.detail_description = row.get('detailDescription', '').strip() or None
                            existing.type = row.get('type', '').strip() or None
                            existing.personal_color_type = row.get('personalColorType', '').strip() or None
                            updated_count += 1
                            
                            if updated_count % 50 == 0:
                                db.commit()
                                logger.info(f"Updated {updated_count} products so far...")
                        else:
                            logger.debug(f"Product with ID {external_id} already exists, skipping")
                            skipped_count += 1
                        continue
                    
                    # Create new product
                    product = Product(
                        external_id=external_id,
                        description=row.get('description', '').strip() or None,
                        price=row.get('price', '').strip() or None,
                        image_url=row.get('imageUrl', '').strip() or None,
                        color_hex=row.get('colorHex', '').strip() or None,
                        product_url=row.get('productUrl', '').strip() or None,
                        color_name=row.get('colorName', '').strip() or None,
                        detail_description=row.get('detailDescription', '').strip() or None,
                        type=row.get('type', '').strip() or None,
                        personal_color_type=row.get('personalColorType', '').strip() or None,
                    )
                    
                    db.add(product)
                    migrated_count += 1
                    
                    if migrated_count % 50 == 0:
                        db.commit()
                        logger.info(f"Migrated {migrated_count} products so far...")
                        
                except Exception as e:
                    logger.error(f"Error processing row {row.get('id', 'unknown')}: {str(e)}", exc_info=True)
                    db.rollback()
                    continue
        
        # Final commit
        db.commit()
        logger.info(f"Migration completed: {migrated_count} products migrated, {updated_count} updated, {skipped_count} skipped")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
    
    return migrated_count, updated_count, skipped_count


def main():
    """Main entry point for migration."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate products from CSV file to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_products.py
  python migrate_products.py data/products.csv
  python migrate_products.py --update
  python migrate_products.py --clear
  python migrate_products.py --update --clear
        """
    )
    parser.add_argument(
        'csv_path',
        nargs='?',
        default='data/zara_data_output - zara_data_output.csv',
        help='Path to CSV file (default: data/zara_data_output - zara_data_output.csv)'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update existing products instead of skipping them'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all existing products before migration'
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_path)
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        parser.print_help()
        sys.exit(1)
    
    try:
        print("=" * 60)
        print("Product Migration from CSV")
        print("=" * 60)
        print(f"Source: {csv_path}")
        if args.update:
            print("Mode: Update existing products")
        if args.clear:
            print("Mode: Clear all products first")
        if not args.update and not args.clear:
            print("Mode: Skip existing products (use --update to update, --clear to clear)")
        print()
        
        migrated, updated, skipped = migrate_products_from_csv(
            csv_path,
            update_existing=args.update,
            clear_first=args.clear
        )
        
        print()
        print("=" * 60)
        print("Migration Summary:")
        print(f"  ✓ Migrated: {migrated} new products")
        if args.update:
            print(f"  ✓ Updated: {updated} existing products")
        print(f"  ⊘ Skipped: {skipped} products")
        print(f"  Total processed: {migrated + updated + skipped}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

