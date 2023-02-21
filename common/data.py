from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Reply:
    by: str = ''
    type: str = ''
    result: str = ''
    msg: str = ''


@dataclass_json
@dataclass
class Context:
    user_id: str = ''
    user_name: str = ''
    platform: str = ''
    query: str = ''
    extra: Optional[Dict[str, Any]] = None
