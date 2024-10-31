import json
from os import makedirs
from os.path import join, dirname

from pydantic import BaseModel

import neon_data_models.models


def build_json_schema():
    root_path = dirname(__file__)
    for object in neon_data_models.models.__dict__.values():
        try:
            if issubclass(object, BaseModel) and object.__name__ != "BaseModel":
                path_parts = ([root_path, "schema"] +
                              object.__module__.split('.')[2:] +
                              [f"{object.__name__}.json"])
                out_path = join(*path_parts)
                makedirs(dirname(out_path), exist_ok=True)
                with open(out_path, 'w+') as f:
                    json.dump(object.model_json_schema(), f, indent=2)
        except TypeError:
            pass


if __name__ == '__main__':
    build_json_schema()
