# Project Context Snapshot

*This document provides a high-level, "at-a-glance" summary of the project's current state. It should be updated at the end of major work sessions.*

---

**Project Synopsis**: A secure, "burn after reading" note and file sharing application.

**Current High-Level Goal**: The project has achieved a stable v2.0 release with a fully documented production deployment. It is now awaiting new feature planning or maintenance tasks.

**Last Major Milestone Achieved**: Successful and documented deployment to a Debian 12 server with Baota panel.

**Recent Key Activities**:
-   Completed a comprehensive overhaul of all project documentation, including `DEPLOYMENT.md`, `README.md`, `Structure.md`, and `Design.md`.
-   Troubleshot and resolved a series of complex production issues.
-   Finalized the v2.0 feature set.

**Current Active Task(s)**: None. Awaiting new tasks.

**Immediate Next Steps**:
1.  Define the scope for the next feature release (Phase 4: Advanced Security & Polish in `Plan.md`).
2.  Or, enter a maintenance and monitoring phase.

**Critical Blockers/Open Issues**: None at present.

**"Remember This" / "Hot Spots"**:
-   The `DEPLOYMENT.md` is now the single source of truth for all deployment-related activities.
-   The interaction between the external Baota Nginx and the internal Docker containers is a critical architectural point. Any changes to networking or ports must consider this. 