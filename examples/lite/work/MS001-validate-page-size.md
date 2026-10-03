---
type: MicroSpec
title: MS001 · Validate page size
description: Accept integer page sizes from one through one hundred and reject malformed values without changing the default.
work_status: planned
---

# MS001 · Validate page size

## Intent

Give callers predictable pagination validation while preserving a page size of 20 when the parameter is omitted.

## Constraints

- Always: accept only decimal integer input representing a value from 1 through 100, inclusive.
- Never: silently replace a supplied invalid value with the default or expose a low-level parsing exception.

## Acceptance

- Given no page-size parameter, When listing articles, Then the page size is 20.
- Given a supplied decimal integer from 1 through 100, When listing articles, Then that size is used.
- Given zero, a negative number, or a value over 100, When listing articles, Then a validation error is returned.
- Given empty, fractional, scientific-notation, or non-numeric input, When listing articles, Then a validation error is returned.

## Verify

Use the destination project's real targeted tests or equivalent check for omission, valid boundaries, and invalid inputs, then run its required checks. A test label such as `[ms001]` is optional.

Result: not run; this document is an illustration and contains no application. Resolve actual commands and paths before implementation.
