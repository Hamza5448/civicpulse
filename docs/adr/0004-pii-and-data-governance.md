# ADR 0004: Protect Complaint Data During Hosted Triage

- Status: Accepted
- Date: 2026-09-28

## Context

Complaint text and locations may contain names, addresses, phone numbers, or other personally identifiable information. Hosted LLM providers receive data outside the local deployment boundary, while Ollama and rules-based providers can operate locally.

## Decision

The default provider is the local `rules` provider. Hosted LLM use is opt-in through `TRIAGE_PROVIDER=llm` and requires an explicit API key configuration. The current adapter sends the complaint text and location to the configured provider because classification depends on both fields; operators must choose a provider whose data-use terms are acceptable before enabling it. Secrets are read only from environment configuration and never logged or committed.

## Consequences

- Local rules or Ollama are the preferred options for complaints containing sensitive information.
- Hosted-provider use is an explicit deployment decision rather than an accidental default.
- A later phase may add configurable redaction before hosted calls; it is not silently implemented here because redaction can change classification accuracy.
