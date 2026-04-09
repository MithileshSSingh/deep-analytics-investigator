QUERY_FAMILY_REGISTRY = {
    "revenue_baseline": {
        "name": "revenue_baseline",
        "description": "Compute current revenue versus baseline for a target period.",
        "parameters": ["period"],
        "output_shape": ["current_day", "current_value", "baseline_value", "absolute_delta", "delta_pct"],
        "routes": ["revenue_investigation"],
    },
    "segment_delta": {
        "name": "segment_delta",
        "description": "Compare segment revenue versus baseline for a target period and dimension.",
        "parameters": ["period", "dimension"],
        "output_shape": ["segment", "current_revenue", "baseline_revenue", "absolute_delta", "delta_pct"],
        "routes": ["revenue_investigation"],
    },
    "payment_success_rate": {
        "name": "payment_success_rate",
        "description": "Compare payment success rate clusters for the current window.",
        "parameters": [],
        "output_shape": ["provider", "payment_method", "country", "device_type", "total_payments", "current_success_rate", "baseline_success_rate", "success_rate_delta"],
        "routes": ["revenue_investigation"],
    },
    "error_code_cluster": {
        "name": "error_code_cluster",
        "description": "Find concentrated failed payment error-code clusters.",
        "parameters": [],
        "output_shape": ["provider", "payment_method", "country", "device_type", "error_code", "failure_count"],
        "routes": ["revenue_investigation"],
    },
    "target_cluster_check": {
        "name": "target_cluster_check",
        "description": "Inspect the targeted India/mobile/Razorpay/UPI payment-success cluster.",
        "parameters": [],
        "output_shape": ["provider", "payment_method", "country", "device_type", "total_payments", "current_success_rate", "baseline_success_rate", "success_rate_delta"],
        "routes": ["revenue_investigation"],
    },
}
