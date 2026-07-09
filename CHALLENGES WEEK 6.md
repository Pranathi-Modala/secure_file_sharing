# CHALLENGES WEEK 6

## Challenges Encountered

During Week 6, I had several implementation challenges while completing authentication hardening work.

1. Integrating security improvements without breaking the existing session-based workflow took longer than expected.
2. Aligning lockout, failed-attempt tracking, and user feedback messages required careful testing across multiple login scenarios.
3. Keeping documentation fully synchronized with code updates during active changes was also challenging.

## PostgreSQL Implementation Challenge

I was having challenges implementing PostgreSQL integration in this phase. I attempted to plan the migration path from the current model, but I did not manage to complete the PostgreSQL implementation during Week 6.

Key blockers were:

- Additional setup and schema design effort needed to avoid disrupting the current authentication and file workflow.
- Need for controlled migration steps and testing before replacing current storage behavior.

## Decision and Next Step

Because of these constraints, I will proceed with PostgreSQL implementation in Week 7.

Week 7 plan:

- Define the initial database schema for users, files, share metadata, and auth-related records.
- Implement database connection and configuration integration.
- Migrate selected in-memory operations to PostgreSQL incrementally.
- Run validation tests to confirm authentication and file operations remain stable.
