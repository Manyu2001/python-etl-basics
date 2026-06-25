import pandas as pd
import sqlite3
import logging

# ── Logging Setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────
RAW_FILE = "data/olist_orders_dataset.csv"
DB_PATH  = "output.db"
TABLE    = "orders_clean"


# ── 1. EXTRACT ─────────────────────────────────────────────────
def extract(filepath: str) -> pd.DataFrame:
    log.info(f"Extracting from {filepath}")
    try:
        df = pd.read_csv(filepath)
        log.info(f"Extracted {len(df)} rows")
        return df
    except Exception as e:
        log.error(f"Extraction failed: {e}")
        raise


# ── 2. TRANSFORM ───────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Transforming data...")
    try:
        df = df[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp']]
        df = df.dropna()
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df['order_year']  = df['order_purchase_timestamp'].dt.year
        df['order_month'] = df['order_purchase_timestamp'].dt.month
        df = df[df['order_status'] == 'delivered']
        log.info(f"Transformed to {len(df)} rows")
        return df
    except Exception as e:
        log.error(f"Transform failed: {e}")
        raise


# ── 3. QUALITY CHECKS ──────────────────────────────────────────
def quality_check(df: pd.DataFrame) -> None:
    log.info("Running quality checks...")

    if df.empty:
        raise ValueError("Quality check failed: DataFrame is empty")

    duplicates = df.duplicated().sum()
    if duplicates > 0:
        log.warning(f"{duplicates} duplicate rows found")

    nulls = df.isnull().sum().sum()
    if nulls > 0:
        log.warning(f"{nulls} null values found")

    log.info("Quality checks passed")


# ── 4. LOAD ────────────────────────────────────────────────────
def load(df: pd.DataFrame, db_path: str, table: str) -> None:
    log.info(f"Loading {len(df)} rows into {db_path} → {table}")
    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table, conn, if_exists='replace', index=False)
        log.info("Load complete")
    except Exception as e:
        log.error(f"Load failed: {e}")
        raise


# ── 5. VALIDATE ────────────────────────────────────────────────
def validate(db_path: str, table: str) -> None:
    log.info("Validating loaded data...")
    try:
        with sqlite3.connect(db_path) as conn:
            result = pd.read_sql(
                f"SELECT order_year, order_month, COUNT(*) as order_count "
                f"FROM {table} GROUP BY order_year, order_month "
                f"ORDER BY order_year, order_month",
                conn
            )
        log.info(f"Validation result:\n{result.to_string(index=False)}")
    except Exception as e:
        log.error(f"Validation failed: {e}")
        raise


# ── ORCHESTRATOR ───────────────────────────────────────────────
def run():
    log.info("Pipeline started")
    df = extract(RAW_FILE)
    df = transform(df)
    quality_check(df)
    load(df, DB_PATH, TABLE)
    validate(DB_PATH, TABLE)
    log.info("Pipeline finished successfully")


if __name__ == "__main__":
    run()