## Neon Data Models
This repository contains Pydantic models and JSON schemas for common data
structures. The `models` module contains Pydantic models, organized by application.

## Configuration
To allow passing or handling parameters that are not explicitly defined in the
models provided by this package, the `NEON_DATA_MODELS_ALLOW_EXTRA` envvar may
be set to `true`. This is generally not necessary and helps to prevent sending
extraneous data, but may help in cases where the server and client are using
different revisions of this package.

## Organization
Models are broadly organized into the following categories.

### API
These schemas are used in API requests and responses. They are grouped by the
applicable API (node, HANA, mq). Use these schemas for sending requests and
parsing responses.

### Client
These schemas are specific to client applications (i.e. Nodes). Use these
schemas for client-specific configuration.

### User
These schemas define user-specific data structures. Use these schemas for 
user-specific configuration.

### Messagebus
These schemas define messages sent on the messagebus. Historically, messagebus
events have not used any validation, so there is greater risk of Message objects
failing validation than other schemas defined here. 