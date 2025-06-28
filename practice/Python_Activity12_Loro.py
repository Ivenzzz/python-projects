from abc import ABC, abstractmethod
from datetime import datetime


# ----------------------
# 1. Citizen Class (Enhanced Encapsulation)
# ----------------------
class Citizen:
    def __init__(self, id_number, clearance_level, region_code):
        self.__id_number = id_number
        self.__clearance_level = clearance_level
        self.__region_code = region_code

    @property
    def masked_id(self):
        return f"CITZ-XXX{str(self.__id_number)[-2:]}"

    @property
    def clearance(self):
        return self.__clearance_level

    @clearance.setter
    def clearance(self, value_password_tuple):
        value, password = value_password_tuple
        if value >= 9 and password != "Override2025":
            raise PermissionError("Password required to set clearance to Level 9 or 10.")
        if not (1 <= value <= 10):
            raise ValueError("Clearance level must be between 1 and 10.")
        self.__clearance_level = value
        print(f"[INFO] Clearance updated to Level {value}.")

    @property
    def region_code(self):
        return self.__region_code


# ----------------------
# 2. AuthorizedPersonnel Class
# ----------------------
class AuthorizedPersonnel(Citizen):
    def __init__(self, id_number, clearance_level, region_code, role):
        super().__init__(id_number, clearance_level, region_code)
        self.role = role


# ----------------------
# 3. RegionalCommander Class
# ----------------------
class RegionalCommander(AuthorizedPersonnel):
    def grant_emergency_access(self, zone):
        self._log_emergency(zone)
        print(f"🚨 Emergency access granted to {zone.__class__.__name__} by {self.role}.")

    def _log_emergency(self, zone):
        print(f"🔐 [LOG] Emergency override used in {zone.__class__.__name__} by Commander {self.masked_id}.")


# ----------------------
# 4. SecureZone Abstract Class
# ----------------------
class SecureZone(ABC):
    def __init__(self, protocol_code):
        self.protocol_code = protocol_code

    @abstractmethod
    def evaluate(self, citizen, current_time):
        pass


# ----------------------
# 5. Zone Implementations
# ----------------------
class ParkZone(SecureZone):
    def evaluate(self, citizen, current_time):
        if citizen.clearance >= 3:
            print("✅ ParkZone Access Granted")
        else:
            print("❌ ParkZone Access Denied")


class LabZone(SecureZone):
    def evaluate(self, citizen, current_time):
        if (citizen.clearance >= 6 and isinstance(citizen, AuthorizedPersonnel)
                and citizen.role in ["Scientist", "Engineer"]
                and 6 <= current_time.hour < 18):
            print("✅ LabZone Access Granted")
        else:
            print("❌ LabZone Access Denied")


class BunkerZone(SecureZone):
    def evaluate(self, citizen, current_time):
        if (citizen.clearance >= 9 and isinstance(citizen, AuthorizedPersonnel)
                and citizen.role == "Guard" and citizen.region_code == "Delta"):
            print("✅ BunkerZone Access Granted")
        else:
            print("❌ BunkerZone Access Denied")


# ----------------------
# 6. Main Program
# ----------------------
if __name__ == "__main__":
    now = datetime.now()

    citizens = [
        Citizen("C00112233", 2, "Alpha"),
        AuthorizedPersonnel("B44556677", 6, "Beta", "Scientist"),
        AuthorizedPersonnel("D88990011", 10, "Delta", "Guard"),
        RegionalCommander("Z99999999", 10, "Gamma", "Commander")
    ]

    zones = [ParkZone("PZ-101"), LabZone("LZ-202"), BunkerZone("BZ-303")]

    for person in citizens:
        print(f"\n🔍 Checking Access for {person.__class__.__name__} ({person.masked_id})")
        for zone in zones:
            try:
                zone.evaluate(person, now)
            except Exception as e:
                print(f"Error during evaluation: {e}")
            if isinstance(person, RegionalCommander):
                person.grant_emergency_access(zone)
