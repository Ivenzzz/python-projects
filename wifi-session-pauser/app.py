import subprocess
import winreg
import time
import socket
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
ADAPTER_DISPLAY_NAME = "Intel(R) Wireless-AC 9560"  # Your exact adapter name (as seen in Device Manager)
MAC_LIST_FILE = "mac_list.txt"
TARGET_URL = "http://10.0.0.1/"  # Replace with your actual target page

def debug_list_adapters():
    base_key = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    print("[*] Listing all network adapters in registry...\n")
    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
        with winreg.OpenKey(hklm, base_key) as key:
            for i in range(1000):
                subkey_name = f"{i:04}"
                try:
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            name = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                            print(f"[{subkey_name}] {name}")
                        except FileNotFoundError:
                            continue
                except OSError:
                    break

def wait_for_router(address="10.0.0.1", port=80, timeout=30):
    print(f"[*] Waiting for {address} to become reachable...")
    for i in range(timeout):
        try:
            with socket.create_connection((address, port), timeout=2):
                print(f"[+] Successfully connected to {address}:{port}")
                return True
        except OSError:
            time.sleep(1)
    raise Exception(f"[-] Timeout: Cannot reach {address}:{port}")

# --- MAC Address Changer ---
def change_mac_windows(new_mac):
    subkey_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0001"

    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
            with winreg.OpenKey(hklm, subkey_path, 0, winreg.KEY_ALL_ACCESS) as subkey:
                winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                print(f"[+] MAC address set to {new_mac} in key 0001")
    except Exception as e:
        raise Exception(f"[-] Failed to modify registry key 0001: {e}")

def toggle_adapter(name):
    disable_cmd = f'PowerShell "Get-NetAdapter -Name \'{name}\' | Disable-NetAdapter -Confirm:$false"'
    enable_cmd = f'PowerShell "Get-NetAdapter -Name \'{name}\' | Enable-NetAdapter -Confirm:$false"'

    subprocess.run(disable_cmd, shell=True)
    time.sleep(2)
    subprocess.run(enable_cmd, shell=True)
    time.sleep(5)
    print(f"[+] Restarted adapter '{name}'")

# --- Browser Click Automation ---
def click_pause_button():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--allow-running-insecure-content")

    driver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)

    result = ""

    try:
        driver.get("http://10.0.0.1/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "btn-pause"))
            )
            driver.find_element(By.ID, "btn-pause").click()
            result = "Clicked PAUSE"
            print("[+] Clicked 'PAUSE' button.")
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "btn-resume"))
                )
                driver.find_element(By.ID, "btn-resume").click()
                result = "Clicked RESUME"
                print("[+] Clicked 'RESUME' button.")
            except:
                result = "No button found"
                print("[*] Neither 'PAUSE' nor 'RESUME' button found. Proceeding to next MAC.")

        time.sleep(2)

    except Exception as e:
        result = f"Browser error: {e}"
        print(f"[-] Error during browser interaction: {e}")
    finally:
        driver.quit()
    
    return result
                
# --- Main Process ---
def process_mac_list():
    try:
        with open(MAC_LIST_FILE, "r") as f:
            macs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] MAC list file '{MAC_LIST_FILE}' not found.")
        return

    while True:  # Infinite loop
        for mac in macs:
            if len(mac) != 12 or not all(c in "0123456789ABCDEFabcdef" for c in mac):
                result = "Invalid MAC format"
                print(f"[-] Skipping invalid MAC: {mac}")
            else:
                print(f"\n=== Processing MAC: {mac} ===")
                try:
                    change_mac_windows(mac)
                    toggle_adapter("Wi-Fi")
                    wait_for_router("10.0.0.1")
                    result = click_pause_button()
                except Exception as e:
                    result = f"Error: {e}"
                    print(f"[-] Failed for {mac}: {e}")
                time.sleep(2)

            # Append result immediately after processing each MAC
            with open("results.txt", "a") as results_file:
                results_file.write(f"{mac} = {result}\n")

if __name__ == "__main__":
    process_mac_list()
