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

from uuid import uuid4
from pydantic import Field
from typing import Optional, Dict
from neon_data_models.models.base import BaseModel


class NodeSoftware(BaseModel):
    operating_system: str = ""
    os_version: str = ""
    neon_packages: Optional[Dict[str, str]] = None


class NodeNetworking(BaseModel):
    local_ip: str = ""
    public_ip: str = ""
    mac_address: str = ""


class NodeLocation(BaseModel):
    def __init__(self, **kwargs):
        # Enables backwards-compat. with old coordinate values
        if lat := kwargs.pop("lat", None):
            kwargs.setdefault("latitude", lat)
        if lon := kwargs.pop("lon", None):
            kwargs.setdefault("longitude", lon)
        BaseModel.__init__(self, **kwargs)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    site_id: Optional[str] = None


class NodeData(BaseModel):
    device_id: str = Field(default_factory=lambda: str(uuid4()))
    device_name: str = ""
    device_description: str = ""
    platform: str = ""
    networking: NodeNetworking = NodeNetworking()
    software: NodeSoftware = NodeSoftware()
    location: NodeLocation = NodeLocation()


__all__ = [NodeSoftware.__name__, NodeNetworking.__name__,
           NodeLocation.__name__, NodeData.__name__]
