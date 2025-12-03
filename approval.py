#!/usr/bin/env python3
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
# FILES & PATHS
# =============================
KEY_FILE = "keys.json"
COOKIES_FILE = "cookies.json"
OWNER_FILE_CANDIDATES = ["keys/OWNER", "owner.txt", "keys/owner.txt"]
ADMIN_PASS_FILE = "admin_pass.txt"
TOKEN_FILE = "token.txt"

# =============================
# UTIL: ensure files exist
# =============================
def ensure_files():
    for f in [KEY_FILE, COOKIES_FILE]:
        if not os.path.exists(f):
            with open(f, "w") as fx:
                json.dump({}, fx, indent=4)

ensure_files()

# =============================
# KEYS
# =============================
def load_keys():
    try:
        return json.load(open(KEY_FILE, "r"))
    except Exception:
        return {}

def save_keys(data):
    json.dump(data, open(KEY_FILE, "w"), indent=4)

def create_key(key, seconds=None):
    data = load_keys()
    if key in data:
        console.print(f"[yellow]Key {key} already exists![/]")
        return False
    if seconds is None:
        data[key] = {"expire": "LIFETIME"}
    else:
        data[key] = {"expire": time.time() + seconds}
    save_keys(data)
    return True

def revoke_key(key):
    data = load_keys()
    if key in data:
        data.pop(key)
        save_keys(data)
        return True
    return False

def validate_key(key):
    data = load_keys()
    if key not in data:
        return False, "Key not found."
    expire = data[key].get("expire")
    if expire == "LIFETIME":
        return True, None
    try:
        expire = float(expire)
    except Exception:
        return False, "Invalid expire format."
    if time.time() > expire:
        return False, "Key expired."
    return True, expire - time.time()

# =============================
# OWNER KEY
# =============================
def load_owner_key():
    for candidate in OWNER_FILE_CANDIDATES:
        if os.path.exists(candidate):
            try:
                return open(candidate, "r").read().strip()
            except Exception:
                continue
    return "Daev-OWNER"

OWNER_KEY = load_owner_key()

# =============================
# BANNER
# =============================
credit = """[bold cyan]
=== SPAM / AUTO-SHARE TOOL ===
Owner-protected Admin Panel & Key approval system
[/bold cyan]
"""

def show_banner():
    console.clear()
    console.print(credit)

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
        console.print(Panel("\n".join(menu_items), title="[bold green]MAIN MENU[/]", border_style="magenta", padding=(0,0), expand=True))
        choice = input("\nChoose: ").strip()
        if choice == "1":
            auto_login()
        elif choice == "2":
            add_cookie()
        elif choice == "3":
            remove_cookie()
        elif choice == "4" and is_owner:
            admin_panel()
        elif choice == "0":
            console.print("[bold]Bye[/]")
            sys.exit(0)
        else:
            console.print("[red]Invalid choice![/]")
            time.sleep(1)

# =============================
# ADMIN PANEL
# =============================
def parse_duration(duration_str):
    units = {'d': 24*3600, 'w': 7*24*3600, 'm': 30*24*3600, 'y': 365*24*3600}
    try:
        if duration_str[-1] in units:
            return int(duration_str[:-1]) * units[duration_str[-1]]
        return int(duration_str) * 24*3600
    except Exception:
        return None

def admin_panel():
    while True:
        os.system("clear")
        show_banner()
        console.print(
            Panel("\n".join([
                "[cyan]1.[/] Create Key",
                "[cyan]2.[/] Revoke Key",
                "[cyan]3.[/] View All Keys",
                "[cyan]0.[/] Back to Main Menu"
            ]), title="[bold green]ADMIN PANEL[/]", border_style="magenta", padding=(0,0), expand=True)
        )
        choice = input("\nChoose: ").strip()
        if choice == "1":
            key_name = input("Enter new key name (example: Daev-12345): ").strip()
            t = input("Lifetime? (y/n): ").strip().lower()
            if t == "y":
                if create_key(key_name):
                    console.print(f"[green]Lifetime key {key_name} created.[/]")
            else:
                duration = input("Enter duration (e.g., 1d, 2w, 3m, 1y): ").strip()
                seconds = parse_duration(duration)
                if seconds is None:
                    console.print("[red]Invalid duration![/]")
                elif create_key(key_name, seconds):
                    dt = datetime.datetime.fromtimestamp(time.time() + seconds)
                    console.print(f"[green]Key {key_name} created, expires at {dt}[/]")
            input("Press Enter to continue...")
        elif choice == "2":
            key_name = input("Enter key to revoke: ").strip()
            if revoke_key(key_name):
                console.print(f"[red]Key {key_name} revoked.[/]")
            else:
                console.print(f"[yellow]Key {key_name} not found.[/]")
            input("Press Enter to continue...")
        elif choice == "3":
            keys = load_keys()
            if not keys:
                console.print("[yellow]No keys found.[/]")
            else:
                console.print("\n[bold green]ALL KEYS[/]")
                for k,v in keys.items():
                    expire = v.get("expire")
                    if expire == "LIFETIME":
                        console.print(f"{k} : LIFETIME")
                    else:
                        try:
                            dt = datetime.datetime.fromtimestamp(float(expire))
                            console.print(f"{k} : Expires at {dt}")
                        except:
                            console.print(f"{k} : Invalid expire")
            input("\nPress Enter to continue...")
        elif choice == "0":
            break
        else:
            console.print("[red]Invalid choice![/]")
            time.sleep(1)

# =============================
# COOKIE MANAGEMENT
# =============================
def add_cookie():
    os.system('clear')
    name = input("[yellow]Enter account name:[/] ").strip()
    cookie = input("[yellow]Enter cookie:[/] ").strip()
    cookies = {}
    if os.path.exists(COOKIES_FILE):
        try:
            cookies = json.load(open(COOKIES_FILE,"r"))
        except Exception:
            cookies = {}
    cookies[name] = cookie
    json.dump(cookies, open(COOKIES_FILE,"w"), indent=4)
    console.print(f"[green]Cookie saved for {name}![/]")
    time.sleep(1)
    main_menu(is_owner=True)

def remove_cookie():
    if not os.path.exists(COOKIES_FILE):
        console.print("[red]No cookie to remove.[/]")
        time.sleep(1)
        return main_menu(is_owner=True)
    try:
        cookies = json.load(open(COOKIES_FILE,"r"))
    except Exception:
        cookies = {}
    if not cookies:
        console.print("[red]No cookie to remove.[/]")
        time.sleep(1)
        return main_menu(is_owner=True)
    console.print("[yellow]Saved accounts:[/]")
    for i, acc in enumerate(cookies.keys(), start=1):
        console.print(f"[cyan]{i}[/cyan]. {acc}")
    try:
        choice = int(input("\nChoose account to remove: ").strip()) - 1
        key = list(cookies.keys())[choice]
    except:
        console.print("[red]Invalid selection.[/]")
        time.sleep(1)
        return main_menu(is_owner=True)
    cookies.pop(key, None)
    json.dump(cookies, open(COOKIES_FILE,"w"), indent=4)
    console.print(f"[green]Removed cookie for {key}[/]")
    time.sleep(1)
    main_menu(is_owner=True)

def select_cookie():
    if not os.path.exists(COOKIES_FILE):
        console.print(Panel("[red]No saved cookies![/]", border_style="red"))
        time.sleep(1)
        return None
    try:
        cookies = json.load(open(COOKIES_FILE,"r"))
    except Exception:
        cookies = {}
    if not cookies:
        console.print(Panel("[red]No saved cookies![/]", border_style="red"))
        time.sleep(1)
        return None
    cookie_list = "\n".join(f"[cyan]{i}.[/] {name}" for i,name in enumerate(cookies.keys(), start=1))
    show_banner()
    console.print(Panel(cookie_list, title="[bold green]Select Account[/]", border_style="blue", expand=True))
    try:
        choice = int(input("\nChoose: ").strip()) - 1
        key = list(cookies.keys())[choice]
    except:
        console.print("[red]Invalid selection.[/]")
        time.sleep(1)
        return None
    return cookies[key], key

# =============================
# AUTO LOGIN / SHARE
# =============================
def auto_login():
    selected = select_cookie()
    if not selected:
        return main_menu()
    cookie, account_name = selected
    console.print(f"[yellow]Checking cookie for {account_name}...[/]")
    try:
        res = requests.get("https://business.facebook.com/business_locations",
                           headers={"user-agent":"Mozilla/5.0"}, cookies={"cookie":cookie})
        if res.status_code != 200:
            console.print(f"[red]Failed to connect, status {res.status_code}[/]")
            time.sleep(2)
            return main_menu()
        match = re.search(r"(EAAG\w+)", res.text)
        if match:
            token = match.group(1)
            try: open(TOKEN_FILE,"w").write(token)
            except: pass
            console.print(f"[green]Login success for {account_name}![/]")
            time.sleep(1)
            share_flow(cookie, token)
        else:
            console.print("[red]Cookie invalid or token not found![/]")
            time.sleep(2)
            main_menu()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error: {e}[/]")
        time.sleep(2)
        main_menu()

def share_flow(cookie, token):
    os.system('clear')
    show_banner()
    post_link = Prompt.ask("[magenta]Your Post Link[/]")
    try:
        limit = int(input("Share Limit: ").strip())
    except:
        limit = 1
    console.print('[blue]Post Share Started...[/]')
    success = 0
    failed = 0
    for _ in range(limit):
        try:
            res = ses.post(
                f"https://graph.facebook.com/me/feed?link={post_link}&published=0&access_token={token}",
                cookies={"cookie": cookie},
                timeout=30
            ).json()
        except Exception as e:
            res = {"error": str(e)}
        if isinstance(res, dict) and "id" in res:
            success += 1
            console.print(f"[green]Shared successfully: {res['id']}[/]")
        else:
            failed += 1
            console.print(f"[red]Failed: {res}[/]")
        time.sleep(0.2)
    console.print(f"[bold cyan]Success: {success} | Failed: {failed}[/]")
    input("</> Press Enter to return")
    main_menu(is_owner=True)

# =============================
# LOGIN FLOW
# =============================
def key_login():
    os.system("clear")
    show_banner()
    console.print(Panel("[cyan]Enter Approval Key[/]", border_style="magenta"))
    key = input("Key: ").strip()
    global OWNER_KEY
    OWNER_KEY = load_owner_key()
    if key == OWNER_KEY:
        console.print(Panel("[green]OWNER ACCESS GRANTED[/]", border_style="green"))
        time.sleep(1)
        return True
    valid, msg = validate_key(key)
    if not valid:
        console.print(Panel(f"[red]{msg}[/]", border_style="red"))
        time.sleep(2)
        sys.exit(1)
    if msg is None:
        console.print(Panel(f"[green]ACCESS GRANTED[/]\nRemaining Time: [yellow]LIFETIME[/]", border_style="green"))
    else:
        remaining = str(datetime.timedelta(seconds=int(msg)))
        console.print(Panel(f"[green]ACCESS GRANTED[/]\nRemaining Time: [yellow]{remaining}[/]", border_style="green"))
    time.sleep(1)
    return False

# =============================
# START
# =============================
if __name__ == '__main__':
    is_owner = key_login()
    main_menu(is_owner=is_owner)