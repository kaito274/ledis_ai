import requests
import sys

SERVER_URL = "http://127.0.0.1:5000/"

def main():
    print("Ledis CLI (type 'EXIT' to quit)")
    # Construct the prompt similar to redis-cli
    prompt = f"{SERVER_URL.replace('http://', '').replace('/', '')}> "
    
    while True:
        try:
            command_input = input(prompt)
            if command_input.strip().upper() == "EXIT":
                break
            if not command_input.strip():
                continue

            response = requests.post(SERVER_URL, data=command_input)
            response.raise_for_status() # Raise an exception for HTTP errors
            print(response.text)

        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to Ledis server. Is it running?")
            break
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request failed: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError: # Handles Ctrl+D
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()