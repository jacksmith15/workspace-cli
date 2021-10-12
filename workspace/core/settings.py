from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Settings:
    filename: str = "workspace.json"

    @classmethod
    def from_env(cls):
        env_prefix = "WORKSPACE_"
        params = {
            name: os.environ[env_prefix + name.upper()]
            for name, field in cls.__dataclass_fields__.items()
            if env_prefix + name.upper() in os.environ and field.init
        }
        return cls(**params)


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings.from_env()
