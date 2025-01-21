import re

def is_anomalous_name(name):
    # Define allowed pattern
    allowed_pattern = r"^[A-Za-zÀ-ÿ' -]+$"
    
    # Check if the name matches the pattern
    if re.match(allowed_pattern, name):
        return False  # Name is valid
    else:
        return True   # Name is anomalous

# Test cases
names = ["LÃon Raymond", "LÃ©on Raymond", "John O'Connor", "Chloë Adams", "Mårten Jönsson"]
for name in names:
    print(f"{name}: {'Anomalous' if is_anomalous_name(name) else 'Valid'}")
