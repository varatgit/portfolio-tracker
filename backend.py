# backend_fin.py

import psycopg2
from psycopg2 import sql
import streamlit as st

# Database connection details
DB_HOST = "localhost"
DB_NAME = "Portfolio Tracker"
DB_USER = "postgres"
DB_PASS = "vardhini"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

# --- CRUD Operations ---

# CREATE
def add_asset(ticker, asset_class_id, name):
    """Adds a new asset to the database."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO assets (ticker, asset_class_id, name) VALUES (%s, %s, %s) ON CONFLICT (ticker) DO NOTHING;",
            (ticker, asset_class_id, name)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding asset: {e}")
        return False
    finally:
        if conn:
            conn.close()

def add_transaction(asset_id, transaction_date, transaction_type, quantity, price_per_share):
    """Adds a new transaction to the database."""
    conn = get_db_connection()
    total_cost = quantity * price_per_share
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO transactions (asset_id, transaction_date, transaction_type, quantity, price_per_share, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (asset_id, transaction_date, transaction_type, quantity, price_per_share, total_cost)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding transaction: {e}")
        return False
    finally:
        if conn:
            conn.close()

# READ
def get_all_assets():
    """Retrieves all assets with their associated class names."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.id, a.ticker, a.name, ac.name
            FROM assets a
            JOIN asset_classes ac ON a.asset_class_id = ac.id
            ORDER BY a.ticker;
            """
        )
        return cur.fetchall()
    except Exception as e:
        st.error(f"Error getting assets: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_asset_classes():
    """Retrieves all asset classes."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM asset_classes;")
        return cur.fetchall()
    except Exception as e:
        st.error(f"Error getting asset classes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_asset_by_ticker(ticker):
    """Retrieves a single asset by its ticker symbol."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, ticker, name FROM assets WHERE ticker = %s;", (ticker,))
        return cur.fetchone()
    except Exception as e:
        st.error(f"Error getting asset by ticker: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_transactions():
    """Retrieves all transactions with asset ticker and name."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT t.id, a.ticker, t.transaction_date, t.transaction_type, t.quantity, t.price_per_share, t.total_cost
            FROM transactions t
            JOIN assets a ON t.asset_id = a.id
            ORDER BY t.transaction_date DESC;
            """
        )
        return cur.fetchall()
    except Exception as e:
        st.error(f"Error getting transactions: {e}")
        return []
    finally:
        if conn:
            conn.close()

# UPDATE
def update_asset_name(asset_id, new_name):
    """Updates the name of an asset."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE assets SET name = %s WHERE id = %s;",
            (new_name, asset_id)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating asset: {e}")
        return False
    finally:
        if conn:
            conn.close()

# DELETE
def delete_asset(asset_id):
    """Deletes an asset and its associated transactions."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Delete related transactions first due to foreign key constraints
        cur.execute("DELETE FROM transactions WHERE asset_id = %s;", (asset_id,))
        cur.execute("DELETE FROM assets WHERE id = %s;", (asset_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting asset: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_transaction(transaction_id):
    """Deletes a transaction."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id = %s;", (transaction_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting transaction: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Business Insights ---
def get_total_portfolio_value():
    """Calculates the total portfolio value based on transactions."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT SUM(total_cost) FROM transactions WHERE transaction_type = 'BUY';
            """
        )
        total_buy_cost = cur.fetchone()[0] or 0.0

        cur.execute(
            """
            SELECT SUM(total_cost) FROM transactions WHERE transaction_type = 'SELL';
            """
        )
        total_sell_cost = cur.fetchone()[0] or 0.0

        return total_buy_cost - total_sell_cost
    except Exception as e:
        st.error(f"Error calculating total portfolio value: {e}")
        return 0.0
    finally:
        if conn:
            conn.close()

def get_insights():
    """Provides key business insights using aggregate functions."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        insights = {}

        # 1. Total Assets by Type (COUNT)
        cur.execute("SELECT ac.name, COUNT(a.id) FROM assets a JOIN asset_classes ac ON a.asset_class_id = ac.id GROUP BY ac.name;")
        insights['assets_by_type'] = dict(cur.fetchall())

        # 2. Total money invested (SUM)
        cur.execute("SELECT SUM(total_cost) FROM transactions WHERE transaction_type = 'BUY';")
        insights['total_investment'] = cur.fetchone()[0] or 0.0

        # 3. Average cost per share for all buys (AVG)
        cur.execute("SELECT AVG(price_per_share) FROM transactions WHERE transaction_type = 'BUY';")
        insights['avg_cost_per_share'] = cur.fetchone()[0] or 0.0

        # 4. Highest transaction value (MAX)
        cur.execute("SELECT MAX(total_cost) FROM transactions;")
        insights['max_transaction_value'] = cur.fetchone()[0] or 0.0

        # 5. Lowest transaction value (MIN)
        cur.execute("SELECT MIN(total_cost) FROM transactions;")
        insights['min_transaction_value'] = cur.fetchone()[0] or 0.0

        return insights
    except Exception as e:
        st.error(f"Error getting insights: {e}")
        return {}
    finally:
        if conn:
            conn.close()