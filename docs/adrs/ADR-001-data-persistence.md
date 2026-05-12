# ADR-001: Data Persistence Strategy

**Status**: Accepted  
**Date**: 2026-05-12  
**Deciders**: InnovatEPAM Portal Architecture Committee  
**Affected Stakeholders**: Backend team, DevOps, Security  

---

## Context

InnovatEPAM Portal Phase 1 MVP must store and retrieve:
- Employee user identities with authentication credentials
- Innovation ideas (title, description, category, status)
- File attachments (one per idea, max 5MB)
- Complete audit trail of all governance and security events

**Requirements**:
- Persistent storage across server restarts
- Support for ACID transactions (for decision-making integrity)
- Scalability to thousands of users and ideas
- Easy schema evolution as features expand in later phases
- Audit compliance with immutable records

**Constraints**:
- Phase 1 budget: Minimize infrastructure costs
- Development timeline: Need rapid iteration without complex schema migrations
- Team expertise: Python and MongoDB (decided in Constitution Principle II)

---

## Decision

Use **MongoDB Atlas** (cloud-hosted MongoDB) as the primary data persistence layer with:
- **Pydantic** for application-level schema validation
- **Motor** (async MongoDB driver) for non-blocking I/O
- **GridFS** for attachment file storage (embedded in MongoDB)
- **Optimistic concurrency control** using version fields for concurrent updates

---

## Rationale

### 1. MongoDB Atlas (Document Database)

**Why MongoDB?**
- **Flexibility**: Document schema naturally maps to Python objects (via Pydantic)
- **Rapid iteration**: No complex migration scripts for schema changes (unlike SQL)
- **Scalability**: Horizontal sharding built-in for future phases
- **Consistency**: ACID transactions at document level (sufficient for Phase 1)
- **Native audit**: Store full history in audit_logs collection
- **File storage**: GridFS handles attachments without external S3 (MVP simplicity)

**Why Atlas (cloud)?**
- **Operational simplicity**: No database administration overhead
- **Built-in backups**: Automatic daily backups included in free tier
- **Monitoring**: Atlas provides connection pooling, performance analytics
- **Free tier**: M0 cluster sufficient for Phase 1 MVP development and early production

### 2. Pydantic Validation

**Why Pydantic instead of MongoDB schema validation?**
- **Type safety**: Full static type checking in Python (vs MongoDB JSON schema subset)
- **Consistency**: Validation happens in application before write (fail fast)
- **Clear errors**: Pydantic produces human-readable validation error messages for API responses
- **Separation of concerns**: Application validates business logic; DB validates structure

**Schema Definition**:
```python
class User(BaseModel):
    email: EmailStr  # Pydantic validates email format
    role: Literal["submitter", "evaluator", "admin"]  # Enum validation
    hashed_password: str  # Never returned in API
```

### 3. Motor (Async Driver)

**Why async?**
- FastAPI is async-first framework (ASGI)
- Prevents thread pool exhaustion under concurrent requests
- Better resource utilization on limited-resource servers (VPS)
- Enables handling 10x concurrent connections with single server instance

### 4. GridFS for Attachments

**Why GridFS instead of S3/external storage?**
- **Phase 1 simplicity**: 5MB files fit easily in single MongoDB document (16MB limit)
- **Reduced dependencies**: No additional service to configure/monitor
- **Easier backup**: All data in one system
- **Audit trail**: File metadata stored alongside audit entries

**Transition path**: Phase 2 can migrate to S3 if attachment volume exceeds 1GB/month.

### 5. Optimistic Concurrency Control

**Why version fields instead of pessimistic locking?**
- **Low contention expected**: Few concurrent evaluators in Phase 1
- **Simplicity**: No distributed locks required
- **Scalability**: No blocking; reader-writer conflicts resolved at application level
- **Debuggability**: Conflicts are explicit and traceable

**Implementation**:
```mongodb
db.ideas.updateOne(
  { _id: idea_id, _version: current_version },
  { $set: { status: new_status, _version: current_version + 1 } }
)
// If matched_count == 0: conflict; client retries with fresh version
```

---

## Alternatives Considered

### Alternative 1: PostgreSQL (Relational Database)

**Rejected because**:
- Slower iteration: SQL schema changes require migrations (`ALTER TABLE`, rollback risk)
- Over-engineered: ACID relational constraints unnecessary for MVP scope
- Complex joins: Audit history queries would require complex JOINs vs MongoDB simple filter
- Overkill for single-server Phase 1 (advantages only visible at massive scale)

**When to reconsider**: Phase 3+ if complex reporting queries across normalized tables become critical

### Alternative 2: DynamoDB (NoSQL, AWS)

**Rejected because**:
- Vendor lock-in: AWS-specific (harder to migrate later)
- Cost at scale: Pay-per-request model expensive for analytics queries
- Limited querying: No aggregation pipeline like MongoDB
- Learning curve: Different query syntax than MongoDB

### Alternative 3: Files + In-Memory Cache (No Database)

**Rejected because**:
- No persistence: Data lost on restart
- No concurrency: Multiple server instances can't share state
- Audit trail: Impossible to maintain reliable history
- Specification requirement FR-020: "Preserve historical governance entries"

### Alternative 4: Attachment Storage on Filesystem

**Rejected because**:
- Horizontal scaling: Can't share files across multiple server instances
- Backup complexity: Separate backup process for files
- Permissions: Security model more complex than database
- MongoDB GridFS is simpler for MVP

---

## Consequences

### Positive

✅ **Rapid development**: Schema changes don't require migrations  
✅ **Natural Python integration**: Pydantic schemas match MongoDB documents  
✅ **Cost-effective**: MongoDB Atlas free tier covers MVP  
✅ **Audit-first design**: Full governance history preserved automatically  
✅ **Scalable**: Can handle 100x growth without major refactoring  
✅ **Type-safe**: Pydantic validation catches errors early  

### Negative

❌ **No ACID across collections**: Transactions limited to single document (acceptable for Phase 1)  
❌ **Schema responsibility on app**: No DB-level foreign key enforcement  
❌ **Learning curve**: Some developers may need to learn MongoDB paradigms  

### Mitigations

| Risk | Mitigation |
|------|-----------|
| Data corruption from concurrent writes | Optimistic locking with _version field + client retry logic |
| Lost data if database deleted | Enable MongoDB Atlas automatic backups + document retention policy |
| Slow queries on large datasets | Proper indexing strategy (see data-model.md) + monitoring |
| Schema drift between app and DB | Pydantic validation enforced on every write + test coverage |

---

## Implementation Details

### Connection Pooling

Motor manages connection pool per Uvicorn worker:
```python
client = AsyncClient(
    MONGODB_URI,
    socketTimeoutMS=30000,
    connectTimeoutMS=10000,
    maxPoolSize=50,  # Per worker
    minPoolSize=10
)
```

### Indexes

All indexes must be created before production deployment:
```python
# Automatic index creation in init_db.py
db.users.createIndex({ email: 1 }, { unique: true })
db.ideas.createIndex({ submitter_id: 1, created_at: -1 })
db.audit_logs.createIndex({ resource_id: 1, timestamp: -1 })
```

### Data Validation Layers

1. **Pydantic (Application)**: Type safety, business rule validation
2. **MongoDB (Database)**: Uniqueness constraints, TTL expiration
3. **API Schema (FastAPI)**: Additional validation in request/response models

---

## Related Decisions

- **ADR-002**: Authentication & Authorization (depends on User collection structure)
- **ADR-003**: Testing & Quality Assurance (test data in MongoDB)
- **Constitution Principle II**: Primary tech stack (MongoDB + Pydantic mandated)

---

## Verification

Acceptance criteria for this ADR:
- [ ] MongoDB Atlas cluster provisioned and accessible
- [ ] Pydantic schemas defined for all entities (see data-model.md)
- [ ] Motor connection pool configured and tested
- [ ] All indexes created and verified
- [ ] GridFS working for file uploads/downloads
- [ ] Optimistic locking test passes with concurrent updates
- [ ] Audit trail captures all writes
- [ ] Data persists across server restarts

---

## Questions & Answers

**Q: Why not use SQLAlchemy ORM for relational database?**  
A: Phase 1 requirements don't justify relational schema complexity. MongoDB provides sufficient structure via Pydantic without migration overhead.

**Q: Will MongoDB scale for millions of records?**  
A: Yes. With proper indexing and sharding (Phase 2), MongoDB scales to billions of documents. Phase 1 will have <10k ideas.

**Q: What if we need to migrate to SQL later?**  
A: Possible but non-trivial. Choose MongoDB for Phase 1; evaluate migration cost in Phase 3 if needed. Data export tools exist.

**Q: Is GridFS secure for sensitive attachments?**  
A: GridFS respects MongoDB authentication. Phase 1 doesn't encrypt at rest; Phase 2 can add database-level encryption.

---

## References

- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Motor Async Driver](https://motor.readthedocs.io/)
- [Pydantic Schema Validation](https://docs.pydantic.dev/)
- [MongoDB GridFS](https://docs.mongodb.com/manual/core/gridfs/)
- [MongoDB Transactions](https://docs.mongodb.com/manual/core/transactions/)

---

**Approval Status**: ✅ Accepted  
**Next Review Date**: 2026-08-12 (end of Phase 2)
