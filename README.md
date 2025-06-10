# Burn After Reading

🔐 Enterprise-grade secure messaging service with self-destructing messages and files.

## Project Overview

A production-ready web service implementing the "burn after reading" philosophy. Users can securely share sensitive text or files via one-time-use links with optional password protection and flexible expiration policies.

## ✨ Core Features (Phase 2 Complete)

- ✅ **Self-Destructing Messages** - Text notes deleted after access with multiple expiration options
- ✅ **Secure File Sharing** - Binary file uploads up to 5MB with streaming downloads  
- ✅ **Password Protection** - bcrypt-secured optional password protection
- ✅ **Custom Expiration** - Read-once, 1 hour, 24 hours, or 7 days policies
- 🎯 **End-to-End Encryption** - Planned for Phase 4 (client-side encryption)
- ✅ **RESTful API** - 7 endpoints with comprehensive error handling and testing

## 🚀 Quick Start

### Production Deployment
```bash
docker build -t burn-after-reading .
docker run -p 8000:8000 burn-after-reading
```

### Development Setup
```bash
# Recommended: Install with uv
uv sync
uv run uvicorn src.main:app --reload --port 8001

# Alternative: Install with pip
pip install -e .
uvicorn src.main:app --reload
```

### Health Check
```bash
curl http://localhost:8001/health
# {"status": "healthy", "version": "0.2.0"}
```

## 📊 Project Status

- ✅ **Phase 1**: MVP Backend (Completed)
- ✅ **Phase 2**: Feature Expansion (Completed 2025-06-10)
- 🎯 **Phase 3**: Frontend Development (Ready to start)
- 🔄 **Phase 4**: Advanced Security & Polish
- 🚀 **Phase 5**: Production Deployment

## 🧪 Testing

```bash
# Run comprehensive API tests
uv run python test_phase2_api.py

# Database migration (if upgrading from v1)
uv run python migrate_to_v2.py migrate
```

---

*This project follows the **RIPER-5+ Multidimensional Thinking Protocol** for systematic development.*
