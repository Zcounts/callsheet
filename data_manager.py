# data_manager.py
import json
import os
from datetime import datetime, time
from typing import Dict, Any, Optional, List

from models import CallSheet, Location, CastMember, CrewMember

def time_to_str(t: time) -> str:
    """Convert time object to string for JSON serialization"""
    return t.strftime("%H:%M")

def str_to_time(t_str: str) -> time:
    """Convert string to time object for JSON deserialization"""
    hours, minutes = map(int, t_str.split(":"))
    return time(hour=hours, minute=minutes)

def datetime_to_str(dt: datetime) -> str:
    """Convert datetime object to string for JSON serialization"""
    return dt.strftime("%Y-%m-%d")

def str_to_datetime(dt_str: str) -> datetime:
    """Convert string to datetime object for JSON deserialization"""
    return datetime.strptime(dt_str, "%Y-%m-%d")

def save_call_sheet(call_sheet: CallSheet, filename: str) -> bool:
    """Save a call sheet to a JSON file"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Convert call sheet to dictionary
        call_sheet_dict = {
            "production_name": call_sheet.production_name,
            "production_date": datetime_to_str(call_sheet.production_date),
            "general_call_time": time_to_str(call_sheet.general_call_time),
            "logo_path": call_sheet.logo_path,
            "home_base": {
                "name": call_sheet.home_base.name,
                "address": call_sheet.home_base.address,
                "notes": call_sheet.home_base.notes
            } if call_sheet.home_base else None,
            "filming_locations": [
                {
                    "name": loc.name,
                    "address": loc.address,
                    "notes": loc.notes
                } for loc in call_sheet.filming_locations
            ],
            "cast_members": [
                {
                    "name": cast.name,
                    "role": cast.role,
                    "call_time": time_to_str(cast.call_time),
                    "notes": cast.notes
                } for cast in call_sheet.cast_members
            ],
            "crew_members": [
                {
                    "name": crew.name,
                    "position": crew.position,
                    "department": crew.department,
                    "call_time": time_to_str(crew.call_time),
                    "notes": crew.notes
                } for crew in call_sheet.crew_members
            ],
            "notes": call_sheet.notes
        }
        
        # Save to JSON file
        with open(os.path.join("data", filename), "w") as f:
            json.dump(call_sheet_dict, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error saving call sheet: {e}")
        return False

def load_call_sheet(filename: str) -> Optional[CallSheet]:
    """Load a call sheet from a JSON file"""
    try:
        # Load from JSON file
        with open(os.path.join("data", filename), "r") as f:
            call_sheet_dict = json.load(f)
        
        # Create call sheet object
        call_sheet = CallSheet(
            production_name=call_sheet_dict["production_name"],
            production_date=str_to_datetime(call_sheet_dict["production_date"]),
            general_call_time=str_to_time(call_sheet_dict["general_call_time"]),
            logo_path=call_sheet_dict.get("logo_path"),
            notes=call_sheet_dict.get("notes")
        )
        
        # Add home base if exists
        if call_sheet_dict.get("home_base"):
            call_sheet.home_base = Location(
                name=call_sheet_dict["home_base"]["name"],
                address=call_sheet_dict["home_base"]["address"],
                notes=call_sheet_dict["home_base"].get("notes")
            )
        
        # Add filming locations
        for loc_dict in call_sheet_dict.get("filming_locations", []):
            call_sheet.add_filming_location(Location(
                name=loc_dict["name"],
                address=loc_dict["address"],
                notes=loc_dict.get("notes")
            ))
        
        # Add cast members
        for cast_dict in call_sheet_dict.get("cast_members", []):
            call_sheet.add_cast_member(CastMember(
                name=cast_dict["name"],
                role=cast_dict["role"],
                call_time=str_to_time(cast_dict["call_time"]),
                notes=cast_dict.get("notes")
            ))
        
        # Add crew members
        for crew_dict in call_sheet_dict.get("crew_members", []):
            call_sheet.add_crew_member(CrewMember(
                name=crew_dict["name"],
                position=crew_dict["position"],
                department=crew_dict["department"],
                call_time=str_to_time(crew_dict["call_time"]),
                notes=crew_dict.get("notes")
            ))
        
        return call_sheet
    except Exception as e:
        print(f"Error loading call sheet: {e}")
        return None

def list_saved_call_sheets() -> List[str]:
    """List all saved call sheets"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # List all JSON files in data directory
        return [f for f in os.listdir("data") if f.endswith(".json")]
    except Exception as e:
        print(f"Error listing call sheets: {e}")
        return []
