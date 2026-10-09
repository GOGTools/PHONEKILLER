import os
import subprocess
import sys
import time
from colorama import init, Fore, Style

# Initialize colorama for cross-platform ANSI colors
init(autoreset=True)

SILVER = Fore.LIGHTBLACK_EX + Style.BRIGHT

def get_adb_path():
    """Locates adb.exe whether running as a script or embedded inside a PyInstaller .exe"""
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle (.exe)
        base_path = sys._MEIPASS
    else:
        # Running normally as a script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    adb_path = os.path.join(base_path, "adb.exe")
    
    # Fallback to system path if local adb.exe isn't found
    if not os.path.exists(adb_path):
        return "adb"
    return adb_path

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{SILVER}██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗    ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗ 
{SILVER}██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝    ██║  ██║██║██║     ██║     ██╔════╝██╔══██╗
{SILVER}██████╔╝███████║██║   ██║██╔██╗ ██║█████╗      ███████║██║██║     ██║     █████╗  ██████╔╝
{SILVER}██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝      ██╔══██║██║██║     ██║     ██╔══╝  ██╔══██╗
{SILVER}██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗    ██║  ██║██║███████╗███████╗███████╗██║  ██║
{SILVER}╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝    ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
    """
    print(banner)
    print(f"{SILVER}{'='*94}")
    print(f"{SILVER}                      AUTOMATED DEVICE WIPING & TESTING STATION")
    print(f"{SILVER}{'='*94}\n")

def get_connected_devices(adb_bin):
    try:
        output = subprocess.check_output([adb_bin, "devices"]).decode("utf-8")
        lines = output.strip().split("\n")[1:]
        devices = []
        for line in lines:
            if line.strip():
                device_info = line.split()
                devices.append(device_info[0])
        return devices
    except Exception:
        print(f"{Fore.RED}[!] Error: Failed to execute ADB binary at: {adb_bin}")
        return []

def execute_wipe(adb_bin, device_id):
    print(f"\n{Fore.YELLOW}[*] Preparing to wipe device {device_id}...")
    print(f"{Fore.RED}[WARNING] This will completely delete all data on the target device.")
    confirm = input(f"{Fore.YELLOW}Are you absolutely sure you want to proceed? (yes/no): ")
    
    if confirm.lower() == "yes":
        print(f"{Fore.CYAN}[*] Sending master clear intent broadcast...")
        cmd = [adb_bin, "-s", device_id, "shell", "am", "broadcast", "-a", "android.intent.action.MASTER_CLEAR", "-n", "android/com.android.server.MasterClearReceiver"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "result=0" in result.stdout or "Broadcast completed" in result.stdout:
                print(f"{Fore.GREEN}[+] Reset signal accepted successfully!")
            else:
                print(f"{Fore.RED}[!] Direct broadcast blocked. Attempting Recovery Mode boot...")
                subprocess.run([adb_bin, "-s", device_id, "reboot", "recovery"])
                print(f"{Fore.GREEN}[+] Device rebooted into Recovery.")
        except Exception as e:
            print(f"{Fore.RED}[!] Operational failure: {e}")
    else:
        print(f"{Fore.GREEN}[+] Operation aborted safely.")

def get_password_sim(device_id):
    print(f"\n{Fore.CYAN}[*] Reading security configuration locks for {device_id}...")
    time.sleep(1.5)
    print(f"{Fore.GREEN}[+] Device Connection Status: AUTHORIZED")
    print(f"{Fore.YELLOW}[i] Modern Android devices encrypt passwords inside secure hardware keystores.")
    print(f"{Fore.YELLOW}[i] Direct plaintext password retrieval is blocked by the filesystem encryption layer.")

def main():
    adb_bin = get_adb_path()
    while True:
        print_header()
        devices = get_connected_devices(adb_bin)
        
        if not devices:
            print(f"{Fore.YELLOW}[i] No devices detected. Connect an Android phone via USB with USB Debugging enabled.")
            print(f"{Fore.WHITE}Press Enter to refresh or type 'exit' to quit.")
            choice = input("> ")
            if choice.lower() == 'exit':
                break
            continue
            
        print(f"{Fore.WHITE}Found Connected Devices:")
        for idx, device in enumerate(devices, 1):
            print(f" {Fore.GREEN}{idx}. Device ID: {device}")
        print("")
        
        user_input = input(f"{Fore.WHITE}Select a device (e.g., 'device 1') or 'exit' to quit: ").strip().lower()
        
        if user_input == 'exit':
            break
            
        if user_input.startswith("device "):
            try:
                num = int(user_input.split()[1]) - 1
                if 0 <= num < len(devices):
                    selected_device = devices[num]
                    
                    print_header()
                    print(f"{Fore.GREEN}Selected Target: {selected_device}")
                    print(f"{Fore.WHITE}Available Sub-Options:")
                    print(f" {Fore.WHITE}1. delete all data")
                    print(f" {Fore.WHITE}2. give password")
                    print(f" {Fore.WHITE}3. Back to main menu")
                    
                    option = input(f"\n{Fore.WHITE}Choose an action (1-3): ").strip()
                    if option == "1" or "delete" in option.lower():
                        execute_wipe(adb_bin, selected_device)
                    elif option == "2" or "password" in option.lower():
                        get_password_sim(selected_device)
                    else:
                        continue
                        
                    input(f"\n{Fore.WHITE}Press Enter to return to the main menu...")
                else:
                    print(f"{Fore.RED}[!] Invalid device selection index.")
                    time.sleep(1.5)
            except (IndexError, ValueError):
                print(f"{Fore.RED}[!] Selection format incorrect. Use syntax like 'device 1'.")
                time.sleep(1.5)

if __name__ == "__main__":
    main()
