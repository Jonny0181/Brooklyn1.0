import os
import sys
import json
import pip
import subprocess

INTERACTIVE_MODE = not len(sys.argv) > 1
win = os.name == "nt"

def clear_screen():
    if win:
        os.system("cls")
    else:
        os.system("clear")

clear_screen()

intro = ("+------------------------+\n"
         "Brooklyn Launcher\n\n"
         "Github: https://jonnyboy2000.github.io/Brooklyn1.0/\n"
         "If you have any questions, open the link above.\n"
         "+------------------------+\n")

h = "config.json"
if not os.path.exists(h):
    with open(h, "w") as f:
        writeJ = '{"TOKEN": "None", "PREFIX": "None", "OWNER_ID": "None", "Debug": "False", "LOG_CHANNEL": "None"}'
        parse = json.loads(writeJ)
        f.write(json.dumps(parse, indent=4, sort_keys=True))
        f.truncate()
else:
    pass

with open("config.json") as f:
    config = json.load(f)


def install():
    pip.main(['install', '-r', "req.txt"])


def wait():
    if INTERACTIVE_MODE:
        input("Press enter to continue.")


def user_choice():
    return input("\n⤷ ").lower().strip()


def main_menu():
    while True:
        print(intro)
        print("Main Menu:\n")
        print("1. Run Brooklyn.")
        print("2. Setup config.")
        print("3. Install Requirements.")
        print("4. Quit.")
        choice = user_choice()
        if choice == "1":
            run_brooklyn()
        elif choice == "2":
            setup_menu()
        elif choice == "3":
            install()
            wait()
        elif choice == "4":
            break
        clear_screen()

def setup_menu():
    clear_screen()
    while True:
        print(intro)
        print("Config Setup:\n")
        print("1. Set Token")
        print("2. Set Owner ID")
        print("3. Set Prefix")
        print("4. Set Logging Channel")
        print("5. Go Back.")
        choice = user_choice()
        if choice == "1":
            with open(h, "r+") as f:
                settings = json.load(f)
                token = input("\nPlease enter token here.\n➣ ")
                settings["TOKEN"] = token
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Token")
                wait()
        elif choice == "2":
            with open(h, "r+") as f:
                settings = json.load(f)
                id = input("\nPlease enter Owner ID here\n➣ ")
                settings["OWNER_ID"] = id
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Owner ID")
                wait()
        elif choice == "3":
            with open(h, "r+") as f:
                settings = json.load(f)
                prefix = input("\nPlease enter Prefix here\n➣ ")
                settings["PREFIX"] = prefix
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Prefix")
                wait()
        elif choice == "4":
            with open(h, "r+") as f:
                settings = json.load(f)
                login = input("\nPlease enter Logging Channel ID here\n➣ ")
                settings["LOG_CHANNEL"] = login
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Logging Channel")
                wait()
        elif choice == "5":
            clear_screen()
            main_menu()
        elif choice == "0":
            break
        clear_screen()

def run_brooklyn():
    interpreter = sys.executable
    cmd = (interpreter, "main.py")
    while True:
        try:
            code = subprocess.call(cmd)
        except KeyboardInterrupt:
            code = 0
            break
        else:
            if code == 0:
                break

if __name__ == '__main__':
    main_menu()
