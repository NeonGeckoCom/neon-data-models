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

from typing import Optional, List, Union
from pydantic import ConfigDict, Field, field_validator, model_validator

from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.contexts import (SessionContext, KlatContext,
                                                   TimingContext, MQContext)
from neon_data_models.models.client.node import NodeData
from neon_data_models.models.user.database import NeonUserConfig


class MessageContext(BaseModel):
    model_config = ConfigDict(extra="allow")
    session: SessionContext = Field(description="Session Data",
                                              default=SessionContext())
    node_data: Optional[NodeData] = Field(description="Node Data", default=None)
    timing: TimingContext = Field(
        description="User Interaction Timing Information", 
        default=TimingContext())
    user_profiles: Optional[List[NeonUserConfig]] = (
        Field(description="List of relevant user profiles", default=None))
    klat_data: Optional[KlatContext] = Field(
        description="Klat context for Klat-generated messages", default=None)
    mq: Optional[MQContext] = Field(
        description="MQ context for messages traversing a RabbitMQ broker",
        default=None)

    username: str = "local"
    # TODO: Consider refactoring client/client_name into a single dict
    #  or merging with `node_data`
    client_name: str = "unknown"
    client: str = "unknown"
    source: Union[str, List[str]] = "unknown"
    destination: Union[str, List[str]] = Field(
        default=["skills"],
        description="List of destination modules expected to handle the message"
        )
    neon_should_respond: bool = True
    
    @field_validator('destination')
    def validate_destination(cls, v):
        if isinstance(v, str):
            return [v]
        return v
    
    @model_validator(mode='before')
    def validate_session_value(cls, data):
        if isinstance(data, dict) and data.get('session', {}) is None:
            data.pop('session')
        return data


class BaseMessage(BaseModel):
    msg_type: str
    data: dict
    context: MessageContext

    def as_messagebus_message(self) -> "Message": # type: ignore
        """
        Get a `Message` representation of this object.
        """
        try:
            from ovos_bus_client.message import Message
            if hasattr(self.data, 'model_dump'):
                data = self.data.model_dump()
            else:
                data = self.data
            return Message(self.msg_type, data, self.context.model_dump())
        except ImportError:
            raise RuntimeError("pip install ovos-bus-client to enable Message "
                               "deserialization.")
