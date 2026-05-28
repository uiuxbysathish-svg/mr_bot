def validate_order_value(value_str):
    """
    Validates whether the user-supplied order value is a positive number.
    Returns: (is_valid: bool, value_or_error: float/str)
    """
    if not value_str:
        return False, "Order value cannot be empty. Please enter a valid number (e.g. 12500)."
    
    # Strip currency symbol if any and commas
    cleaned = value_str.replace("₹", "").replace(",", "").strip()
    
    try:
        val = float(cleaned)
        if val < 0:
            return False, "Order value cannot be negative. Please enter a positive number."
        return True, val
    except ValueError:
        return False, "Invalid number format. Please enter numbers only (digits and decimal, e.g. 12500)."

def validate_non_empty(value_str, field_name="Field"):
    """
    Validates that a string value is not empty or just whitespace.
    Returns: (is_valid: bool, cleaned_value_or_error: str)
    """
    if not value_str or not value_str.strip():
        return False, f"{field_name} cannot be empty. Please enter a valid text response."
    return True, value_str.strip()
