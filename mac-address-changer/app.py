# Iven Loro
# @ June 7, 2025

import sys
import subprocess
import winreg
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)

class MacChangerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAC Address Changer")
        self.setGeometry(100, 100, 300, 200)

        self.label = QLabel("New MAC Address (12 hex digits):")
        self.mac_input = QLineEdit()

        self.apply_button = QPushButton("Change MAC")
        self.apply_button.clicked.connect(self.change_mac)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.mac_input)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

    def change_mac(self):
        new_mac = self.mac_input.text().strip()
        adapter_name = "Wi-Fi"  # Make sure this exactly matches the system
        if len(new_mac) != 12 or not all(c in "0123456789ABCDEFabcdef" for c in new_mac):
            QMessageBox.critical(self, "Error", "Invalid MAC format.")
            return

        try:
            self.modify_registry(new_mac)
            self.toggle_adapter(adapter_name)
            QMessageBox.information(self, "Success", "MAC address changed.")
        except Exception as e:
            QMessageBox.critical(self, "Failed", str(e))

    def modify_registry(self, new_mac):
        base_key = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
            with winreg.OpenKey(hklm, base_key) as key:
                for i in range(1000):
                    subkey_name = f"{i:04}"
                    try:
                        with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                                print(f"[{subkey_name}] DriverDesc: {name}")
                                # Match your adapter name loosely, adjust as needed
                                if "wireless" in name.lower() and "9560" in name:
                                    print("Found target adapter, setting MAC...")
                                    winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                                    return
                            except FileNotFoundError:
                                continue
                    except OSError:
                        break
        raise Exception("Wireless adapter not found in registry.")

    def toggle_adapter(self, name):
        disable_cmd = f'PowerShell "Get-NetAdapter -Name \'{name}\' | Disable-NetAdapter -Confirm:$false"'
        enable_cmd = f'PowerShell "Get-NetAdapter -Name \'{name}\' | Enable-NetAdapter -Confirm:$false"'

        disable = subprocess.run(disable_cmd, shell=True)
        enable = subprocess.run(enable_cmd, shell=True)

        if disable.returncode != 0 or enable.returncode != 0:
            raise Exception("Failed to toggle adapter.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MacChangerApp()
    win.show()
    sys.exit(app.exec())
