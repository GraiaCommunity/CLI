from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import tomli
from graia.saya import Channel, Saya

if TYPE_CHECKING:
    from graia.ariadne.connection._info import U_Info


def require_modules(
    saya: Saya, modules: List[str], env: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[Channel, Any]]:
    channels: Dict[str, Union[Channel, Any]] = {}
    env = env or {}
    for mod in sorted(modules):  # dictionary order to make sure shallow modules will be required first
        channels[mod] = saya.require(mod, env.get(mod, None))
    return channels


def extract_modules_from_toml(path: str) -> List[str]:
    data = tomli.loads(path.read_text(encoding="utf-8"))
    return data.setdefault("tool", {}).setdefault("graiax", {}).setdefault("load", [])
