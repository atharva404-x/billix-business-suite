
def validate_gstin(gstin: str) -> bool:
    """
    Basic GSTIN validation (checks length and first two digits are numeric).
    For production, implement full checksum validation per Indian GST rules.
    """
    if len(gstin) != 15:
        return False
    if not gstin[:2].isdigit():
        return False
    return True


def validate_hsn_sac(code: str) -> bool:
    """
    Basic HSN/SAC validation (checks length: 4-8 digits).
    """
    if not code.isdigit():
        return False
    if len(code) < 4 or len(code) > 8:
        return False
    return True

