import os
import sys
import json
import pip

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
    print("Found Config")

with open("config.json") as f:
    config = json.load(f)

INTERACTIVE_MODE = not len(sys.argv) > 1


win = os.name == "nt"


def clear_screen():
    if win:
        os.system("cls")
    else:
        os.system("clear")


def install():
    pip.main(['install', '-r', "req.txt"])


def wait():
    if INTERACTIVE_MODE:
        input("Press enter to continue.")


def user_choice():
    return input("> ").lower().strip()


def menu():
    while True:
        print(intro)
        print("Main Menu:\n")
        print("1. Set Token")
        print("2. Set Owner ID")
        print("3. Set Prefix")
        print("4. Set Logging Channel")
        print("5. Install Requirements")
        print("6. Debug Mode")
        choice = user_choice()
        if choice == "1":
            with open(h, "r+") as f:
                settings = json.load(f)
                token = input("Please enter token here: ")
                settings["Token"] = token
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Token")
                wait()
        elif choice == "2":
            with open(h, "r+") as f:
                settings = json.load(f)
                id = input("Please enter Owner ID here: ")
                settings["Owner ID"] = id
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Owner ID")
                wait()
        elif choice == "3":
            with open(h, "r+") as f:
                settings = json.load(f)
                prefix = input("Please enter Prefix here: ")
                settings["Prefix"] = prefix
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Prefix")
                wait()
        elif choice == "4":
            with open(h, "r+") as f:
                settings = json.load(f)
                login = input("Please enter Logging Channel ID here: ")
                settings["LOG_CHANNEL"] = login
                f.seek(0)
                f.write(json.dumps(settings, indent=4, sort_keys=True))
                f.truncate()
                print("Set Logging Channel")
                wait()
        elif choice == "5":
            install()
            wait()
        elif choice == "0":
            break
        clear_screen()

if __name__ == '__main__':
    menu()