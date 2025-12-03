import os
import re
import sys
import time
import json
import random
import datetime
import requests
from rich import print
from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console

console = Console()
ses = requests.Session()

# =============================
# APPROVAL KEY SYSTEM (OWNER CONTROLLED)
# =============================
KEY_FILE = "keys.json"

def load_keys():
    try:
        return json.load(open(KEY_FILE, "r"))
    except:
        return {}

def save_keys(data):
    json.dump(data, open(KEY_FILE, "w"), indent=4)

def create_key(key, seconds=None):
    """Create a key. seconds=None for lifetime."""
    data = load_keys()
    if key in data:
        print(f"[yellow]Key {key} already exists![/]")
        return
    if seconds is None:
        data[key] = {"expire": "LIFETIME"}
        print(f"[green]Lifetime Key created:[/] {key}")
    else:
        expire_time = time.time() + seconds
        data[key] = {"expire": expire_time}
        print(f"[green]Key created:[/] {key}")
        print(f"[yellow]Expires at: {datetime.datetime.fromtimestamp(expire_time)}[/]")
    save_keys(data)

def revoke_key(key):
    """Remove a key to revoke access."""
    data = load_keys()
    if key in data:
        data.pop(key)
        save_keys(data)
        print(f"[red]Key {key} has been revoked![/]")
    else:
        print(f"[yellow]Key {key} not found.[/]")

def validate_key(key):
    data = load_keys()
    if key not in data:
        return False, "Key not found."
    expire = data[key]["expire"]
    if expire == "LIFETIME":
        return True, None
    if time.time() > expire:
        return False, "Key expired."
    remaining = expire - time.time()
    return True, remaining

def key_login():
    os.system("clear")
    console.print(Panel("[cyan]Enter Approval Key[/]", border_style="magenta"))
    key = input("Key: ").strip()
    valid, msg = validate_key(key)
    if not valid:
        console.print(Panel(f"[red]{msg}[/]", border_style="red"))
        time.sleep(2)
        exit()
    # Check owner key from file
    owner_file = os.path.join("keys", "OWNER")
    if os.path.exists(owner_file):
        OWNER_KEY = open(owner_file, "r").read().strip()
    else:
        OWNER_KEY = "Daev-OWNER"
    is_owner = key == OWNER_KEY
    if msg is None:
        console.print(Panel(f"[green]ACCESS GRANTED[/]\nRemaining Time: [yellow]LIFETIME[/]", border_style="green"))
    else:
        remaining = str(datetime.timedelta(seconds=int(msg)))
        console.print(Panel(f"[green]ACCESS GRANTED[/]\nRemaining Time: [yellow]{remaining}[/]", border_style="green"))
    time.sleep(1)
    return is_owner

# =============================
# DATE DICTIONARY
# =============================
DTX = {
    '1':'januari', '2':'februari', '3':'maret', '4':'april',
    '5':'mei', '6':'juni', '7':'juli', '8':'agustus',
    '9':'september', '10':'oktober', '11':'november', '12':'desember'
}

tgl = datetime.datetime.now().day
bln = DTX[str(datetime.datetime.now().month)]
thn = datetime.datetime.now().year
lj_lmn = f"{tgl} {bln} {thn}"

# =============================
# CREDIT / BANNER
# =============================
credit = """[bold red][bold green]
=== SPAM TOOL ===
"""

def show_banner():
    console.clear()
    console.print(credit, justify="left")

# =============================
# MAIN MENU
# =============================
def main_menu(is_owner=False):
    while True:
        show_banner()
        menu_items = [
            "[cyan]1.[/] Auto Share",
            "[cyan]2.[/] Add / Replace Cookie",
            "[cyan]3.[/] Remove Cookie"
        ]
        if is_owner:
            menu_items.append("[cyan]4.[/] Admin Panel")
        menu_items.append("[cyan]0.[/] Exit")

        menu_text = "\n".join(menu_items)
        console.print(
            Panel(menu_text, title="[bold green]MAIN MENU[/]", border_style="magenta", padding=(0,0), expand=True)
        )

        choice = input("\nChoose: ")

        if choice == "1":
            auto_login()
        elif choice == "2":
            add_cookie()
        elif choice == "3":
            remove_cookie()
        elif choice == "4" and is_owner:
            admin_panel()
        elif choice == "0":
            exit()
        else:
            console.print("[red]Invalid choice![/]")
            time.sleep(1)

# =============================
# ADMIN PANEL
# =============================
def admin_panel():
    while True:
        os.system("clear")
        show_banner()
        console.print(
            Panel(
                "\n".join([
                    "[cyan]1.[/] Create Key",
                    "[cyan]2.[/] Revoke Key",
                    "[cyan]3.[/] View All Keys",
                    "[cyan]0.[/] Back to Main Menu"
                ]),
                title="[bold green]ADMIN PANEL[/]",
                border_style="magenta",
                padding=(0,0),
                expand=True
            )
        )

        choice = input("\nChoose: ")

        if choice == "1":
            key_name = input("Enter new key name: ").strip()
            t = input("Lifetime? (y/n): ").strip().lower()
            if t == "y":
                create_key(key_name)
            else:
                days = int(input("Enter days until expiration: "))
                create_key(key_name, days*24*3600)
            input("Press Enter to continue...")
        elif choice == "2":
            key_name = input("Enter key to revoke: ").strip()
            revoke_key(key_name)
            input("Press Enter to continue...")
        elif choice == "3":
            keys = load_keys()
            if not keys:
                print("[yellow]No keys found.[/]")
            else:
                print("\n[bold green]ALL KEYS[/]")
                for k, v in keys.items():
                    expire = v["expire"]
                    if expire == "LIFETIME":
                        print(f"{k} : LIFETIME")
                    else:
                        dt = datetime.datetime.fromtimestamp(expire)
                        print(f"{k} : Expires at {dt}")
            input("\nPress Enter to continue...")
        elif choice == "0":
            break
        else:
            console.print("[red]Invalid choice![/]")
            time.sleep(1)

# =============================
# COOKIE FUNCTIONS
# =============================
def add_cookie():
    os.system('clear')
    print("[yellow]Enter account name:[/]")
    name = input("> ").strip()
    print("[yellow]Enter cookie:[/]")
    cookie = input("> ").strip()
    cookies = {}
    if os.path.exists("cookies.json"):
        cookies = json.load(open("cookies.json", "r"))
    cookies[name] = cookie
    json.dump(cookies, open("cookies.json","w"), indent=4)
    print(f"[green]Cookie saved for {name}![/]")
    time.sleep(1)
    main_menu(is_owner=True)

def remove_cookie():
    if not os.path.exists("cookies.json"):
        print("[red]No cookie to remove.[/]")
        time.sleep(1)
        return main_menu(is_owner=True)
    cookies = json.load(open("cookies.json","r"))
    if not cookies:
        print("[red]No cookie to remove.[/]")
        time.sleep(1)
        return main_menu(is_owner=True)
    print("[yellow]Saved accounts:[/]")
    for i, acc in enumerate(cookies.keys(), start=1):
        print(f"[cyan]{i}[/cyan]. {acc}")
    choice = int(input("\nChoose account to remove: ")) - 1
    key = list(cookies.keys())[choice]
    cookies.pop(key)
    json.dump(cookies, open("cookies.json","w"), indent=4)
    print(f"[green]Removed cookie for {key}[/]")
    time.sleep(1)
    main_menu(is_owner=True)

def select_cookie():
    if not os.path.exists("cookies.json"):
        console.print(Panel("[red]No saved cookies![/]", border_style="red"))
        time.sleep(1)
        return None
    cookies = json.load(open("cookies.json", "r"))
    if not cookies:
        console.print(Panel("[red]No saved cookies![/]", border_style="red"))
        time.sleep(1)
        return None
    cookie_list = "\n".join(f"[cyan]{i}.[/] {name}" for i, name in enumerate(cookies.keys(), start=1))
    show_banner()
    console.print(Panel(cookie_list, title="[bold green]Select Account[/]", border_style="blue", expand=True))
    choice = int(input("\nChoose: ")) - 1
    key = list(cookies.keys())[choice]
    return cookies[key], key

# =============================
# AUTO LOGIN & BOT / SHARE FUNCTIONS
# =============================
def auto_login():
    selected = select_cookie()
    if not selected:
        return main_menu()
    cookie, account_name = selected
    print(f"[yellow]Checking cookie for {account_name}...[/]")
    try:
        res = requests.get(
            "https://business.facebook.com/business_locations",
            headers={"user-agent":"Mozilla/5.0","cookie":cookie}
        )
        if res.status_code != 200:
            print(f"[red]Failed to connect, status code {res.status_code}[/]")
            time.sleep(2)
            return main_menu()
        match = re.search(r"(EAAG\w+)", res.text)
        if match:
            token = match.group(1)
            open("token.txt","w").write(token)
            print(f"[green]Login success for {account_name}![/]")
            time.sleep(1)
            bot(cookie)
        else:
            print("[red]Cookie invalid or token not found![/]")
            time.sleep(2)
            main_menu()
    except requests.exceptions.RequestException as e:
        print(f"[red]Network error: {e}[/]")
        time.sleep(2)
        main_menu()

def bot(cookie):
    LijA = str(datetime.datetime.now().strftime('%H:%M:%S'))
    LiMoN = {
        'Sunday':'Minggu','Monday':'Senin','Tuesday':'Selasa',
        'Wednesday':'Rabu','Thursday':'Kamis','Friday':'Jumat','Saturday':'Sabtu'
    }[str(datetime.datetime.now().strftime("%A"))]
    token = open("token.txt","r").read()
    respon = random.choice(['Semangat Bang','Keren Bang','Gokil Suhu','Panutanku','Semangat Terus'])
    kom = ("\n\nKomentar Ini Ditulis Oleh Bot")
    requests.post(
        "https://graph.facebook.com/100089033379675_139149639062815/comments?"
        f"message={respon}{kom}\n[ Pukul {LijA} WIB ] "
        f"\n- {LiMoN}, {lj_lmn} -&access_token={token}",
        headers={"cookie":cookie}
    )
    lmnx9_share(cookie, token)

def lmnx9_share(cookie, token):
    os.system('clear')
    print(credit)
    header = {"user-agent": "Mozilla/5.0"}
    lija_xan = Prompt.ask("[magenta]Your Post Link[/]")
    lija_xans = int(input("Share Limit : "))
    print('[blue]Post Share Started...[/]')
    coki = {"cookie": cookie}
    success = 0
    failed = 0
    try:
        for _ in range(lija_xans):
            ress = ses.post(
                f"https://graph.facebook.com/me/feed?link={lija_xan}&published=0&access_token={token}",
                headers=header,
                cookies=coki
            ).json()
            if "id" in ress:
                success += 1
                print("[yellow]Successfully Shared[/]")
                print(f"[green]{ress['id']}[/]")
                print("[blue]" + "-"*40 + "[/]")
            else:
                failed += 1
                print(f"[red]Failed to share: {ress}[/]")
                print("[blue]" + "-"*40 + "[/]")
            sys.stdout.flush()
            time.sleep(0.2)
        print("\n[bold cyan]==== SHARE SUMMARY ====[/]")
        print(f"[green]✔ Success : {success}[/]")
        print(f"[red]✖ Failed  : {failed}[/]")
        print("[bold cyan]========================[/]\n")
        input("</> Press Enter To Back")
        main_menu(is_owner=True)
    except requests.exceptions.ConnectionError:
        exit('</> Server Error !!! \n')

# =============================
# START
# =============================
if __name__ == '__main__':
    owner = key_login()  # returns True if owner key
    main_menu(is_owner=owner)