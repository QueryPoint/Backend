from enum import Enum

class WSStatus(str, Enum):
    idle = "idle"
    processing = "processing"
    blocked = "blocked"