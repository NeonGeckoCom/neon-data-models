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

## Access Roles
This module defines `AccessRoles` for use with Role-Based Access Control (RBAC).
The `AccessRoles` enum defines some specific roles and is structured such that
roles correspond to an integer value in the range of `-inf`-`50`.

Roles are structured such that `0` corresponds to no permissions and `50` is
reserved for unlimited permissions. A role will always include the permissions
available to any role with a smaller positive number. For example, an `ADMIN`
role with a value of `30` will have access to everything a `USER` with value `20`
does, and possibly more.

A role is defined per service, so a user may have greater access to some 
resources than others. For example, a user may have unlimited access to manage
LLM deployments, but only read access to the DIANA backend.

### Service Roles
Roles with a value <0 are intended for use by non-user service accounts. These
roles contain specific access that is limited to the requirements of a specific 
program or service.

For example, the `AccessRoles.NODE` role is used by a node device making
API requests.

### Guest Role
The `AccessRoles.GUEST` role is used by a guest user, which is usually implemented
as a single account with public credentials.

### User Role
The `AccessRoles.USER` role is used by a registered user. It should NOT be 
assumed that a registered user has been verified or validated in any way.

### Admin Role
The `AccessRoles.ADMIN` role is assigned to a user who is responsible to 
administration of a resource.

### Owner Role
The `AccessRoles.OWNER` role is assigned to a user who owns a resource.
