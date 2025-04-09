# models.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, time

@dataclass
class Location:
    name: str
    address: str
    notes: Optional[str] = None

@dataclass
class CastMember:
    name: str
    role: str
    call_time: time
    notes: Optional[str] = None

@dataclass
class CrewMember:
    name: str
    position: str
    department: str
    call_time: time
    notes: Optional[str] = None

@dataclass
class CallSheet:
    production_name: str
    production_date: datetime
    general_call_time: time
    logo_path: Optional[str] = None
    home_base: Optional[Location] = None
    filming_locations: List[Location] = field(default_factory=list)
    cast_members: List[CastMember] = field(default_factory=list)
    crew_members: List[CrewMember] = field(default_factory=list)
    notes: Optional[str] = None
    
    def add_filming_location(self, location: Location) -> bool:
        """Add a filming location if limit not reached"""
        if len(self.filming_locations) < 3:
            self.filming_locations.append(location)
            return True
        return False
        
    def add_cast_member(self, cast_member: CastMember) -> None:
        """Add a cast member to the call sheet"""
        self.cast_members.append(cast_member)
        
    def add_crew_member(self, crew_member: CrewMember) -> None:
        """Add a crew member to the call sheet"""
        self.crew_members.append(crew_member)
        
    def get_departments(self) -> List[str]:
        """Get a list of all departments"""
        departments = set(crew.department for crew in self.crew_members)
        return sorted(list(departments))
        
    def get_crew_by_department(self, department: str) -> List[CrewMember]:
        """Get all crew members in a specific department"""
        return [crew for crew in self.crew_members if crew.department == department]
