# Rand Engine Documentation

**Complete technical documentation for `rand-engine` v0.6.1**

Welcome to the comprehensive documentation hub for rand-engine, a high-performance Python library for generating realistic synthetic data.

---

## 📚 Documentation Index

### 🚀 Getting Started

- **[Main README](../README.md)** - Quick start, installation, and overview
  - Installation via pip
  - Pre-built templates
  - Core features overview
  - Real-world use cases

### 📖 Complete Guides

#### **[API Reference](./API_REFERENCE.md)** - Full API Documentation
Complete reference for all public APIs, methods, and parameters.

**Contents:**
- Core Classes (DataGenerator, RandSpecs)
- Generation Methods (Numeric, Selection, Temporal)
- **Constraints & Referential Integrity** ⭐ NEW
- File Writers (Batch, Stream)
- Database Handlers (DuckDB, SQLite)
- Validation & Error Messages
- Logging Configuration
- Type Hints

**Length:** 1,400+ lines | **Audience:** Developers, API consumers

---

#### **[Constraints Guide](./CONSTRAINTS.md)** - PK/FK System
In-depth guide to the constraints system for referential integrity.

**Contents:**
- Core Concepts (Primary Keys, Foreign Keys, Watermarks)
- Simple PK → FK Examples
- Composite Keys (Multi-column)
- 3-Level Relationships (Categories → Products → Orders)
- Complete Workflows
- Best Practices & Pitfalls
- DuckDB vs SQLite
- FAQ

**Length:** 900+ lines | **Audience:** Data Engineers, architects

**Key Topics:**
- ✅ Creating checkpoint tables
- ✅ Referencing parent records
- ✅ Temporal windows (watermarks)
- ✅ Composite primary keys
- ✅ Multi-level hierarchies

---

#### **[Examples Gallery](../EXAMPLES.md)** - Production-Ready Examples
50+ real-world examples demonstrating all features.

**Contents:**
- Quick Start (30 seconds to first DataFrame)
- Pre-Built Templates (10 specs)
- Core Features (Generation, Streaming, Export)
- **Advanced: Constraints & Referential Integrity**
- Industry Use Cases (E-commerce, Finance, HR, IoT, Web)
- Engineering & Testing (ETL, Load Testing, DB Integration)
- Performance Optimization (Benchmarks, Memory, Parallel)

**Length:** 1,647 lines | **Audience:** All users

**Highlights:**
- ✅ Copy-paste ready code
- ✅ Complete workflows
- ✅ Integrity verification examples
- ✅ Real fixtures used in tests

---

#### **[Logging Guide](./LOGGING.md)** - Logging Configuration
How to enable, configure, and use logging in rand-engine.

**Contents:**
- Default Behavior (Silent Mode)
- Enabling Logs (INFO, DEBUG levels)
- Available Log Messages
- Use Cases (Development, Production, Debugging)
- Configuration Examples

**Length:** 450+ lines | **Audience:** Developers, DevOps

**Key Topics:**
- ✅ RandEngineLogger class
- ✅ Integration logs (DuckDB, SQLite)
- ✅ Custom handlers
- ✅ Disabling logs

---

#### **[Writing Files Guide](./WRITING_FILES.md)** - File Export Complete Reference
Comprehensive guide to file writing modes, formats, and compression.

**Contents:**
- Batch vs Streaming Modes
- Supported Formats (CSV, JSON, Parquet)
- Compression Options (All Codecs)
- File Naming Patterns
- Overwrite vs Append Modes
- Complete API Reference
- Practical Examples
- Performance Considerations
- Troubleshooting

**Length:** 800+ lines | **Audience:** Data Engineers, developers

**Key Topics:**
- ✅ Single vs multiple files
- ✅ Streaming with timeout/trigger
- ✅ CSV/JSON external compression (gzip, bz2, zip, xz)
- ✅ Parquet internal compression (snappy, zstd, lz4, brotli)
- ✅ File extensions and naming patterns
- ✅ Parallel processing patterns

---

### 🔧 Technical References

#### **[Changelog](../CHANGELOG.md)** - Version History
Release notes and breaking changes for all versions.

#### **[Project Instructions](.github/copilot-instructions.md)** - AI Agent Instructions
Architecture overview, conventions, and patterns for contributors.

---

## 🎯 Quick Navigation

### By User Type

**Data Engineers:**
1. Start: [Main README](../README.md)
2. Learn: [Constraints Guide](./CONSTRAINTS.md)
3. Explore: [Examples Gallery](../EXAMPLES.md)
4. Reference: [API Reference](./API_REFERENCE.md)

**QA Engineers:**
1. Start: [Main README](../README.md) → Pre-Built Templates
2. Test: [Examples Gallery](../EXAMPLES.md) → Load Testing
3. Reference: [API Reference](./API_REFERENCE.md) → Validation

**Data Scientists:**
1. Start: [Main README](../README.md) → Quick Start
2. Explore: [Examples Gallery](../EXAMPLES.md) → Industry Use Cases
3. Reference: [API Reference](./API_REFERENCE.md) → Generation Methods

**Backend Developers:**
1. Start: [Main README](../README.md) → Integration
2. Learn: [Examples Gallery](../EXAMPLES.md) → Database Integration
3. Configure: [Logging Guide](./LOGGING.md)

---

### By Feature

**Constraints (PK/FK):**
- Guide: [CONSTRAINTS.md](./CONSTRAINTS.md)
- Examples: [EXAMPLES.md](../EXAMPLES.md) → Constraints Section
- API: [API_REFERENCE.md](./API_REFERENCE.md) → Constraints Section

**File Export:**
- Complete Guide: [WRITING_FILES.md](./WRITING_FILES.md)
- Examples: [EXAMPLES.md](../EXAMPLES.md) → File Export
- API: [API_REFERENCE.md](./API_REFERENCE.md) → File Writers

**Streaming Data:**
- Examples: [EXAMPLES.md](../EXAMPLES.md) → Streaming Data
- API: [API_REFERENCE.md](./API_REFERENCE.md) → Stream Writer

**Database Integration:**
- Examples: [EXAMPLES.md](../EXAMPLES.md) → Database Integration
- API: [API_REFERENCE.md](./API_REFERENCE.md) → Database Handlers

**Validation:**
- Guide: [API_REFERENCE.md](./API_REFERENCE.md) → Validation
- Examples: [EXAMPLES.md](../EXAMPLES.md) → Spec Validation

**Logging:**
- Complete Guide: [LOGGING.md](./LOGGING.md)
- API: [API_REFERENCE.md](./API_REFERENCE.md) → Logging

---

## 📊 Documentation Statistics

| Document | Lines | Status | Last Updated |
|----------|-------|--------|--------------|
| [README.md](../README.md) | 770 | ✅ Complete | Oct 21, 2025 |
| [API_REFERENCE.md](./API_REFERENCE.md) | 1,400+ | ✅ Complete | Oct 21, 2025 |
| [CONSTRAINTS.md](./CONSTRAINTS.md) | 900+ | ✅ Complete | Oct 21, 2025 |
| [EXAMPLES.md](../EXAMPLES.md) | 1,647 | ✅ Complete | Oct 21, 2025 |
| [LOGGING.md](./LOGGING.md) | 450+ | ✅ Complete | Oct 21, 2025 |
| [WRITING_FILES.md](./WRITING_FILES.md) | 800+ | ✅ Complete | Oct 21, 2025 |
| **Total** | **5,967+** | ✅ **Complete** | v0.6.1 |

---

## 🔍 Search Tips

**Find Specific Topics:**

```bash
# Search across all docs
grep -r "constraint" docs/ README.md EXAMPLES.md

# Find method documentation
grep -A 10 "def method_name" docs/API_REFERENCE.md

# Find examples
grep -B 5 -A 20 "Example:" EXAMPLES.md
```

---

## 🤝 Contributing

Found an issue or want to improve docs?

1. **Typos/Errors:** [Open an issue](https://github.com/marcoaureliomenezes/rand_engine/issues)
2. **Examples:** Submit examples via [GitHub Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)
3. **API Docs:** Ensure type hints and docstrings are accurate in code

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/marcoaureliomenezes/rand_engine/issues)
- **Discussions:** [GitHub Discussions](https://github.com/marcoaureliomenezes/rand_engine/discussions)
- **Email:** marcourelioreislima@gmail.com

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

**Built with ❤️ for the data community**

Last Updated: October 21, 2025 (v0.6.1)
