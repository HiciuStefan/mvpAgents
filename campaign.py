from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class Campaign:
    name: str
    sostac_data: Dict
    strategy: Optional[str] = None
    deliverables: Optional[Dict] = None
    influencers: Optional[List] = None
    approved: bool = False
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()