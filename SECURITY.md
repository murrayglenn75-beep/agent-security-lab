# Security Policy

## Scope

Agent Security Lab is a defensive research and regression-testing project built around local simulated tools and canary data.

Please do not use project issues to post real credentials, private keys, access tokens, customer data, or exploit details for third-party systems.

## Reporting a repository vulnerability

If you find a vulnerability in the repository itself, describe the affected component, reproduction conditions using synthetic data, and expected security property.

Do not include real-world stolen data or target unrelated systems.

## Security design principle

The project assumes model-facing logic can become manipulated. Sensitive authorization is therefore kept outside the model and evaluated by deterministic controls and an independent evaluator.
