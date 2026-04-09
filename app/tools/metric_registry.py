METRIC_REGISTRY = {
    "revenue": {
        "name": "revenue",
        "base_table": "payments",
        "expression": "SUM(amount)",
        "filters": ["payment_status = 'success'"],
        "time_column": "payment_timestamp",
        "supported_dimensions": [
            "device_type",
            "country",
            "provider",
            "payment_method",
        ],
    }
}
