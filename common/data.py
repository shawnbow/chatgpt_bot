from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Reply:
    by: str = ''
    type: str = ''
    result: str = ''
    msg: str = ''
