from os import environ

from pydantic import ConfigDict, BaseModel as _BaseModel


class BaseModel(_BaseModel):
    _allow_extra = "allow" if environ.get("NEON_DATA_MODELS_ALLOW_EXTRA",
                                          False) else "ignore"
    model_config = ConfigDict(extra=_allow_extra)
