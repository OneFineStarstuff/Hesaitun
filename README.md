# Enterprise AI Integration Protocol (EAIP)

![Version](https://img.shields.io/badge/version-2.4.1-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Status](https://img.shields.io/badge/status-FINALIZED-success)

The **Enterprise AI Integration Protocol (EAIP)** is a standardized framework for the interoperability, security, and state management of autonomous agent systems within the enterprise. It provides mandatory requirements for transport, identity, and distributed state propagation.

## 🚀 Key Features

- **Standardized Transport**: Mandates **gRPC over HTTP/2** for efficient, low-latency communication.
- **Robust Identity Layer**: Utilizes **SPIFFE/SPIRE** for workload identity and **mutual TLS 1.3** for secure channel establishment.
- **Recursive Context Envelope (RCE)**: A unified state-management system for distributed AI workloads, ensuring consistent context propagation across heterogeneous agent systems.
- **Policy-Driven Governance**: Integrates **Open Policy Agent (OPA)** for fine-grained, real-time authorization and compliance.

## 📂 Project Structure

- `EAIP_Technical_Specification.xml`: The definitive technical specification.
- `governance/`: A comprehensive AGI/ASI Governance Framework organized into six domains:
  - `core/`: Architecture design and implementation guides.
  - `executive/`: Dashboards and summaries for leadership.
  - `ops/`: Operational models and CoE frameworks.
  - `readiness/`: Assessment tools and maturity rubrics.
  - `technical/`: Advanced technical architectures and policies.
  - `communication/`: Playbooks and reporting templates.

## 🛠 Getting Started

This repository includes a `Makefile` to assist with compliance and verification.

### Run Technical Compliance Checks
Execute the EAIP v2.4.1 compliance suite:
```bash
make check-gsifi-governance
```

### Verify Framework Integrity
Verify the integrity of all governance documents and links:
```bash
make verify-framework
```

Refer to the [Master Index](governance/core/MASTER_INDEX.md) for a detailed breakdown of all available tools and guides.

## 📄 License

This specification is licensed under the [Apache License 2.0](LICENSE).

---
*Maintained by the EAIP Technical Standards Committee.*
