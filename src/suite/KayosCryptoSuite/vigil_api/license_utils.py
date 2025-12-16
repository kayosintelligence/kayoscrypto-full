# vigil_api/license_utils.py

def validate_license(token: str) -> bool:
    try:
        # Token esperado
        expected = "KFRIDAY-LICENSE::kfriday.shop::A843F0D9E73A22C4B99E91C0"
        return token.strip() == expected
    except:
        return False
