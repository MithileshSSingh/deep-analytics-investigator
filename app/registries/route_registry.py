ROUTE_REGISTRY = {
    "revenue_investigation": {
        "name": "revenue_investigation",
        "description": "Investigate revenue movement and identify likely causes.",
        "supported_metrics": ["revenue"],
        "supported_investigation_types": ["metric_drop", "metric_increase", "metric_change"],
        "required_tables": ["payments"],
        "supported_dimensions": ["device_type", "country", "provider", "payment_method"],
        "baseline_query_families": ["revenue_baseline"],
        "segment_query_families": ["segment_delta"],
        "validation_query_families": [
            "payment_success_rate",
            "error_code_cluster",
            "target_cluster_check",
        ],
        "stop_conditions": {
            "max_iterations": 2,
            "minimum_confidence_for_stop": "medium",
        },
    }
}
