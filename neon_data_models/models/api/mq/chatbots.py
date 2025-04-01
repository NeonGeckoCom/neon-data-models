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

from typing import Any, Dict, Literal, Optional, List, Union
from datetime import datetime, timezone
from pydantic import Field, model_validator

from neon_data_models.enum import SubmindStatus, CcaiState, CcaiControl
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
        """
        Override model_dump to include SIO fields for backwards compatibility
        """
        data = super().model_dump(**kwargs)
        
        # Add parameters for backwards-compat.
        data["bot"] = "1" if self.from_bot else "0"
        data["messageText"] = self.message_text
        data["nick"] = self.username
        return data


class ChatbotsMqSubmindResponse(KlatContext, MQContext):
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
    bot: Literal["0", "1"] = Field(default='0', alias='is_bot',
                                   description="1 if the shout is from a bot")
    prompt_id: Optional[str] = Field(
        default=None, alias="promptID",
        description="ID of the CCAI prompt associated with the shout")
    prompt_state: int = Field(
        deprecated=True, alias="conversation_state",
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
    bot_type: BotType = Field(default=None, deprecated=True,
                              description="Type of submind sending the shout")

    # service_name: Any = Field(default=None, deprecated=True)
    # context: Optional[dict] = Field(default=None, deprecated=True)
    # dom: Any = Field(default=None, deprecated=True,
    #                  description="Domain of this conversation")
    # omit_reply: bool = Field(
    #     default=True, deprecated=True,
    #     description="If true, the Proctor will ignore this message")
    # no_save: bool = Field(default=False, deprecated=True,
    #                       description="If true, this message will be ignored")
    # created_on: datetime = Field(default=datetime.now(timezone.utc),
    #                              description="Timestamp of response")
    # to_discussion: bool = Field(default=False, deprecated=True)

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if isinstance(values, dict):
            # Some references use different keys
            # TODO: prevent `None` values from being added here in place of missing
            #  keys
            if "nick" in values:
                values.setdefault("userID", values.get("nick"))

            if "shout" in values:
                values.setdefault("messageText", values.get("shout"))
            
            if values.get("responded_shout"):
                values.setdefault("repliedMessage",
                                   values.get("responded_shout"))

            if "time" in values:
                values.setdefault("timeCreated", values.get("time"))

            if "created_on" in values:
                values.setdefault("timeCreated", values.get("created_on"))

            if "sid" in values and values["sid"] is None:
                values.pop("sid")

            # # TODO: Mark as deprecated
            # if values.get('bot_type') in ('proctor', 'observer'):
            #     values['bot_type'] = 'facilitator'

        return values

    def model_dump(self, **kwargs):
        # For backwards-compat, include aliased keys in serialization
        by_alias = {}
        if 'by_alias' not in kwargs:
            by_alias = super().model_dump(by_alias=True, **kwargs)

        # TODO: Below are for SIO compat.
        by_alias['isAnnouncement'] = '1' if self.is_announcement else '0'
        by_alias['nick'] = self.user_id
        by_alias['responded_shout'] = self.replied_message
        by_alias['shout'] = self.message_text
        by_alias['time'] = self.time_created.timestamp()
        by_alias['promptState'] = self.prompt_state
        by_alias['created_on'] = self.time_created.timestamp()
        
        return {**super().model_dump(**kwargs), **by_alias}


class PromptCompletedContext(BaseModel):
    prompt: Optional[ChatbotsMqRequest] = None
    is_active: bool = False
    prompt_text: str
    available_subminds: List[str] = []
    state: Optional[int] = None
    participating_subminds: List[str] = []
    proposed_responses: Dict[str, str] = {}
    submind_opinions: Dict[str, str] = {}
    votes: Dict[str, str] = {}
    votes_per_submind: Dict[str, List[str]] = {}
    winner: str = ""


class ChatbotsMqSavePrompt(ChatbotsMqSubmindResponse):
    prompt_id: str = Field(
        default="",
        description="ID of the CCAI prompt associated with the shout")
    prompt_text: str = Field(default="")
    # created_on: str = Field(default="", deprecated=True,
    #                         description="String date of prompt creation.")
    context: PromptCompletedContext = Field(alias="conversation_context")

    # @model_validator(mode='before')
    # @classmethod
    # def validate_context(cls, values):
    #     # if "context" in values and not values["context"]:
    #     #     # Pop to replace with `conversation_context` or fail
    #     #     values.pop("context")

    #     # TODO: Patching invalid input for backwards-compat.
    #     if "created_on" in values and values["created_on"] is None:
    #         values.pop("created_on")
    #     return values
    
    def model_dump(self, **kwargs):
        return ChatbotsMqSubmindResponse.model_dump(self, **kwargs)


class ChatbotsMqNewPrompt(ChatbotsMqSubmindResponse):
    prompt_id: str = Field(
        description="ID of the CCAI prompt associated with the shout"
    )
    user_id: Optional[str] = Field(default=None)
    prompt_text: str = Field(default="")
    context: Optional[dict] = Field(default=None,
                                    alias="conversation_context")


    @model_validator(mode='before')
    @classmethod
    def validate_context(cls, values):
        values.setdefault("context", values.get("conversation_context"))
        if "prompt_text" in values:
            values["messageText"] = values.get("prompt_text")
        if "nick" in values:
            values.setdefault("user_id", values.get("nick"))
        return values
    
    def model_dump(self, **kwargs):
        return ChatbotsMqSubmindResponse.model_dump(self, **kwargs)


class ChatbotsMqResponse:
    """
    Type adapter for validating an arbitrary MQ message. This will always return
    an instance that extends `BaseMessage` and `MQContext`.
    """
    @classmethod
    def __new__(cls, *_, **kwargs) -> Union[ChatbotsMqSavePrompt,
                                            ChatbotsMqNewPrompt, 
                                            ChatbotsMqSubmindResponse]:
        message_text = kwargs.get("message_text") or kwargs.get("messageText") \
            or kwargs.get("shout")
        
        if message_text == CcaiControl.SAVE_PROMPT_RESULTS.value:
            return ChatbotsMqSavePrompt(**kwargs)
        elif message_text == CcaiControl.CREATE_PROMPT.value:
            return ChatbotsMqNewPrompt(**kwargs)
        else:
            return ChatbotsMqSubmindResponse(**kwargs)
    
    # ta = TypeAdapter(Union[ChatbotsMqSavePrompt, ChatbotsMqNewPrompt, 
    #                        ChatbotsMqSubmindResponse])


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


class ChatbotsMqSubmindConnection(MQContext):
    user_id: str = Field(description="User ID of the submind", alias="nick")
    time: datetime = Field(
        default= datetime.now(tz=timezone.utc),
        description="Timestamp when the submind last connected")
    cids: Optional[List[str]] = Field(
        default=None, description="List of conversation IDs the submind is in")
    supports_raw_shouts: bool = Field(
        default=False,
          description="True if the submind supports unprocessed conversations")


class ChatbotsMqSubmindDisconnection(MQContext):
    user_id: str = Field(description="User ID of the submind", alias="nick")


class ChatbotsMqSubmindInvitation(MQContext):
    cid: str = Field(description="Conversation ID to invite subminds to")
    requested_participants: List[str] = Field(
        description="List of submind User IDs to invite to the conversation")


class ChatbotsMqUpdateParticipatingSubminds(MQContext):
    cid: str = Field(description="Conversation ID to update")
    subminds_to_invite: List[str] = Field(
        default=[],
        description="List of submind User IDs to invite to the conversation")
    subminds_to_kick: List[str] = Field(
        default=[],
        description="List of submind User IDs to evict from the conversation")


class ChatbotsMqSubmindConversationBan(MQContext):
    user_id: str = Field(description="User ID of the submind", alias="nick")
    cid: str = Field(description="Conversation ID to (un)ban submind from")

    class Config:
        # For aliased fields, accept either the canonical name OR the alias
        populate_by_name = True


class ChatbotsMqSubmindGlobalBan(MQContext):
    user_id: str = Field(description="User ID of the submind", alias="nick")

    class Config:
        # For aliased fields, accept either the canonical name OR the alias
        populate_by_name = True


class ChatbotsMqSubmindResponseError(MQContext):
    message: Optional[str] = Field(default=None, alias="msg",
                                    description="Error message")


__all__ = [ChatbotsMqRequest.__name__, ChatbotsMqResponse.__name__,
           ChatbotsMqSubmindResponse.__name__, ChatbotsMqSavePrompt.__name__,
           ChatbotsMqNewPrompt.__name__, ChatbotsMqSubmindsState.__name__, 
           ChatbotsMqConfiguredPersonasRequest.__name__,
           ChatbotsMqConfiguredPersonasResponse.__name__,
           ChatbotsMqPromptsDataRequest.__name__,
           ChatbotsMqPromptsDataResponse.__name__,
           ChatbotsMqSubmindConnection.__name__,
           ChatbotsMqSubmindDisconnection.__name__,
           ChatbotsMqSubmindInvitation.__name__,
           ChatbotsMqUpdateParticipatingSubminds.__name__,
           ChatbotsMqSubmindConversationBan.__name__,
           ChatbotsMqSubmindGlobalBan.__name__,
           ChatbotsMqSubmindResponseError.__name__,]
