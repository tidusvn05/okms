---
type: MicroSpec
title: P002-MS01 · Admin device catalog
description: Let administrators manage uniquely identified devices while preserving loan history and recording successful mutations.
---

# P002-MS01 · Admin device catalog

## Intent

Provide administrator server operations to create, update, and softly retire devices. Normalize asset codes, keep them unique, and preserve loan history.

## Constraints

- Always: enforce administrator authorization at the router and persist an audit record for every successful change.
- Never: hard-delete a device or expose a raw database error for duplicate asset codes.

## Acceptance

- Given an administrator and valid input, When creating a device, Then an active device and its audit record are saved through the real schema.
- Given an asset code colliding after normalization, When creating or updating a device, Then a clear business error is returned and existing data is unchanged.
- Given a device with loan history, When retiring it, Then history remains and the device accepts no new requests or approvals.
- Given a non-administrator, When calling catalog mutations, Then the server refuses the operation without changing catalog data.

## Verify

Check the destination project's actual migrations, admin router, and lending service, including retirement effects on new requests and approvals. Use its real focused command; a `[p002-ms01]` test label is optional. Record actual results in the parent plan's Work table.
