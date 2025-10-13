"""
Test script for SQLiteHandler - Same interface as DuckDBHandler
"""
import pandas as pd
from sqlite_handler import SQLiteHandler


def run_poc():
    """Run the complete SQLite POC demonstration."""
    # Initialize database
    db = SQLiteHandler(db_path="test_clientes.db")

    table_name = "checkpoint_category_ids"
    col_id_name = "category_ids"
    
    try:
        # 1. Create table
        print("1. Creating table...")
        db.create_table(table_name, pk_def="category_ids VARCHAR(16)")
        print()

        # 2. Insert usando DataFrame (primeira vez - 5 registros)
        print("2. Inserting DataFrame (first batch - 5 records)...")
        df1 = pd.DataFrame({
            col_id_name: ["cat_1", "cat_2", "cat_3", "cat_4", "cat_5"]
        })
        db.insert_df(table_name, df1, [col_id_name])
        print()

        # 3. Select all records
        print("3. Selecting all records after first insert...")
        db.select_all(table_name, [col_id_name])
        print()

        # 4. Insert com duplicatas (deve ignorar cat_1, cat_2, cat_3)
        print("4. Inserting DataFrame with duplicates (should ignore cat_1, cat_2, cat_3)...")
        df2 = pd.DataFrame({
            col_id_name: ["cat_1", "cat_2", "cat_3", "cat_6", "cat_7"]
        })
        db.insert_df(table_name, df2, [col_id_name])
        print()

        # 5. Select all records (deve ter 7 registros únicos)
        print("5. Selecting all records after second insert...")
        results = db.select_all(table_name, [col_id_name])
        print(f"\n✓ Total unique records: {len(results)}")
        print()

        # 6. Test select without column specification (SELECT *)
        print("6. Testing SELECT * (all columns)...")
        db.select_all(table_name)
        print()

        # 7. Drop table
        print("7. Dropping table...")
        db.drop_table(table_name)
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\n" + "="*60)
        print("SQLite POC completed successfully!")
        print("="*60 + "\n")


if __name__ == "__main__":
    run_poc()
