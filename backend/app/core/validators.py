def validation_of_phone_number(v: str) -> str:
    if not v or len(v) < 2:
        raise ValueError("Phone number must start with 8 or +7 and contain only digits")
    if v.startswith("+"):
        if len(v) != 12 or v[1] != "7" or not v[1:].isdigit():
            raise ValueError("Phone number must be +7 followed by 10 digits")
        return v
    if v[0] == "8" and len(v) == 11 and v[1:].isdigit():
        return "+7" + v[1:]
    raise ValueError("Phone number must start with 8 or +7 and contain only digits")