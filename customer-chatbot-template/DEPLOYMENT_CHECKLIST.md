# Production Deployment Checklist

A comprehensive checklist for deploying the customer chatbot to production.

---

## Phase 1: Pre-Deployment Setup

### 1.1 Environment Configuration

- [ ] Create production `.env` file from template
- [ ] Set `OPENAI_API_KEY` with production key
- [ ] Set `ASSISTANT_NAME` to customer-specific name
- [ ] Configure `CORS_ORIGINS` to production domain(s) only
- [ ] Set `LOG_LEVEL` to `WARNING` or `ERROR`
- [ ] Remove or disable debug settings

### 1.2 Document Preparation

- [ ] Collect all customer documents
- [ ] Review documents for sensitive information
- [ ] Organize documents in `backend/data/`
- [ ] Run `python scripts/setup-vector-store.py`
- [ ] Verify vector store created successfully
- [ ] Test document retrieval with sample queries
- [ ] Update `.env` with production `VECTOR_STORE_ID`

### 1.3 Assistant Configuration

- [ ] Customize `ASSISTANT_INSTRUCTIONS_TEMPLATE` in `config.py`
- [ ] Choose appropriate `ASSISTANT_MODEL` (cost vs capability)
- [ ] Set `ASSISTANT_TEMPERATURE` (lower for factual responses)
- [ ] Configure `MAX_SEARCH_RESULTS` (balance speed vs accuracy)
- [ ] Test assistant responses with sample questions
- [ ] Verify citations are accurate and complete

### 1.4 Code Customization

- [ ] Update branding in frontend (if using)
- [ ] Customize greeting and starter prompts
- [ ] Review and update API endpoint paths if needed
- [ ] Add customer logo/favicon
- [ ] Update page title and meta tags

---

## Phase 2: Security Hardening

### 2.1 Store Implementation

- [ ] **CRITICAL**: Replace `MemoryStore` with database store
  - [ ] Choose database (PostgreSQL, MongoDB, Redis)
  - [ ] Implement `Store[dict[str, Any]]` interface
  - [ ] Add connection pooling
  - [ ] Set up database migrations
  - [ ] Test all CRUD operations

- [ ] Add authentication checks in store methods:
  - [ ] Verify `user_id` in context
  - [ ] Check user owns thread before loading
  - [ ] Validate user permissions for operations
  - [ ] Add audit logging

### 2.2 Authentication & Authorization

- [ ] Implement user authentication system
  - [ ] Choose auth method (OAuth, JWT, session-based)
  - [ ] Create login/logout endpoints
  - [ ] Add auth middleware to FastAPI
  - [ ] Protect all sensitive endpoints

- [ ] Add authorization rules
  - [ ] Define user roles (admin, user, viewer)
  - [ ] Implement role-based access control
  - [ ] Restrict document access by role
  - [ ] Add admin-only endpoints if needed

### 2.3 API Security

- [ ] Add rate limiting
  ```python
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  ```

- [ ] Enable HTTPS/TLS
  - [ ] Obtain SSL certificate
  - [ ] Configure reverse proxy (nginx/caddy)
  - [ ] Redirect HTTP to HTTPS
  - [ ] Test SSL configuration

- [ ] Restrict CORS origins
  - [ ] Remove `*` from `CORS_ORIGINS`
  - [ ] Set specific production domains only
  - [ ] Test CORS with frontend

- [ ] Add security headers
  ```python
  @app.middleware("http")
  async def add_security_headers(request, call_next):
      response = await call_next(request)
      response.headers["X-Content-Type-Options"] = "nosniff"
      response.headers["X-Frame-Options"] = "DENY"
      response.headers["X-XSS-Protection"] = "1; mode=block"
      return response
  ```

- [ ] Input validation and sanitization
  - [ ] Validate all request parameters
  - [ ] Sanitize user inputs
  - [ ] Add request size limits
  - [ ] Implement input schema validation

### 2.4 File Upload Security (if enabled)

- [ ] Validate file types and extensions
- [ ] Implement file size limits
- [ ] Add virus/malware scanning
- [ ] Store files outside web root
- [ ] Use cloud storage (S3, Azure Blob, GCS)
- [ ] Generate unique, non-guessable filenames
- [ ] Implement access control for file downloads

---

## Phase 3: Infrastructure Setup

### 3.1 Database

- [ ] Provision production database
  - [ ] Choose provider (AWS RDS, Azure Database, etc.)
  - [ ] Configure appropriate instance size
  - [ ] Enable automated backups
  - [ ] Set up backup retention policy
  - [ ] Configure high availability if needed

- [ ] Database security
  - [ ] Use strong passwords
  - [ ] Restrict network access
  - [ ] Enable encryption at rest
  - [ ] Enable encryption in transit
  - [ ] Set up database monitoring

### 3.2 Application Hosting

**Option A: Container-based (Recommended)**

- [ ] Create `Dockerfile`
- [ ] Build container image
- [ ] Push to container registry
- [ ] Deploy to container platform:
  - [ ] AWS ECS/Fargate
  - [ ] Azure Container Apps
  - [ ] Google Cloud Run
  - [ ] Kubernetes cluster

**Option B: Platform-as-a-Service**

- [ ] Deploy to platform:
  - [ ] Heroku
  - [ ] Railway
  - [ ] Render
  - [ ] Fly.io

**Option C: Virtual Machine**

- [ ] Provision VM
- [ ] Install Python 3.11+
- [ ] Install dependencies
- [ ] Configure systemd service
- [ ] Set up reverse proxy (nginx)

### 3.3 Frontend Hosting (if applicable)

- [ ] Build frontend for production
  ```bash
  cd frontend && npm run build
  ```

- [ ] Deploy static files to:
  - [ ] AWS S3 + CloudFront
  - [ ] Azure Static Web Apps
  - [ ] Netlify
  - [ ] Vercel
  - [ ] Same server as backend

### 3.4 Domain & DNS

- [ ] Register domain name
- [ ] Configure DNS records
  - [ ] A record for apex domain
  - [ ] CNAME for www subdomain
  - [ ] A/CNAME for API subdomain
- [ ] Set up CDN (optional)
- [ ] Test DNS propagation

---

## Phase 4: Monitoring & Logging

### 4.1 Application Monitoring

- [ ] Set up error tracking
  - [ ] Sentry, Rollbar, or similar
  - [ ] Configure DSN in environment
  - [ ] Test error reporting

- [ ] Add performance monitoring
  - [ ] New Relic, DataDog, or similar
  - [ ] Track response times
  - [ ] Monitor resource usage

- [ ] Set up uptime monitoring
  - [ ] UptimeRobot, Pingdom, or similar
  - [ ] Monitor health endpoint
  - [ ] Configure alerts

### 4.2 Logging

- [ ] Configure structured logging
  ```python
  import logging
  logging.basicConfig(
      level=LOG_LEVEL,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  ```

- [ ] Set up log aggregation
  - [ ] CloudWatch Logs (AWS)
  - [ ] Azure Monitor (Azure)
  - [ ] Cloud Logging (GCP)
  - [ ] Logstash/ELK stack

- [ ] Configure log retention
- [ ] Set up log search and filtering
- [ ] Create log-based alerts

### 4.3 Metrics & Dashboards

- [ ] Track key metrics:
  - [ ] Request count per endpoint
  - [ ] Response times (p50, p95, p99)
  - [ ] Error rates
  - [ ] Active threads/conversations
  - [ ] Document search latency
  - [ ] OpenAI API usage and costs

- [ ] Create dashboards for:
  - [ ] System health
  - [ ] User activity
  - [ ] Error trends
  - [ ] Cost tracking

---

## Phase 5: Testing

### 5.1 Functional Testing

- [ ] Test all API endpoints
  - [ ] ChatKit protocol endpoint
  - [ ] Documents list endpoint
  - [ ] Document file serving
  - [ ] Citations endpoint
  - [ ] Health check endpoint

- [ ] Test chatbot functionality
  - [ ] Create new thread
  - [ ] Send messages
  - [ ] Verify responses
  - [ ] Check citations
  - [ ] Test error handling

- [ ] Test document retrieval
  - [ ] Query each document
  - [ ] Verify correct chunks returned
  - [ ] Check citation accuracy

### 5.2 Performance Testing

- [ ] Load testing
  - [ ] Simulate concurrent users
  - [ ] Test with realistic message volume
  - [ ] Measure response times
  - [ ] Identify bottlenecks

- [ ] Stress testing
  - [ ] Test system limits
  - [ ] Verify graceful degradation
  - [ ] Check error handling under load

### 5.3 Security Testing

- [ ] Penetration testing
  - [ ] SQL injection attempts
  - [ ] XSS attempts
  - [ ] CSRF testing
  - [ ] Authentication bypass attempts

- [ ] Access control testing
  - [ ] Test unauthorized access
  - [ ] Verify role restrictions
  - [ ] Test session management

- [ ] Dependency scanning
  ```bash
  # Python
  pip-audit

  # JavaScript
  npm audit
  ```

### 5.4 User Acceptance Testing

- [ ] Test with customer stakeholders
- [ ] Verify responses meet requirements
- [ ] Check branding and UI
- [ ] Validate document coverage
- [ ] Gather feedback and iterate

---

## Phase 6: Deployment

### 6.1 Pre-Deployment

- [ ] Review all checklist items above
- [ ] Backup current production (if updating)
- [ ] Create deployment plan with rollback steps
- [ ] Schedule deployment window
- [ ] Notify stakeholders

### 6.2 Deployment Steps

- [ ] Deploy database changes (if any)
- [ ] Deploy backend application
  - [ ] Update environment variables
  - [ ] Deploy new code
  - [ ] Run database migrations
  - [ ] Verify health check

- [ ] Deploy frontend (if applicable)
  - [ ] Build production assets
  - [ ] Deploy to CDN/hosting
  - [ ] Clear CDN cache
  - [ ] Verify frontend loads

- [ ] Test end-to-end
  - [ ] Send test message
  - [ ] Verify response
  - [ ] Check citations
  - [ ] Test document preview

### 6.3 Post-Deployment

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Review logs for issues
- [ ] Test from different locations/devices
- [ ] Verify with customer
- [ ] Update documentation

---

## Phase 7: Ongoing Maintenance

### 7.1 Regular Tasks

- [ ] **Daily**
  - [ ] Check error logs
  - [ ] Monitor uptime
  - [ ] Review user activity

- [ ] **Weekly**
  - [ ] Review performance metrics
  - [ ] Check OpenAI API costs
  - [ ] Test key functionality

- [ ] **Monthly**
  - [ ] Update dependencies
  - [ ] Security patch review
  - [ ] Backup verification
  - [ ] Cost optimization review

- [ ] **Quarterly**
  - [ ] User feedback review
  - [ ] Document updates
  - [ ] Performance optimization
  - [ ] Disaster recovery test

### 7.2 Document Updates

- [ ] Process for adding new documents
  ```bash
  # 1. Add files to backend/data/
  # 2. Run upload script
  python scripts/setup-vector-store.py
  # 3. Test new documents
  # 4. Deploy updated documents.py
  ```

- [ ] Version control for documents
- [ ] Approval workflow for updates
- [ ] Testing before deployment

### 7.3 Incident Response

- [ ] Create incident response plan
- [ ] Define severity levels
- [ ] Establish on-call rotation
- [ ] Document escalation procedures
- [ ] Set up alerting channels

---

## Phase 8: Compliance & Legal

### 8.1 Data Privacy

- [ ] Review data retention policies
- [ ] Implement data deletion procedures
- [ ] Add privacy policy
- [ ] Add terms of service
- [ ] GDPR compliance (if applicable)
  - [ ] User data export
  - [ ] Right to be forgotten
  - [ ] Consent management

### 8.2 Audit & Compliance

- [ ] Enable audit logging
- [ ] Define data retention periods
- [ ] Set up compliance monitoring
- [ ] Document security controls
- [ ] Complete security questionnaires

---

## Quick Reference: Production Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-proj-production-key
VECTOR_STORE_ID=vs_production_id

# Configuration
ASSISTANT_NAME="Customer Production Bot"
ASSISTANT_MODEL=gpt-4.1-mini
ASSISTANT_TEMPERATURE=0.3
MAX_SEARCH_RESULTS=5

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8002
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING

# Database (if using)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Monitoring
SENTRY_DSN=https://...
```

---

## Rollback Plan

If issues arise after deployment:

1. **Identify the issue**
   - Check error logs
   - Review monitoring dashboards
   - Test affected functionality

2. **Quick fixes**
   - Roll back environment variables
   - Restart services
   - Clear caches

3. **Full rollback**
   - Revert to previous code version
   - Restore database backup if needed
   - Clear CDN cache
   - Notify users

4. **Post-mortem**
   - Document what went wrong
   - Identify root cause
   - Update deployment procedures
   - Add prevention measures

---

## Success Criteria

Deployment is successful when:

- ✅ Health endpoint returns 200
- ✅ Users can create threads and send messages
- ✅ Assistant responses include accurate citations
- ✅ Document preview works
- ✅ Error rate < 1%
- ✅ Response time < 2 seconds for 95% of requests
- ✅ No critical errors in logs
- ✅ Customer stakeholder approval

---

## Support & Escalation

**For issues during deployment:**

1. Check logs: `tail -f logs/app.log`
2. Verify environment: Review `.env` file
3. Test API: `curl http://localhost:8002/knowledge/health`
4. Review documentation: `README.md`, `backend/app/config.py`
5. OpenAI status: https://status.openai.com/

**Emergency contacts:**

- Technical lead: [Name/Contact]
- DevOps team: [Contact]
- Customer stakeholder: [Contact]

---

**Last updated:** [Date]
**Deployment version:** 1.0.0
**Checklist maintainer:** [Name]
