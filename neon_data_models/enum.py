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

from enum import Enum, IntEnum


class AccessRoles(IntEnum):
    """
    Defines access roles such that a larger value always corresponds to more
    permissions. `0` equates to no permission, negative numbers correspond to
    non-user roles. In this way, an activity can require, for example,
    `permission > AccessRoles.GUEST` to grant access to all registered users,
    admins, and owners.

    Special Roles:
        NODE: Reserved for use by a Node device service account to access
            various services
    """
    NONE = 0
    # 1-9 reserved for unauthenticated connections
    GUEST = 10
    # 11-19 reserved for unverified user roles
    USER = 20
    # 21-29 Reserved for "premium users"
    ADMIN = 30
    # 31-39 Reserved for "restricted owners"
    OWNER = 40
    # 41-49 Reserved for "escalated owners"

    # 50 Reserved for "unlimited access"

    NODE = -1


class UserData(IntEnum):
    """
    Defines types of user data.
    """
    CACHES = 0
    PROFILE = 1
    TRANSCRIPTS = 2
    LIKED_BRANDS = 3
    DISLIKED_BRANDS = 4
    ALL_DATA = 5
    ALL_MEDIA = 6
    UNITS_CONFIG = 7
    LANGUAGE_CONFIG = 8


class AlertType(IntEnum):
    """
    Defines kinds of alerts.
    """
    ALL = -1
    ALARM = 0
    TIMER = 1
    REMINDER = 2
    UNKNOWN = 99


class Weekdays(IntEnum):
    """
    Defines weekdays as used in the Alerts skill.
    """
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


class SubmindStatus(Enum):
    """
    Defines status of a submind in a particular conversation
    """
    BANNED = "banned"
    ACTIVE = "active"


class CcaiState(IntEnum):
    """
    Defines status of a conversation where a CCAI is operating
    """
    IDLE = 0  # No active prompt
    RESP = 1  # Gathering responses to prompt
    DISC = 2  # Discussing responses
    VOTE = 3  # Voting on responses
    PICK = 4  # Proctor will select response
    WAIT = 5  # Bot is waiting for an invitation to participate


class CcaiControl(Enum):
    """
    Defines control messages for a CCAI conversation
    """
    PROMPT_REGEX = r"^!PROMPT:"
    SAVE_PROMPT_RESULTS = "!MSG:SAVE_PROMPT_RESULTS"
    CREATE_PROMPT = "!MSG:CREATE_PROMPT"
    START_AUTO_PROMPTS = "!START_AUTO_PROMPTS"
    STOP_AUTO_PROMPTS = "!STOP_AUTO_PROMPTS"
