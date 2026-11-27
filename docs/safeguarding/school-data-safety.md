# School Data Safety — Baseline Requirements

This is an engineering and governance checklist, not legal advice or a completed compliance assessment.

## Default position

The prototype should work with public or otherwise approved educational resources and should not require identifiable learner records. Do not use student data for model training by default.

## Prohibited by default for the pilot

- Facial recognition or biometric identification.
- Behavioural profiling or emotion inference.
- Automated grading or high-stakes decisions without accountable human review.
- Sending identifiable learner data to external AI services.
- Collecting precise location or sensitive personal information without a justified, approved purpose.

## Minimum controls

- Role-based access and secure administrator authentication.
- Encryption in transit and appropriate protection at rest.
- Short, documented retention periods for operational logs.
- Ability to delete accounts and remove data under an approved process.
- No secrets or real personal data in source control, demos or test fixtures.
- Clear labels that AI outputs can be incorrect and require educator judgement.
- Content reporting and escalation path.
- Security updates, backups and tested recovery.

## Before any live school pilot

Conduct data mapping, privacy and safeguarding reviews; identify controller/processor responsibilities; confirm applicable Nigerian data protection requirements; establish appropriate notices and consent/authorisation; and obtain school approval.
