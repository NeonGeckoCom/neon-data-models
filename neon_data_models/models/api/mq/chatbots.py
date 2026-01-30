# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2026 Neongecko.com Inc.
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
from pydantic import Field, model_validator, AliasChoices

from neon_data_models.enum import SubmindStatus, CcaiState, CcaiControl
from neon_data_models.types import BotType
from neon_data_models.models.api.llm import LLMPersona
from neon_data_models.models.api.chatbots import ConnectedSubmind
from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.contexts import KlatContext, MQContext


class ChatbotsMqRequest(KlatContext, MQContext):
    """
    Defines a request from Klat to the Chatbots service.
    """

    username: str = Field(
        alias="nick", description="Username (or 'nick') of the sender"
    )
    cid: str = Field(description="Conversation ID associated with the shout")
    message_text: str = Field(
        alias="messageText", description="Text content of the shout"
    )
    from_bot: bool = Field(
        default=False,
        description="True if the shout is from a bot, False if from a user",
    )
    prompt_id: Optional[str] = Field(
        default=None,
        description="ID of the CCAI prompt associated with the shout",
    )
    prompt_state: Optional[CcaiState] = Field(
        default=None,
        deprecated=True,
        description="State of the CCAI conversation associated with the shout",
    )
    time_created: datetime = Field(
        default=datetime.now(tz=timezone.utc),
        description="Timestamp when the shout was created",
    )
    requested_participants: Optional[List[str]] = Field(
        default=None,
        alias="participating_subminds",
        description="List of CCAI participants requested to handle the shout",
    )
    recipient: Optional[str] = Field(
        default=None, description="Explicitly defined recipient of the shout"
    )
    bound_service: Optional[str] = Field(
        default=None, description="Service bound to the conversation"
    )
    context: dict = Field(
        default={}, deprecated=True, description="Extra proctor context"
    )

    @classmethod
    def from_sio_message(cls, sio_message: dict) -> "ChatbotsMqRequest":
        # Parse incoming message `sid`, `cid`, and `title` from SIO Message
        klat_context = KlatContext(**sio_message)
        # This is the first MQ message; define new context
        mq_context = MQContext()
        return ChatbotsMqRequest(
            **klat_context.model_dump(exclude_none=True),
            **mq_context.model_dump(exclude_none=True),
            username=sio_message.get("username")
            or sio_message.get("userDisplayName"),
            message_text=sio_message.get("message_body")
            or sio_message.get("messageText"),
            from_bot=sio_message.get("is_bot", sio_message.get("bot")) == 1,
            prompt_id=sio_message.get("prompt_id")
            or sio_message.get("promptID"),
            prompt_state=sio_message.get("prompt_state")
            or sio_message.get("promptState"),
            time_created=sio_message.get("time_created")
            or sio_message.get("timeCreated"),
            recipient=sio_message.get(
                "recipient"
            ),
            bound_service=sio_message.get("bound_service"),
        )

    def model_dump(self, **kwargs):
        """
        Override model_dump to include SIO fields for backwards compatibility
        """

        # For backwards-compat with Klat Server, include aliased keys in
        # serialization. In the future, this should be configurable and
        # eventually removed.
        by_alias = {}
        if "by_alias" not in kwargs:
            by_alias = super().model_dump(by_alias=True, **kwargs)

        # Add parameters for backwards-compat.
        by_alias["bot"] = "1" if self.from_bot else "0"

        return {**super().model_dump(**kwargs), **by_alias}


class ChatbotsMqSubmindResponse(KlatContext, MQContext):
    """
    Defines a chatbot response to a request.
    """

    user_id: str = Field(
        alias="userID", description="Unique UID of the sender"
    )
    username: Optional[str] = Field(
        default=None,
        alias="nick",
        description="Username of the sender",
    )
    message_text: str = Field(
        alias=AliasChoices("messageText", "shout"),
        description="Text content of the shout",
    )
    sid: str = Field(default="", alias="messageID", description="Shout ID")
    replied_message: Optional[str] = Field(
        default=None,
        alias=AliasChoices("repliedMessage", "responded_shout"),
        description="ID of the shout being replied to",
    )
    bot: Literal["0", "1"] = Field(
        default="0", alias="is_bot", description="1 if the shout is from a bot"
    )
    prompt_id: Optional[str] = Field(
        default=None,
        alias="promptID",
        description="ID of the CCAI prompt associated with the shout",
    )
    is_announcement: bool = Field(
        default=False,
        alias="isAnnouncement",
        description="True if the shout is an announcement",
    )
    time_created: datetime = Field(
        default=datetime.now(tz=timezone.utc),
        alias=AliasChoices("timeCreated", "time", "created_on"),
        description="Timestamp when the shout was created",
    )
    source: str = Field(
        default="klat_observer",
        description="Name of the service originating the shout",
    )
    bot_type: Optional[BotType] = Field(
        default=None,
        deprecated=True,
        description="Type of submind sending the shout",
    )

    # Below are deprecated fields for backwards-compat.
    service_name: Any = Field(default=None, deprecated=True)
    context: dict = Field(
        default={},
        deprecated=True,
        description="Context used for Klat Server backwards-compat.",
    )
    dom: Any = Field(
        default=None,
        deprecated=True,
        description="Domain of this conversation",
    )
    omit_reply: bool = Field(
        default=True,
        deprecated=True,
        description="If true, the Proctor will ignore this message",
    )
    no_save: bool = Field(
        default=False,
        deprecated=True,
        description="If true, this message will be ignored",
    )
    to_discussion: bool = Field(default=False, deprecated=True)
    prompt_state: CcaiState = Field(
        default=CcaiState.IDLE,
        deprecated=True,
        alias=AliasChoices("promptState", "conversation_state"),
        description="State of the CCAI conversation associated with the shout",
    )

    @model_validator(mode="after")
    def set_username_from_user_id(self):
        if self.username is None and self.user_id:
            self.username = self.user_id.rsplit("-", 1)[0]
        if self.username == self.user_id:
            raise ValueError(
                f"username cannot be the same as user_id: {self.username}"
            )
        return self

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        if isinstance(values, dict):
            if "sid" in values and values["sid"] is None:
                values.pop("sid")

        return values

    def model_dump(self, **kwargs):
        # For backwards-compat with Klat Server, include aliased keys in
        # serialization. In the future, this should be configurable and
        # eventually removed.
        by_alias = {}
        if "by_alias" not in kwargs:
            by_alias = super().model_dump(by_alias=True, **kwargs)

        # Add all aliases for fields using AliasChoices
        # username: AliasChoices("userDisplayName", "nick")
        by_alias["userDisplayName"] = self.username
        by_alias["nick"] = self.username

        # message_text: AliasChoices("messageText",  "shout")
        by_alias["messageText"] = self.message_text
        by_alias["shout"] = self.message_text

        # replied_message: AliasChoices("repliedMessage", "responded_shout")
        by_alias["repliedMessage"] = self.replied_message
        by_alias["responded_shout"] = self.replied_message

        # prompt_id: alias="promptID"
        by_alias["promptID"] = self.prompt_id

        # is_announcement: alias="isAnnouncement"
        by_alias["isAnnouncement"] = "1" if self.is_announcement else "0"

        # time_created: AliasChoices("timeCreated", "time", "created_on")
        if self.time_created:
            by_alias["timeCreated"] = self.time_created.timestamp()
            by_alias["time"] = self.time_created.timestamp()
            by_alias["created_on"] = self.time_created.timestamp()

        # prompt_state: AliasChoices("promptState", "conversation_state")
        if self.prompt_state:
            by_alias["promptState"] = self.prompt_state.value
            by_alias["conversation_state"] = self.prompt_state.value

        return {**super().model_dump(**kwargs), **by_alias}


class PromptCompletedContext(BaseModel):
    prompt: Optional[ChatbotsMqRequest] = Field(
        default=None, description="Original request containing the prompt"
    )

    prompt_text: str = Field(description="The string prompt that is completed")
    available_subminds: List[str] = (
        Field(  # Seems to always match `participating_subminds`
            default=[], description="List of subminds available to participate"
        )
    )
    participating_subminds: List[str] = Field(
        default=[], description="List of subminds participating in the prompt"
    )
    proposed_responses: Dict[str, str] = Field(
        default={}, description="Dict of nick to proposal"
    )

    # In the future, there will be a list of these for multi-round discussion
    submind_discussion_history: Dict[str, List[str]] = Field(
        default=[],
        description="List of dict of discussion rounds (dict of nick to shout)",
    )
    submind_opinions: Dict[str, str] = Field(
        default={}, description="Dict of nick to discussion"
    )

    votes: Dict[str, str] = Field(
        default={}, description="Dict of nick to vote"
    )
    votes_per_submind: Dict[str, List[str]] = Field(
        default={},
        description="Dict of nick to list of received votes (nicks)",
    )
    winner: str = Field(default="", description="nick of selected winner")

    # Below are deprecated
    is_active: bool = Field(  # Seems to report active all the time
        default=False,
        deprecated=True,
        description="True if a response has not yet been chosen",
    )
    state: Optional[CcaiState] = Field(
        default=CcaiState.PICK,
        deprecated=True,
        description="State of the CCAI conversation (always PICK)",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_discussion_history(cls, values):
        if (
            "submind_discussion_history" not in values
            and "submind_opinions" in values
        ):
            values["submind_discussion_history"] = {
                k: [v] for k, v in values["submind_opinions"].items()
            }
        return values


class ChatbotsMqSavePrompt(ChatbotsMqSubmindResponse):
    context: PromptCompletedContext = Field(
        alias="conversation_context",
        description="Definition of the completed discussion",
    )

    def model_dump(self, **kwargs):
        return ChatbotsMqSubmindResponse.model_dump(self, **kwargs)


class ChatbotsMqNewPrompt(KlatContext, MQContext):
    prompt_id: str = Field(
        description="ID of the CCAI prompt associated with the shout"
    )
    prompt_text: str = Field(description="The new prompt being discussed")
    prompt_state: CcaiState = Field(
        default=CcaiState.IDLE,
        deprecated=True,
        description="Implemented for backwards-compat. New Prompt always IDLE",
    )
    user_id: Optional[str] = Field(
        default=None,
        alias="userID",
        validation_alias="userID",
        description="User ID of the proctor",
    )
    sid: str = Field(default="", alias="messageID", description="Shout ID")
    username: Optional[str] = Field(
        default=None,
        alias="nick",
        description="Username of the sender",
    )
    time_created: datetime = Field(
        default=datetime.now(tz=timezone.utc),
        alias=AliasChoices("timeCreated", "time", "created_on"),
        description="Timestamp when the shout was created",
    )
    source: str = Field(
        default="klat_observer",
        description="Name of the service originating the shout",
    )
    bot_type: Optional[BotType] = Field(
        default=None,
        deprecated=True,
        description="Type of submind sending the shout",
    )
    discussion_rounds: int = Field(
        default=2,
        description="Number of discussion rounds per cycle for this prompt",
    )
    context: dict = Field(
        default={},
        deprecated=True,
        description="Conversation Context used by Klat Server",
        alias="conversation_context",
    )


class ChatbotsMqResponse:
    """
    Type adapter for validating an arbitrary MQ message. This will always return
    an instance that extends `BaseMessage` and `MQContext`.
    """

    @classmethod
    def __new__(
        cls, *_, **kwargs
    ) -> Union[
        ChatbotsMqSavePrompt, ChatbotsMqNewPrompt, ChatbotsMqSubmindResponse
    ]:
        message_text = (
            kwargs.get("message_text")
            or kwargs.get("messageText")
            or kwargs.get("shout")
        )
        kwargs["message_text"] = message_text

        if message_text == CcaiControl.SAVE_PROMPT_RESULTS.value:
            return ChatbotsMqSavePrompt(**kwargs)
        elif message_text == CcaiControl.CREATE_PROMPT.value:
            return ChatbotsMqNewPrompt(**kwargs)
        else:
            return ChatbotsMqSubmindResponse(**kwargs)


class ChatbotsMqSubmindsState(MQContext):
    class SubmindState(BaseModel):
        submind_id: str = Field(
            description="Connected submind's ID (nickname + suffix)"
        )
        status: SubmindStatus = Field(
            description="Subminds's status in a particular conversation"
        )

    subminds_per_cid: Dict[str, List[SubmindState]] = Field(
        description="List of submind participants per conversation ID"
    )
    connected_subminds: Dict[str, ConnectedSubmind] = Field(
        description="Dict of `submind_id` to `ConnectedSubmind` object"
    )
    cid_submind_bans: Dict[str, List[str]] = Field(
        description="Dict of `cid` to list of banned `submind_id`s"
    )
    banned_subminds: List[str] = Field(
        description="List of globally banned `submind_id`s"
    )

    msg_type: Literal["subminds_state"] = Field(
        "subminds_state", description="Message type for SIO", deprecated=True
    )


class ChatbotsMqConfiguredPersonasRequest(MQContext):
    service_name: str = Field(
        description="Name of the service to get personas for"
    )
    user_id: Optional[str] = Field(
        default=None, description="Optional user_id making the request."
    )


class ChatbotsMqConfiguredPersonasResponse(MQContext):
    update_time: datetime = Field(
        description="Time the personas were last checked"
    )
    items: List[LLMPersona] = Field(
        description="List of configured personas from Klat"
    )

    context: dict = Field(deprecated=True)

    @model_validator(mode="before")
    @classmethod
    def validate_context(cls, values):
        # Deprecated context handling for backwards-compat.
        if "context" not in values and "message_id" in values:
            values["context"] = {"mq": {"message_id": values["message_id"]}}
        return values

    def model_dump(self, **kwargs):
        """
        Override model_dump to include 'persona_name' field for each item based
        on its 'name' for backwards-compat. with Klat server
        """
        by_alias = {}
        if "by_alias" not in kwargs:
            # `by_alias` to include `persona_name` in serialized `LLMPersona`s
            by_alias = super().model_dump(by_alias=True, **kwargs)

        return {**super().model_dump(**kwargs), **by_alias}

    @classmethod
    def from_persona_request(
        cls, data: dict, request: ChatbotsMqConfiguredPersonasRequest
    ):
        data["items"] = [
            item
            for item in data["items"]
            if request.service_name in item["supported_llms"]
        ]
        return cls(
            **data,
            message_id=request.message_id,
            routing_key=request.routing_key,
        )


class ChatbotsMqPromptsDataRequest(MQContext):
    """
    Convenience class. The message payload here is just `MQContext`.
    """


class ChatbotsMqPromptsDataResponse(MQContext):
    records: List[str] = Field(description="List of configured prompts")

    context: dict = Field(deprecated=True)

    @model_validator(mode="before")
    @classmethod
    def validate_context(cls, values):
        # Deprecated context handling for backwards-compat.
        if "context" not in values and "message_id" in values:
            values["context"] = {"mq": {"message_id": values["message_id"]}}
        return values

    @classmethod
    def from_prompt_data_request(
        cls, data: dict, request: ChatbotsMqPromptsDataRequest
    ):
        return cls(
            **data,
            message_id=request.message_id,
            routing_key=request.routing_key,
        )


class ChatbotsMqSubmindConnection(MQContext):
    user_id: str = Field(
        description="User ID of the submind",
        validation_alias="userID",
        alias="userID",
    )
    time: datetime = Field(
        default=datetime.now(tz=timezone.utc),
        description="Timestamp when the submind last connected",
    )
    cids: Optional[List[str]] = Field(
        default=None, description="List of conversation IDs the submind is in"
    )
    context: Optional[ConnectedSubmind] = Field(
        default=None,
        description="ConnectedSubmind definition of the connecting bot",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_context(cls, values):
        if "context" in values and isinstance(values["context"], dict):
            user_id = values.get("user_id") or values.get("userID") or ""
            values["context"].setdefault(
                "service_name", user_id.rsplit("-", 1)[0]
            )
        return values


class ChatbotsMqSubmindDisconnection(MQContext):
    user_id: str = Field(
        description="User ID of the submind",
        validation_alias="userID",
        alias="userID",
    )


class ChatbotsMqSubmindInvitation(MQContext):
    cid: str = Field(description="Conversation ID to invite subminds to")
    requested_participants: List[str] = Field(
        description="List of submind User IDs to invite to the conversation"
    )


class ChatbotsMqUpdateParticipatingSubminds(MQContext):
    cid: str = Field(description="Conversation ID to update")
    subminds_to_invite: List[str] = Field(
        default=[],
        description="List of submind User IDs to invite to the conversation",
    )
    subminds_to_kick: List[str] = Field(
        default=[],
        description="List of submind User IDs to evict from the conversation",
    )


class ChatbotsMqSubmindConversationBan(MQContext):
    user_id: str = Field(
        description="User ID of the submind",
        validation_alias="userID",
        alias="userID",
    )
    cid: str = Field(description="Conversation ID to (un)ban submind from")


class ChatbotsMqSubmindGlobalBan(MQContext):
    user_id: str = Field(
        description="User ID of the submind",
        validation_alias="userID",
        alias="userID",
    )


class ChatbotsMqSubmindResponseError(MQContext):
    message: Optional[str] = Field(
        default=None, alias="msg", description="Error message"
    )


__all__ = [
    ChatbotsMqRequest.__name__,
    ChatbotsMqResponse.__name__,
    ChatbotsMqSubmindResponse.__name__,
    ChatbotsMqSavePrompt.__name__,
    ChatbotsMqNewPrompt.__name__,
    ChatbotsMqSubmindsState.__name__,
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
    ChatbotsMqSubmindResponseError.__name__,
]
