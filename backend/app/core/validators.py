def validation_of_phone_number(v: str) -> str:
    if v.startswith("+"):
        if v[1] == "7" and v[1:].isdigit():
            return v
        else:
            raise ValueError("Phone number must start with 8 or +7 and contain only digits")
    
    if v[0] == "8" and v[1:].isdigit():
        return "+7" + v[1:]
    else:
        raise ValueError("Phone number must start with 8 or +7 and contain only digits")