# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
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
from typing import Optional, List, Literal
from uuid import uuid4

from pydantic import Field
from neon_data_models.enum import AccessRoles
from neon_data_models.models.base import BaseModel


class JWT(BaseModel):
    iss: Optional[str] = Field(None, validate_default=True,
                               description="Token issuer")
    sub: Optional[str] = Field(None, validate_default=True,
                               description="Unique token subject, ie a user ID")
    exp: int = Field(description="Expiration time in epoch seconds")
    iat: int = Field(description="Token creation time in epoch seconds")
    jti: str = Field(description="Unique token identifier",
                     default_factory=lambda: str(uuid4()))

    client_id: str = Field(description="Client identifier")
    roles: List[str] = Field(description="List of roles, "
                                         "formatted as `<name> <AccessRole>`. "
                                         "See PermissionsConfig for role names")


class HanaToken(JWT):
    def __init__(self, **kwargs):
        from neon_data_models.models.user import PermissionsConfig
        permissions = kwargs.get("permissions")
        if permissions and isinstance(permissions, PermissionsConfig):
            kwargs["roles"] = permissions.to_roles()
        elif permissions and isinstance(permissions, dict):
            core_permissions = AccessRoles.GUEST if \
                permissions.get("assist") else AccessRoles.NONE
            diana_permissions = AccessRoles.GUEST if \
                permissions.get("backend") else AccessRoles.NONE
            node_permissions = AccessRoles.USER if \
                permissions.get("node") else AccessRoles.NONE
            kwargs["roles"] = [f"core {core_permissions.value}",
                               f"diana {diana_permissions.value}",
                               f"node {node_permissions.value}"]
        if kwargs.get("expire") and isinstance(kwargs["expire"], float):
            kwargs["expire"] = round(kwargs["expire"])
        BaseModel.__init__(self, **kwargs)

    # Private parameters
    token_name: str = Field(default="",
                            description="Friendly name to identify this token.")
    creation_timestamp: int = Field(default_factory=lambda: int(time()),
                                    description="Timestamp of initial token "
                                                "creation (not counting "
                                                "refreshes).")
    last_refresh_timestamp: Optional[int] = Field(default=None,
                                                  description="Timestamp of "
                                                              "most recent "
                                                              "refresh.")
    purpose: Literal["access", "refresh"] = "access"


__all__ = [JWT.__name__, HanaToken.__name__]
