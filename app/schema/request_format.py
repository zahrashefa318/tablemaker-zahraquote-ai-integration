from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TableRequest(BaseModel):
    rows: List[Dict[str, Any]]
    columns: Optional[List[str]] = None
    format: Optional[str] = "html"
