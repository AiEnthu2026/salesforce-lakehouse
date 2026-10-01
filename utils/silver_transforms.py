def build_select_exprs(columns: dict) -> list:
    return [f"{expr} AS {alias}" for alias, expr in columns.items()]


def quarantine_expr(rules: dict) -> str:
    combined = " AND ".join(f"({rule})" for rule in rules.values())
    return f"NOT COALESCE({combined}, FALSE)"