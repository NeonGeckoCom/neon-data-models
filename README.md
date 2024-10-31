## Neon Data Models
This repository contains Pydantic models and JSON schemas for common data
structures. The `models` module contains Pydantic models, organized by application.

## Configuration
To allow passing or handling parameters that are not explicitly defined in the
models provided by this package, the `NEON_DATA_MODELS_ALLOW_EXTRA` envvar may
be set to `true`. This is generally not necessary and helps to prevent sending
extraneous data, but may help in cases where the server and client are using
different revisions of this package.