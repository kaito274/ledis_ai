import time
from ledis_utils import is_key_expired, check_type

# --- Data Storage ---
DATA_STORE = {}
EXPIRATION_STORE = {}
TYPE_STORE = {}

# --- Command Handler Functions ---

def handle_set(args):
    if len(args) != 2:
        return "ERROR: SET requires 2 arguments (key value)"
    key, value = args[0], args[1]
    is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE)
    DATA_STORE[key] = value
    TYPE_STORE[key] = "string"
    if key in EXPIRATION_STORE:
        del EXPIRATION_STORE[key]
    return "OK"

def handle_get(args):
    if len(args) != 1:
        return "ERROR: GET requires 1 argument (key)"
    key = args[0]
    if is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
        return f'ERROR: Key "{key}" has expired and been deleted'
    if key not in DATA_STORE:
        return f'ERROR: Key "{key}" not found'
    
    type_error = check_type(key, "string", DATA_STORE, TYPE_STORE)
    if type_error: return type_error
    return DATA_STORE[key]

def handle_rpush(args):
    if len(args) < 2:
        return "ERROR: RPUSH requires at least 2 arguments (key value1 [value2...])"
    key, values_to_push = args[0], args[1:]
    
    is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE)
    
    if key in DATA_STORE:
        type_error = check_type(key, "list", DATA_STORE, TYPE_STORE)
        if type_error: return type_error
    else:
        DATA_STORE[key] = []
        TYPE_STORE[key] = "list"

    DATA_STORE[key].extend(values_to_push)
    if key in EXPIRATION_STORE: # Remove expiration if it exists
        del EXPIRATION_STORE[key]
    return str(len(DATA_STORE[key]))

def handle_lpop(args):
    if len(args) != 1:
        return "ERROR: LPOP requires 1 argument (key)"
    key = args[0]
    if is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
        return f'ERROR: Key "{key}" has expired and been deleted'
    if key not in DATA_STORE:
        return f'ERROR: Key "{key}" not found'

    type_error = check_type(key, "list", DATA_STORE, TYPE_STORE)
    if type_error: return type_error
    
    if not DATA_STORE[key]: # empty list
        return "(nil)"
    
    if key in EXPIRATION_STORE: # Remove expiration if it exists
        del EXPIRATION_STORE[key]
    return DATA_STORE[key].pop(0)

def handle_lrange(args):
    if len(args) != 3:
        return "ERROR: LRANGE requires 3 arguments (key start stop)"
    key, start_str, stop_str = args[0], args[1], args[2]

    if is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
        return f'ERROR: Key "{key}" has expired and been deleted'
    if key not in DATA_STORE:
        return f'ERROR: Key "{key}" not found'

    type_error = check_type(key, "list", DATA_STORE, TYPE_STORE)
    if type_error: return type_error

    try:
        start = int(start_str)
        stop = int(stop_str)
    except ValueError:
        return "ERROR: value is not an integer"
    
    if start < 0 or stop < 0:
        return "ERROR: start and stop must be non-negative integers"
    
    the_list = DATA_STORE.get(key, [])
            
    # [start: stop + 1] since we want to include start and stop
    elements = the_list[start : stop + 1]
    return " ".join(f'"{e}"' for e in elements) if elements else "(empty list or set)"

def handle_llen(args):
    if len(args) != 1:
        return "ERROR: LLEN requires 1 argument (key)"
    key = args[0]
    if is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
        return f'ERROR: Key "{key}" has expired and been deleted'
    if key not in DATA_STORE:
        return f'ERROR: Key "{key}" not found'

    type_error = check_type(key, "list", DATA_STORE, TYPE_STORE)
    if type_error: return type_error
    
    return str(len(DATA_STORE.get(key, [])))

def handle_keys(args):
    if len(args) != 0:
        return "ERROR: KEYS does not take arguments in this version"
    active_keys = []
    for k in list(DATA_STORE.keys()):
        if not is_key_expired(k, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
            active_keys.append(k)
    return " ".join(f'"{k}"' for k in active_keys) if active_keys else "(empty list or set)"

def handle_del(args):
    if len(args) == 0:
        return "ERROR: DEL requires at least one key"
    deleted_count = 0
    for key_to_del in args:
        was_present_before_del = key_to_del in DATA_STORE
        is_key_expired(key_to_del, DATA_STORE, EXPIRATION_STORE, TYPE_STORE)
        if was_present_before_del and key_to_del not in DATA_STORE:
            pass
        elif key_to_del in DATA_STORE:
            del DATA_STORE[key_to_del]
            if key_to_del in EXPIRATION_STORE:
                del EXPIRATION_STORE[key_to_del]
            if key_to_del in TYPE_STORE:
                del TYPE_STORE[key_to_del]
            deleted_count += 1
    return str(deleted_count)

def handle_flushdb(args):
    if len(args) != 0:
        return "ERROR: FLUSHDB does not take arguments"
    DATA_STORE.clear()
    EXPIRATION_STORE.clear()
    TYPE_STORE.clear()
    return "OK"

def handle_expire(args):
    if len(args) != 2:
        return "ERROR: EXPIRE requires 2 arguments (key seconds)"
    key, seconds_str = args[0], args[1]

    if is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
        return f'ERROR: Key "{key}" has expired and been deleted'
    if key not in DATA_STORE:
        return f'ERROR: Key "{key}" not found'
    
    try:
        seconds = int(seconds_str)
    except ValueError:
        return "ERROR: value is not an integer"
    
    if seconds <= 0:
        return "ERROR: seconds must be a positive integer"
    
    EXPIRATION_STORE[key] = time.time() + seconds
    return str(seconds)

def handle_ttl(args):
    if len(args) != 1:
        return "ERROR: TTL requires 1 argument (key)"
    key = args[0]

    if is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE):
        return f'ERROR: Key "{key}" has expired and been deleted'
    if key not in DATA_STORE:
        return f'ERROR: Key "{key}" not found'
    if key not in EXPIRATION_STORE:
        return f'ERROR: Key "{key}" has no expiration set'
    
    remaining_time = int(EXPIRATION_STORE[key] - time.time())
    if remaining_time < 0:
        is_key_expired(key, DATA_STORE, EXPIRATION_STORE, TYPE_STORE)
        return f'Key "{key}" has expired and been deleted'
    return str(remaining_time)

# --- Command Dispatcher ---
COMMAND_HANDLERS = {
    "SET": handle_set,
    "GET": handle_get,
    "RPUSH": handle_rpush,
    "LPOP": handle_lpop,
    "LRANGE": handle_lrange,
    "LLEN": handle_llen,
    "KEYS": handle_keys,
    "DEL": handle_del,
    "FLUSHDB": handle_flushdb,
    "EXPIRE": handle_expire,
    "TTL": handle_ttl,
    # "CHAT" TODO: Implement chat command
}

def execute_command(command_str): 
    parts = command_str.strip().split()
    if not parts:
        return "ERROR: Empty command"

    command_name = parts[0].upper()
    args = parts[1:]


    handler = COMMAND_HANDLERS.get(command_name)
    if handler:
        try:
            return handler(args)
        except Exception as e:
            print(f"Core Error in handler for {command_name}: {e}") 
            return f"ERROR: An unexpected error occurred while executing {command_name}: {str(e)}"
    else:
        return f"ERROR: Unknown command '{command_name}'"