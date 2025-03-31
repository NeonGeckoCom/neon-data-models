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

from typing import Any, Dict, Literal, Optional, List
from datetime import datetime, timezone
from pydantic import Field, model_validator

from neon_data_models.enum import SubmindStatus, CcaiState
from neon_data_models.types import BotType
from neon_data_models.models.api.llm import LLMPersona
from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.contexts import KlatContext, MQContext


class ChatbotsMqRequest(KlatContext, MQContext):
    """
    Defines a request from Klat to the Chatbots service.
    """
    username: str = Field(description="Username (or 'nick') of the sender")
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
    def from_sio_message(cls, sio_message: dict) -> 'ChatbotsMqRequest':
        klat_context = KlatContext(**sio_message)
        mq_context = MQContext(**sio_message)
        return ChatbotsMqRequest(
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


class ChatbotsMqResponse(KlatContext, MQContext):
    """
    Defines a chatbot response to a request.
    """
    user_id: str = Field(alias='userID', 
                         description="Unique UID of the sender")
    username: Optional[str] = Field(default=None,
                                    alias="userDisplayName",
                                    description="Username of the sender")
    message_text: str = Field(alias="messageText",
                              description="Text content of the shout")
    sid: str = Field(default="", alias="messageID", description="Shout ID")
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
    is_announcement: bool = Field(
        default=False, alias="isAnnouncement",
        description="True if the shout is an announcement")
    time_created: datetime = Field(
        default= datetime.now(tz=timezone.utc), alias="timeCreated",
        description="Timestamp when the shout was created")
    source: str = Field(
        default="klat_observer",
        description="Name of the service originating the shout")
    
    bot_type: BotType = Field(default=None, deprecated=True)
    service_name: Any = Field(default=None, deprecated=True)
    conversation_state: Any = Field(default=None, deprecated=True)
    context: dict = Field(default=None, deprecated=True)
    omit_reply: Any = Field(default=None, deprecated=True)
    no_save: Any = Field(default=None, deprecated=True)

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if isinstance(values, dict):
            # Some references use different keys
            # TODO: prevent `None` values from being added here in place of missing
            #  keys
            values.setdefault("userID", values.get("nick"))

            values.setdefault("messageText", values.get("shout"))
            values.setdefault("repliedMessage", values.get("responded_shout"))
            values.setdefault("timeCreated", values.get("time"))

            if "sid" in values and values["sid"] is None:
                values.pop("sid")

            # # TODO: Mark as deprecated
            # if values.get('bot_type') in ('proctor', 'observer'):
            #     values['bot_type'] = 'facilitator'

        return values

    class Config:
        # For aliased fields, accept either the canonical name OR the alias
        populate_by_name = True

    def model_dump(self, **kwargs):
        # For backwards-compat, include aliased keys in serialization
        by_alias = {}
        if 'by_alias' not in kwargs:
            by_alias = super().model_dump(by_alias=True, **kwargs)
            by_alias['isAnnouncement'] = '1' if self.is_announcement else '0'
        
        return {**super().model_dump(**kwargs), **by_alias}


class PromptCompletedContext(BaseModel):
    prompt: ChatbotsMqRequest
    is_active: bool
    prompt_text: str
    available_subminds: List[str]
    state: int
    participating_subminds: List[str]
    proposed_responses: Dict[str, str]
    submind_opinions: Dict[str, str]
    votes: Dict[str, str]
    votes_per_submind: Dict[str, List[str]]
    winner: str = ""


class ChatbotsMqSavePrompt(ChatbotsMqResponse):
    prompt_id: str = Field(
        default="",
        description="ID of the CCAI prompt associated with the shout")
    prompt_text: str = Field(default="")
    created_on: str = Field(default="")
    # TODO: patched to resolve errors; consider intended behavior
    context: Optional[PromptCompletedContext] = Field(default=None)
    
    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        # If context is empty, remove it from the values so validation passes
        if "context" in values and not values["context"]:
            values.pop("context")
        return values

    def model_dump(self, **kwargs):
        return ChatbotsMqResponse.model_dump(self, **kwargs)


class ChatbotsMqNewPrompt(ChatbotsMqResponse):
    prompt_id: str = Field(
        description="ID of the CCAI prompt associated with the shout"
    )
    user_id: Optional[str] = Field(default=None)
    prompt_text: str = Field(default="")
    context: Optional[dict] = Field(default=None,
                                    alias="conversation_context")

    class Config:
        # For aliased fields, accept either the canonical name OR the alias
        populate_by_name = True

    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        values.setdefault("context", values.get("conversation_context"))
        values["messageText"] = values.get("prompt_text")
        return values
    
    def model_dump(self, **kwargs):
        return ChatbotsMqResponse.model_dump(self, **kwargs)


class ConnectedSubmind(MQContext):
    bot_type: BotType
    service_name: str
    cid: str = Field(deprecated=True)
    dom: str = Field(deprecated=True)
    conversation_state: CcaiState
    responded_shout: Optional[str] = Field(deprecated=True)
    shout: Literal["chatbot state"] = Field(deprecated=True)
    context: Dict[str, Any]  # TODO: Refactor?
    prompt_id: Optional[str] = Field(deprecated=True)
    omit_reply: bool = Field(deprecated=True)
    no_save: bool = Field(deprecated=True)
    attached_cids: List[str]
    supports_raw_shouts: bool  # TODO: Refactor?
    last_ping: datetime

    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        # TODO: Mark as deprecated
        # if values.get('bot_type') in ('proctor', 'observer'):
        #     values['bot_type'] = 'facilitator'
        if values.get('shout') == 'hello':
            values['shout'] = 'chatbot state'
        return values


class ChatbotsMqSubmindsState(MQContext):
    class SubmindState(BaseModel):
        submind_id: str = Field(description="Connected submind's user_id")
        status: SubmindStatus = Field(
            description="Subminds's status in a particular conversation")

    msg_type: Literal["subminds_state"] = Field(
        "subminds_state", description="Message type for SIO", deprecated=True)
    subminds_per_cid: Dict[str, List[SubmindState]]
    connected_subminds: Dict[str, ConnectedSubmind]
    cid_submind_bans: Dict[str, List[str]] = Field(
        description="List of banned submind `user_id`s per `cid`")
    banned_subminds: List[str] = Field(
        description="List of globally banned submind `user_id`s")


class ChatbotsMqConfiguredPersonasRequest(MQContext):
    service_name: str = Field(
        description="Name of the service to get personas for")
    user_id: Optional[str] = Field(
        default=None, description="Optional user_id making with the request.")


class ChatbotsMqConfiguredPersonasResponse(MQContext):
    update_time: datetime = Field(
        description="Time the personas were last checked")
    items: List[LLMPersona]
    context: dict = Field(deprecated=True)

    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        # Deprecated context handling for backwards-compat.
        if 'context' not in values and 'message_id' in values:
            values['context'] = {"mq": {"message_id": values['message_id']}}
        return values
        
    def model_dump(self, **kwargs):
        """
        Override model_dump to include 'persona_name' field for each item based 
        on its 'name' for backwards-compat.
        """
        data = super().model_dump(**kwargs)
        for item in data['items']:
            item['persona_name'] = item['name']
        return data

    @classmethod
    def from_persona_request(cls, data: dict,
                               request: ChatbotsMqConfiguredPersonasRequest):
        data["items"] = [item for item in data["items"]
                         if request.service_name in item["supported_llms"]]
        return cls(**data, message_id=request.message_id,
                   routing_key=request.routing_key)


class ChatbotsMqPromptsDataRequest(MQContext):
    """
    Convenience class. The message payload here is just `MQContext`.
    """


class ChatbotsMqPromptsDataResponse(MQContext):
    records: List[str] = Field(description="List of configured prompts")
    context: dict = Field(deprecated=True)

    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        # Deprecated context handling for backwards-compat.
        if 'context' not in values and 'message_id' in values:
            values['context'] = {"mq": {"message_id": values['message_id']}}
        return values
    
    @classmethod
    def from_prompt_data_request(cls, data: dict,
                               request: ChatbotsMqPromptsDataRequest):
        return cls(**data, message_id=request.message_id,
                   routing_key=request.routing_key)


__all__ = [ChatbotsMqRequest.__name__, ChatbotsMqResponse.__name__,
           ChatbotsMqSavePrompt.__name__, ChatbotsMqNewPrompt.__name__,
           ChatbotsMqSubmindsState.__name__, 
           ChatbotsMqConfiguredPersonasRequest.__name__,
           ChatbotsMqConfiguredPersonasResponse.__name__,
           ChatbotsMqPromptsDataRequest.__name__,
           ChatbotsMqPromptsDataResponse.__name__]
