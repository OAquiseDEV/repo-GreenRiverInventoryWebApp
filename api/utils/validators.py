import re

def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the data.

    Args:
        data: Dictionary containing the data
        required_fields: List of field names that are required

    Returns:
        Tuple (is_valid, error_message)
    """
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False, f"{field} es requerido"
    return True, None

def validate_email(email):
    """
    Validate email format.

    Args:
        email: Email string to validate

    Returns:
        Boolean indicating if email is valid
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_length(value, min_length=None, max_length=None):
    """
    Validate string length.

    Args:
        value: String to validate
        min_length: Minimum length (optional)
        max_length: Maximum length (optional)

    Returns:
        Tuple (is_valid, error_message)
    """
    if not value:
        return False, "Valor vacío"

    length = len(value)

    if min_length and length < min_length:
        return False, f"Debe tener al menos {min_length} caracteres"

    if max_length and length > max_length:
        return False, f"Debe tener máximo {max_length} caracteres"

    return True, None

def validate_positive_number(value, field_name="cantidad"):
    """
    Validate that a number is positive.

    Args:
        value: Number to validate
        field_name: Name of the field for error messages

    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        num = float(value)
        if num <= 0:
            return False, f"{field_name} debe ser mayor a 0"
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} debe ser un número válido"

def validate_non_negative_number(value, field_name="cantidad"):
    """
    Validate that a number is non-negative (>= 0).

    Args:
        value: Number to validate
        field_name: Name of the field for error messages

    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        num = float(value)
        if num < 0:
            return False, f"{field_name} debe ser mayor o igual a 0"
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} debe ser un número válido"
