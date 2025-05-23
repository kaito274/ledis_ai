import time

def is_key_expired(key, data_store, expiration_store, type_store):
    """
    Checks if a key is expired. If so, cleans it up from all stores.
    Returns True if expired and cleaned, False otherwise.
    """
    if key in expiration_store and expiration_store[key] < time.time():
        if key in data_store:
            del data_store[key]
        del expiration_store[key]
        if key in type_store:
            del type_store[key]
        return True
    return False

def check_type(key, expected_type, data_store, type_store):
    """
    Checks if the key exists and is of the expected type.
    Returns an error message string if there's an issue, or None if OK.
    Assumes key existence is already checked or handled by the caller if non-existence is not a type error.
    """
    if key not in data_store: 
        return f"ERROR: Key '{key}' not found" 
    
    actual_type = type_store.get(key)
    if actual_type != expected_type:
        return f"ERROR: WRONGTYPE Operation against a key holding the wrong kind of value. Key '{key}' is a {actual_type}, expected {expected_type}."
    return None