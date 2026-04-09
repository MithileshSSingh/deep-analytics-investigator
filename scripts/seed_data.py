import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import duckdb
import pandas as pd

DB_PATH = Path("data/demo.duckdb")
DAYS = 60
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def weighted_choice(options):
    values = [x[0] for x in options]
    weights = [x[1] for x in options]
    return random.choices(values, weights=weights, k=1)[0]


def random_timestamp_in_day(day: datetime) -> datetime:
    return day + timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )


COUNTRY_CITY_MAP = {
    "India": ["Bangalore", "Mumbai", "Delhi"],
    "US": ["San Francisco", "New York", "Austin"],
    "UAE": ["Dubai", "Abu Dhabi"],
    "UK": ["London", "Manchester"],
    "Germany": ["Berlin", "Munich"],
}
COUNTRY_WEIGHTS = [("India", 45), ("US", 25), ("UAE", 10), ("UK", 10), ("Germany", 10)]
DEVICE_WEIGHTS = [("mobile", 60), ("desktop", 35), ("tablet", 5)]
CHANNEL_WEIGHTS = [("organic", 30), ("paid_search", 25), ("social", 15), ("direct", 20), ("referral", 10)]
PRODUCT_TIER_WEIGHTS = [("basic", 55), ("pro", 30), ("premium", 15)]
PAYMENT_PROVIDER_WEIGHTS = {
    "India": [("razorpay", 60), ("stripe", 25), ("paypal", 15)],
    "US": [("stripe", 70), ("paypal", 20), ("razorpay", 10)],
    "UAE": [("stripe", 50), ("paypal", 30), ("razorpay", 20)],
    "UK": [("stripe", 65), ("paypal", 25), ("razorpay", 10)],
    "Germany": [("stripe", 60), ("paypal", 30), ("razorpay", 10)],
}
PAYMENT_METHOD_WEIGHTS = {
    "India": [("upi", 50), ("card", 35), ("wallet", 15)],
    "US": [("card", 70), ("wallet", 20), ("upi", 10)],
    "UAE": [("card", 65), ("wallet", 20), ("upi", 15)],
    "UK": [("card", 70), ("wallet", 20), ("upi", 10)],
    "Germany": [("card", 75), ("wallet", 15), ("upi", 10)],
}
BROWSER_BY_DEVICE = {
    "mobile": [("Chrome Mobile", 60), ("Safari Mobile", 35), ("Edge Mobile", 5)],
    "desktop": [("Chrome", 65), ("Firefox", 15), ("Safari", 10), ("Edge", 10)],
    "tablet": [("Safari Mobile", 50), ("Chrome Mobile", 50)],
}
OS_BY_DEVICE = {
    "mobile": [("Android", 70), ("iOS", 30)],
    "desktop": [("Windows", 55), ("macOS", 30), ("Linux", 15)],
    "tablet": [("iPadOS", 60), ("Android", 40)],
}
LANDING_PAGES = ["/", "/pricing", "/features", "/blog", "/compare"]
PAYMENT_ERROR_CODES = ["BANK_TIMEOUT", "UPI_COLLECT_FAILED", "PROVIDER_TIMEOUT", "INSUFFICIENT_FUNDS"]


def create_schema(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT, signup_timestamp TIMESTAMP, country TEXT, city TEXT, device_type TEXT, acquisition_channel TEXT, acquisition_campaign TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT, user_id TEXT, session_start TIMESTAMP, session_end TIMESTAMP, device_type TEXT, browser TEXT, os TEXT, landing_page TEXT, traffic_source TEXT, country TEXT, city TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS funnel_events (event_id TEXT, user_id TEXT, session_id TEXT, event_timestamp TIMESTAMP, funnel_step TEXT, device_type TEXT, browser TEXT, country TEXT, experiment_variant TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS orders (order_id TEXT, user_id TEXT, session_id TEXT, order_timestamp TIMESTAMP, product_tier TEXT, order_amount DOUBLE, currency TEXT, order_status TEXT, country TEXT, city TEXT, device_type TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS payments (payment_id TEXT, order_id TEXT, payment_timestamp TIMESTAMP, provider TEXT, payment_method TEXT, payment_status TEXT, error_code TEXT, amount DOUBLE, country TEXT, device_type TEXT, browser TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS refunds (refund_id TEXT, order_id TEXT, refund_timestamp TIMESTAMP, refund_amount DOUBLE, refund_reason TEXT, country TEXT, product_tier TEXT)")


def generate_users(start_date: datetime, days: int, total_users: int = 8000):
    rows = []
    for _ in range(total_users):
        country = weighted_choice(COUNTRY_WEIGHTS)
        rows.append({
            "user_id": uid("usr"),
            "signup_timestamp": random_timestamp_in_day(start_date + timedelta(days=random.randint(0, days - 1))),
            "country": country,
            "city": random.choice(COUNTRY_CITY_MAP[country]),
            "device_type": weighted_choice(DEVICE_WEIGHTS),
            "acquisition_channel": weighted_choice(CHANNEL_WEIGHTS),
            "acquisition_campaign": f"camp_{random.randint(1, 8)}",
        })
    return pd.DataFrame(rows)


def generate_sessions(users_df, start_date: datetime, days: int):
    rows = []
    users = users_df.to_dict("records")
    for day_offset in range(days):
        day = start_date + timedelta(days=day_offset)
        base_sessions = 2400 if day.weekday() < 5 else 1800
        total_sessions = base_sessions + random.randint(-250, 350)
        for _ in range(total_sessions):
            user = random.choice(users)
            device_type = user["device_type"] if random.random() < 0.7 else weighted_choice(DEVICE_WEIGHTS)
            rows.append({
                "session_id": uid("ses"),
                "user_id": user["user_id"],
                "session_start": random_timestamp_in_day(day),
                "session_end": random_timestamp_in_day(day),
                "device_type": device_type,
                "browser": weighted_choice(BROWSER_BY_DEVICE[device_type]),
                "os": weighted_choice(OS_BY_DEVICE[device_type]),
                "landing_page": random.choice(LANDING_PAGES),
                "traffic_source": weighted_choice(CHANNEL_WEIGHTS),
                "country": user["country"],
                "city": user["city"],
            })
    return pd.DataFrame(rows)


def generate_funnel_events(sessions_df):
    rows = []
    for session in sessions_df.to_dict("records"):
        session_time = pd.Timestamp(session["session_start"])
        rows.append({"event_id": uid("evt"), "user_id": session["user_id"], "session_id": session["session_id"], "event_timestamp": session_time, "funnel_step": "landing", "device_type": session["device_type"], "browser": session["browser"], "country": session["country"], "experiment_variant": random.choice(["A", "B"])})
        if random.random() < 0.22:
            signup_time = session_time + timedelta(minutes=random.randint(1, 8))
            rows.append({"event_id": uid("evt"), "user_id": session["user_id"], "session_id": session["session_id"], "event_timestamp": signup_time, "funnel_step": "signup", "device_type": session["device_type"], "browser": session["browser"], "country": session["country"], "experiment_variant": random.choice(["A", "B"])})
            if random.random() < 0.78:
                checkout_time = signup_time + timedelta(minutes=random.randint(1, 8))
                rows.append({"event_id": uid("evt"), "user_id": session["user_id"], "session_id": session["session_id"], "event_timestamp": checkout_time, "funnel_step": "checkout_start", "device_type": session["device_type"], "browser": session["browser"], "country": session["country"], "experiment_variant": random.choice(["A", "B"])})
    return pd.DataFrame(rows)


def price_for_tier(product_tier: str) -> float:
    if product_tier == "basic":
        return round(random.uniform(19, 49), 2)
    if product_tier == "pro":
        return round(random.uniform(79, 149), 2)
    return round(random.uniform(249, 599), 2)


def generate_orders(funnel_events_df, sessions_df):
    checkout_events = funnel_events_df[funnel_events_df["funnel_step"] == "checkout_start"]
    sessions_map = sessions_df.set_index("session_id").to_dict("index")
    rows = []
    for event in checkout_events.to_dict("records"):
        session = sessions_map.get(event["session_id"])
        if not session:
            continue
        product_tier = weighted_choice(PRODUCT_TIER_WEIGHTS)
        if session["country"] == "India" and session["device_type"] == "mobile" and random.random() < 0.35:
            product_tier = weighted_choice([("pro", 45), ("premium", 45), ("basic", 10)])
        rows.append({
            "order_id": uid("ord"),
            "user_id": event["user_id"],
            "session_id": event["session_id"],
            "order_timestamp": event["event_timestamp"] + timedelta(minutes=random.randint(1, 4)),
            "product_tier": product_tier,
            "order_amount": price_for_tier(product_tier),
            "currency": "USD",
            "order_status": "completed",
            "country": session["country"],
            "city": session["city"],
            "device_type": session["device_type"],
        })
    return pd.DataFrame(rows)


def generate_payments(orders_df, sessions_df):
    sessions_map = sessions_df.set_index("session_id").to_dict("index")
    rows = []
    for order in orders_df.to_dict("records"):
        session = sessions_map.get(order["session_id"])
        country = order["country"]
        provider = weighted_choice(PAYMENT_PROVIDER_WEIGHTS[country])
        payment_method = weighted_choice(PAYMENT_METHOD_WEIGHTS[country])

        if country == "India" and order["device_type"] == "mobile" and random.random() < 0.7:
            provider = "razorpay"
            payment_method = "upi"

        rows.append({
            "payment_id": uid("pay"),
            "order_id": order["order_id"],
            "payment_timestamp": pd.Timestamp(order["order_timestamp"]) + timedelta(minutes=random.randint(1, 3)),
            "provider": provider,
            "payment_method": payment_method,
            "payment_status": "success" if random.random() < 0.9 else "failed",
            "error_code": None,
            "amount": order["order_amount"],
            "country": order["country"],
            "device_type": order["device_type"],
            "browser": session["browser"],
        })
    payments_df = pd.DataFrame(rows)
    failed_mask = payments_df["payment_status"] == "failed"
    payments_df.loc[failed_mask, "error_code"] = [random.choice(PAYMENT_ERROR_CODES) for _ in range(failed_mask.sum())]
    return payments_df


def generate_refunds(orders_df):
    rows = []
    for order in orders_df.to_dict("records"):
        if random.random() < 0.03:
            rows.append({
                "refund_id": uid("ref"),
                "order_id": order["order_id"],
                "refund_timestamp": pd.Timestamp(order["order_timestamp"]) + timedelta(days=random.randint(1, 8)),
                "refund_amount": round(order["order_amount"] * random.uniform(0.5, 1.0), 2),
                "refund_reason": random.choice(["quality_issue", "wrong_item", "customer_complaint"]),
                "country": order["country"],
                "product_tier": order["product_tier"],
            })
    return pd.DataFrame(rows)


def inject_revenue_drop_incident(payments_df):
    payments_df = payments_df.copy()
    incident_date = payments_df["payment_timestamp"].max().date() - timedelta(days=1)
    mask = (
        (pd.to_datetime(payments_df["payment_timestamp"]).dt.date == incident_date) &
        (payments_df["country"] == "India") &
        (payments_df["device_type"] == "mobile") &
        (payments_df["provider"] == "razorpay") &
        (payments_df["payment_method"] == "upi") &
        (payments_df["payment_status"] == "success")
    )
    candidates = payments_df[mask]
    if not candidates.empty:
        high_value = candidates[candidates["amount"] >= candidates["amount"].median()]
        target_pool = high_value if not high_value.empty else candidates
        affected = target_pool.sample(frac=0.95, random_state=RANDOM_SEED)
        payments_df.loc[affected.index, "payment_status"] = "failed"
        payments_df.loc[affected.index, "error_code"] = [random.choice(["BANK_TIMEOUT", "UPI_COLLECT_FAILED", "PROVIDER_TIMEOUT"]) for _ in range(len(affected))]
        affected_rows = len(affected)
    else:
        affected_rows = 0
    return payments_df, {"incident_date": str(incident_date), "affected_rows": affected_rows}


def save_to_duckdb(conn, table_name, df):
    conn.register("temp_df", df)
    conn.execute(f"DELETE FROM {table_name}")
    conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
    conn.unregister("temp_df")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    create_schema(conn)
    start_date = datetime.now() - timedelta(days=DAYS)
    users_df = generate_users(start_date, DAYS)
    sessions_df = generate_sessions(users_df, start_date, DAYS)
    funnel_events_df = generate_funnel_events(sessions_df)
    orders_df = generate_orders(funnel_events_df, sessions_df)
    payments_df = generate_payments(orders_df, sessions_df)
    refunds_df = generate_refunds(orders_df)
    payments_df, incident_meta = inject_revenue_drop_incident(payments_df)
    save_to_duckdb(conn, "users", users_df)
    save_to_duckdb(conn, "sessions", sessions_df)
    save_to_duckdb(conn, "funnel_events", funnel_events_df)
    save_to_duckdb(conn, "orders", orders_df)
    save_to_duckdb(conn, "payments", payments_df)
    save_to_duckdb(conn, "refunds", refunds_df)
    print("Seed complete", incident_meta)
    conn.close()


if __name__ == "__main__":
    main()
