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

from typing import Literal, Optional, List
from datetime import datetime, timezone
from pydantic import Field, model_validator

from neon_data_models.models.base.contexts import KlatContext, MQContext


class ChatbotRequest(KlatContext, MQContext):
    """
    Defines a request from Klat to the Chatbots service.
    """
    username: str = Field(description="Username of the sender")
    cid: str = Field(description="Conversation ID associated with the shout")
    message_text: str = Field(description="Text content of the shout")
    from_bot: bool = Field(
        default=False,
        description="True if the shout is from a bot, False if from a user")
    prompt_id: Optional[str] = Field(
        default=None,
        description="ID of the CCAI prompt associated with the shout")
    prompt_state: Optional[int] = Field(
        default=None, deprecated=True,
        description="State of the CCAI conversation associated with the shout")
    time_created: datetime = Field(
        default= datetime.now(tz=timezone.utc),
        description="Timestamp when the shout was created")
    requested_participants: Optional[List[str]] = Field(
        default=None, 
        description="List of CCAI participants requested to handle the shout")
    recipient: Optional[str] = Field(
        default=None, description="Explicitly defined recipient of the shout. ")
    bound_service: Optional[str] = Field(
        default=None, description="Service bound to the conversation")
    
    @classmethod
    def from_sio_message(cls, sio_message: dict) -> 'ChatbotRequest':
        klat_context = KlatContext(**sio_message)
        mq_context = MQContext(**sio_message)
        return ChatbotRequest(
            **klat_context.model_dump(exclude_none=True),
            **mq_context.model_dump(exclude_none=True),
            username=sio_message.get("userDisplayName") or \
                sio_message.get("userID"),
            message_text=sio_message["messageText"],
            from_bot=sio_message.get("bot") == 1,
            prompt_id = sio_message.get("promptID"),
            prompt_state=sio_message.get("promptState"),
            time_created=sio_message["timeCreated"],
            recipient=sio_message.get("recipient"),
            bound_service=sio_message.get("bound_service"),
        )
    
    def model_dump(self, **kwargs):
        """Override model_dump to include 'bot' field for backwards compatibility"""
        data = super().model_dump(**kwargs)
        # Add the 'bot' parameter as '1' or '0' string for backwards compatibility
        data["bot"] = "1" if self.from_bot else "0"
        # Add parameters for backwards-compat.
        data["messageText"] = self.message_text
        data["nick"] = self.username
        return data


class ChatbotResponse(KlatContext, MQContext):
    user_id: str = Field(alias='userID', 
                         description="Unique UID of the sender")
    username: Optional[str] = Field(default=None,
                                    alias="userDisplayName",
                                    description="Username of the sender")
    message_text: str = Field(alias="messageText",
                              description="Text content of the shout")
    sid: Optional[str] = Field(default=None, alias="messageID",
                               description="Shout ID")
    replied_message: Optional[str] = Field(
        default=None, alias="repliedMessage",
        description="ID of the shout being replied to")
    bot: Literal["0", "1"] = Field(default='0',
                                   description="1 if the shout is from a bot")
    prompt_id: Optional[str] = Field(
        default=None, alias="promptID",
        description="ID of the CCAI prompt associated with the shout")
    prompt_state: Optional[int] = Field(
        default=None, deprecated=True, alias="promptState",
        description="State of the CCAI conversation associated with the shout")
    is_announcement: Literal["0", "1"] = Field(
        default='0', alias="isAnnouncement",
        description="`1` if the shout is an announcement")
    time_created: datetime = Field(
        default= datetime.now(tz=timezone.utc), alias="timeCreated",
        description="Timestamp when the shout was created")
    source: str = Field(
        default="klat_observer",
        description="Name of the service originating the shout")
    
    def model_dump(self, **kwargs):
        """Override model_dump to use by_alias=True by default"""
        # Set by_alias=True by default if not specified
        if 'by_alias' not in kwargs:
            kwargs['by_alias'] = True
        return super().model_dump(**kwargs)


class ChatbotSavePrompt(ChatbotResponse):
    prompt_id: str = Field(
        default="",
        description="ID of the CCAI prompt associated with the shout")
    prompt_text: str = Field(default="")
    created_on: str = Field(default="")
    
    def model_dump(self, **kwargs):
        return ChatbotResponse.model_dump(self, **kwargs)


class ChatbotNewPrompt(ChatbotResponse):
    user_id = None
    prompt_text: str = Field(default="")
    context: Optional[dict] = None


    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        values.setdefault("context", values.get("conversation_context"))
        values["messageText"] = values.get("prompt_text")
        return values
    
    def model_dump(self, **kwargs):
        return ChatbotResponse.model_dump(self, **kwargs)


__all__ = [ChatbotRequest.__name__, ChatbotResponse.__name__,
           ChatbotSavePrompt.__name__, ChatbotNewPrompt.__name__]
