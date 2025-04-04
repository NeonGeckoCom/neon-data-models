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

from typing import List, Optional
from datetime import datetime, timezone
from pydantic import Field
from neon_data_models.models.base import BaseModel
from neon_data_models.types import BotType


class ConnectedSubmind(BaseModel):
    service_name: str = Field(
        description="Name of the submind service (not its UID)")
    attached_cids: List[str] = Field(
        default=[], alias="cids",
        description="List of conversation IDs the submind is participating in")
    version: Optional[str] = Field(
        default=None,
        description="Version of chatbot-core the submind is using")
    supports_raw_conversation: bool = Field(
        default=False,
        description="True if the submind will handle all conversation shouts")
    last_ping: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="Last time the submind pinged the observer")

    bot_type: BotType = Field(
        deprecated=True, default="submind",
        description="Type of bot (always `submind` in this context)")


__all__ = [ConnectedSubmind.__name__]
