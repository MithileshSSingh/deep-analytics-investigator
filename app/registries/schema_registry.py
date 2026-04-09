SCHEMA_REGISTRY = {
    "payments": {
        "time_column": "payment_timestamp",
        "columns": {
            "payment_id": "VARCHAR",
            "order_id": "VARCHAR",
            "payment_timestamp": "TIMESTAMP",
            "provider": "VARCHAR",
            "payment_method": "VARCHAR",
            "payment_status": "VARCHAR",
            "error_code": "VARCHAR",
            "amount": "DOUBLE",
            "country": "VARCHAR",
            "device_type": "VARCHAR",
            "browser": "VARCHAR",
        },
        "dimensions": ["device_type", "country", "provider", "payment_method"],
        "routes": ["revenue_investigation"],
    }
}
