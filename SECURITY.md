# Security policy

## Scope

This repository is a portfolio prototype and must not be used with real customer or shipment data without an approved security and privacy review.

## Reporting

Please use GitHub's private vulnerability reporting for security issues. Do not open a public issue containing exploit details, personal data, credentials or real shipment information.

## Secure defaults

- Original images are not persisted.
- Raw OCR storage is disabled by default.
- Upload size and supported image formats are restricted.
- CSRF protection is enabled for state-changing browser requests.
- Printing is blocked until a user has confirmed the extracted data.
- Secrets and databases are excluded from version control.
- Dependency updates are monitored with Dependabot.

Production deployment requires managed authentication, authorization, TLS, secret storage, monitoring, retention controls and an approved integration design.
