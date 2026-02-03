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

from typing import List
from pydantic import Field, RootModel
from neon_data_models.models.api.messagebus import (
    NeonSkillApiData,
    SkillApiRequestData,
    SkillApiResponseData,
)


class NeonSkillApiHttpData(NeonSkillApiData):
    skill_id: str = Field(
        description="ID of the skill providing this API method"
    )
    api_method: str = Field(description="API method name")


class NeonHttpListSkillApiResponse(RootModel):
    root: List[NeonSkillApiHttpData]

    model_config = {
        "json_schema_extra": {
            "examples": [
                [
                    {
                        "help": "\n        API Method to build a list of examples as listed in skill metadata.\n        ",
                        "request_schema": None,
                        "response_schema": None,
                        "signature": None,
                        "type": "skill-about.neongeckocom.skill_info_examples",
                        "skill_id": "skill-about.neongeckocom",
                        "api_method": "skill_info_examples",
                    },
                    {
                        "help": "\n        Get the current timestamp in seconds since epoch.\n        :param request: Request containing location to get time of\n        :returns: Response containing current timestamp\n        ",
                        "request_schema": {
                            "properties": {
                                "location": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {"type": "null"},
                                    ],
                                    "default": None,
                                    "title": "Location",
                                }
                            },
                            "title": "_CurrentTimeRequest",
                            "type": "object",
                        },
                        "response_schema": {
                            "properties": {
                                "current_timestamp": {
                                    "title": "Current Timestamp",
                                    "type": "number",
                                }
                            },
                            "required": ["current_timestamp"],
                            "title": "_CurrentTimeResponse",
                            "type": "object",
                        },
                        "signature": "(request: skill_date_time._CurrentTimeRequest) -> skill_date_time._CurrentTimeResponse",
                        "type": "skill-date_time.neongeckocom.get_current_time",
                        "skill_id": "skill-date_time.neongeckocom",
                        "api_method": "get_current_time",
                    },
                ]
            ]
        }
    }


class NeonHttpSkillApiRequest(SkillApiRequestData):
    skill_id: str = Field(description="skill_id being requested")
    api_method: str = Field(description="API method being requested")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "skill_id": "skill-about.neongeckocom",
                    "api_method": "skill_info_examples",
                    "args": [],
                    "kwargs": {},
                }
            ]
        }
    }


class NeonHttpSkillApiResponse(SkillApiResponseData):
    """
    Convenience wrapper to implement examples for Swagger UI
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": "API Response matching advertised schema",
                    "error": None,
                },
                {"result": None, "error": "API Method error message"},
            ]
        }
    }


__all__ = [
    NeonHttpListSkillApiResponse.__name__,
    NeonHttpSkillApiRequest.__name__,
    NeonHttpSkillApiResponse.__name__,
]
