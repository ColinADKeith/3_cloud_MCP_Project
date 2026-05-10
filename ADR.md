# ADR 1: Multi-Cloud Agentic Orchestration

## Status
Proposed / In-Progress

## Context
I am building an autonomous agent system to assist with professional job applications. The system requires high-fidelity LLM generation, enterprise-grade safety filtering, and long-term vector memory.

## Decision
I have decided to utilize a **Cross-Cloud Architecture** across three providers to maximize the "Always Free" tiers of 2026:

1. **AWS (The Executioner):** Used for **Amazon Bedrock (Claude 3.5)** and **Lambda**. AWS provides the best developer experience for agentic tools and serverless execution.
2. **Azure (The Safety Officer):** Used for **Azure AI Content Safety**. This ensures all generated content and incoming job links are vetted for security and policy compliance.
3. **Oracle Cloud (The Data Guardian):** Used for **OCI Autonomous Database 26ai**. OCI offers the most generous free-tier Vector Database, which is essential for Retrieval-Augmented Generation (RAG).

## Consequences
- **Pros:** Zero-cost infrastructure, experience with multi-cloud networking, and specialized use of each provider's best tools.
- **Cons:** Increased complexity in authentication and secret management.