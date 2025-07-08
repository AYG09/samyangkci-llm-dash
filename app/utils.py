def safe_num(value, default=None):
    """
    입력값을 숫자로 안전하게 변환합니다.
    변환할 수 없거나 값이 None이면 기본값(default)을 반환합니다.
    """
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
