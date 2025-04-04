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

from enum import Enum
from os import environ
from datetime import datetime, timedelta
from pydantic import ConfigDict, BaseModel as _BaseModel


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra="allow" if environ.get(
            "NEON_DATA_MODELS_ALLOW_EXTRA", "false") != "false" else "ignore",
            populate_by_name=environ.get("NEON_DATA_MODELS_POPULATE_BY_NAME",
                                          "true") != "false",)
        
    def model_dump(self, *args, **kwargs) -> dict:
        """
        Global `model_dump` overrides to ensure model serialization.
        Recursively processes nested dictionaries, lists, and BaseModel instances.
        """
        data = super().model_dump(*args, **kwargs)
        return self._process_data(data)
    
    def _process_data(self, data):
        """
        Recursively process data to convert datetime and timedelta objects.
        """
        if isinstance(data, dict):
            # Process dictionary values
            for key, value in list(data.items()):
                data[key] = self._process_data(value)
            return data
        elif isinstance(data, list):
            # Process list elements
            return [self._process_data(item) for item in data]
        elif isinstance(data, datetime):
            # Convert datetime to timestamp
            return data.timestamp()
        elif isinstance(data, timedelta):
            # Convert timedelta to seconds
            return data.total_seconds()
        elif isinstance(data, Enum):
            # Always serialize `Enum` objects by value
            return data.value
        else:
            # Return other types unchanged
            return data


