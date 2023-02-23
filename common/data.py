from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from collections import defaultdict
import arrow


@dataclass_json
@dataclass
class Context:
    user_id: str = ''
    user_name: str = ''
    group_id: str = ''
    group_name: str = ''
    is_group_chat: bool = False
    platform: str = ''
    extra: Optional[Dict[str, Any]] = None


@dataclass_json
@dataclass
class Query:
    msg_id: str = ''
    msg_type: str = ''
    msg: str = ''
    created_at: int = int(arrow.now().float_timestamp * 1000)


@dataclass_json
@dataclass
class Reply:
    by: str = ''
    type: str = ''
    result: str = ''
    msg: any = None
    created_at: int = int(arrow.now().float_timestamp * 1000)
