# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2024 Neongecko.com Inc.
# BSD-3
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from time import time
from typing import Dict, Any, List, Literal, Optional
from uuid import uuid4
from neon_data_models.models.base import BaseModel
from pydantic import Field
from datetime import date

from neon_data_models.enum import AccessRoles


class _UserConfig(BaseModel):
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    preferred_name: str = ""
    dob: Optional[date] = None
    email: str = ""
    avatar_url: str = Field(default="",
                            description="Fully-qualified URI of a user avatar. "
                                        "(i.e. `https://example.com/avatar.jpg")
    about: str = ""
    phone: str = ""


class _LanguageConfig(BaseModel):
    input_languages: List[str] = ["en-us"]
    output_languages: List[str] = ["en-us"]


class _UnitsConfig(BaseModel):
    time: Literal[12, 24] = 12
    date: Literal["MDY", "YMD", "YDM", "DMY"] = "MDY"
    measure: Literal["imperial", "metric"] = "imperial"


class _ResponseConfig(BaseModel):
    hesitation: bool = False
    limit_dialog: bool = False
    tts_gender: Literal["male", "female"] = "female"
    tts_speed_multiplier: float = 1.0


class _LocationConfig(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: Optional[str] = None
    timezone: Optional[str] = None


class _PrivacyConfig(BaseModel):
    save_text: bool = True
    save_audio: bool = False


class NeonUserConfig(BaseModel):
    """
    Defines user configuration used in Neon Core.
    """
    skills: Dict[str, Dict[str, Any]] = {}
    user: _UserConfig = _UserConfig()
    # Former `speech` schema is replaced by `language` which is a more general
    # format.
    language: _LanguageConfig = _LanguageConfig()
    units: _UnitsConfig = _UnitsConfig()
    # Former `location` schema is replaced here with a minimal spec from which
    # the remaining values may be calculated
    location: _LocationConfig = _LocationConfig()
    response_mode: _ResponseConfig = _ResponseConfig()
    privacy: _PrivacyConfig = _PrivacyConfig()


class KlatConfig(BaseModel):
    """
    Defines user configuration used in PyKlatChat.
    """
    is_tmp: bool = True
    preferences: Dict[str, Any] = {}


class BrainForgeConfig(BaseModel):
    """
    Defines configuration used in BrainForge LLM applications.
    """
    inference_access: Dict[str, Dict[str, List[str]]] = {}


class PermissionsConfig(BaseModel):
    """
    Defines roles for supported projects/service families.
    """
    klat: AccessRoles = AccessRoles.NONE
    core: AccessRoles = AccessRoles.NONE
    diana: AccessRoles = AccessRoles.NONE
    node: AccessRoles = AccessRoles.NONE
    hub: AccessRoles = AccessRoles.NONE
    llm: AccessRoles = AccessRoles.NONE

    class Config:
        use_enum_values = True


class TokenConfig(BaseModel):
    username: str
    client_id: str
    permissions: Dict[str, bool]
    refresh_token: str
    expiration: int
    refresh_expiration: int
    token_name: str
    creation_timestamp: int
    last_refresh_timestamp: int
    access_token: Optional[str] = None


class User(BaseModel):
    username: str
    password_hash: Optional[str] = None
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    created_timestamp: int = Field(default_factory=lambda: round(time()))
    neon: NeonUserConfig = NeonUserConfig()
    klat: KlatConfig = KlatConfig()
    llm: BrainForgeConfig = BrainForgeConfig()
    permissions: PermissionsConfig = PermissionsConfig()
    tokens: Optional[List[TokenConfig]] = []

    def __eq__(self, other):
        return self.model_dump() == other.model_dump()


__all__ = [NeonUserConfig.__name__, KlatConfig.__name__,
           BrainForgeConfig.__name__, PermissionsConfig.__name__,
           TokenConfig.__name__, User.__name__]
