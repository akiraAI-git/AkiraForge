# 🚀 Akira Forge

**A comprehensive AI-powered desktop application framework with enterprise-grade security, multi-LLM support, and complete device authentication.**

![Version](https://img.shields.io/badge/version-1.1.3-experimental-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-32%2F33%20passing-green)

## 📋 Features

### 🤖 AI & LLM Integration
- **Multi-LLM Router** - Seamlessly switch between Groq, OpenAI, Claude, and other providers
- **Intelligence Memory System** - Persistent AI memory for user interactions and preferences
- **Offline AI Store** - Works without internet connection using local models
- **Smart Agent System** - Groq-powered AI agents for advanced tasks

### 🔐 Security & Authentication
- **Device Login Manager** - Multi-device authentication with fingerprinting
- **Firewall Manager** - Network security and request filtering
- **Encryption Suite** - AES-256 encryption, SHA-256 hashing, secure key generation
- **Audit Logging** - Complete audit trails with encrypted logs
- **Request Verification** - HMAC-SHA256 request signing and verification
- **Rate Limiting** - DDoS protection and rate limiting per user/device
- **Crash Recovery** - Automatic backup and recovery system

### 🖥️ Advanced GUI
- **Qt-based UI** - Modern, responsive interface with Neon theme
- **Home Screen** - Dashboard with system overview
- **Login & Auth UI** - Secure authentication interface
- **Admin Dashboard** - Complete admin panel with user management
- **Builder Window** - Project generation and code building
- **Vault System** - Secure credential storage and management
- **Role-based Access** - Admin, Developer, and User roles

### 📊 Enterprise Features
- **Project Generator** - Auto-generate projects from templates
- **Configuration Management** - Centralized app configuration
- **Notes & Memory** - Persistent note-taking with encryption
- **Metrics Collector** - Performance monitoring and analytics
- **Database Pool** - Connection pooling for database access
- **Location Detection** - Geographic location awareness
- **Premium System** - Subscription and feature management

### 🧪 Testing & Monitoring
- **Comprehensive Test Suite** - 33 automated tests across 10 categories
- **Performance Monitoring** - Track response times and system health
- **Automated CI/CD** - GitHub Actions pipeline for continuous testing
- **Email Alerts** - SendGrid integration for notifications

## 🛠️ Installation

### Requirements
- Python 3.10+
- pip package manager
- MySQL/MariaDB (for full database features)
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/akiraAI-git/AkiraForge.git
cd AkiraForge

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📺 Running Tests

```bash
# Run full test suite
python tester_everything.py

# Expected output: 32/33 tests passing (AIMemory warning is environmental)
```

## 📁 Project Structure

```
AkiraForge/
├── main.py                    # Application entry point
├── core/                      # Core application modules
│   ├── ai_memory.py          # AI memory persistence
│   ├── groq_agent.py         # Groq AI integration
│   ├── login_manager.py      # Authentication system
│   ├── crypto.py             # Encryption utilities
│   ├── audit_logger.py       # Audit logging
│   ├── db.py                 # Database access
│   └── ... (40+ more modules)
├── windows/                  # GUI windows and dialogs
│   ├── home_screen.py       # Home dashboard
│   ├── login_window.py      # Login interface
│   ├── admin_dashboard_window.py  # Admin panel
│   └── ... (20+ more windows)
├── resources/               # UI styles and assets
├── tester_everything.py     # Comprehensive test suite
└── create_version_branch.py # Version management
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# AI & LLM
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
DEFAULT_LLM=groq

# Database
DB_HOST=localhost
DB_USER=forge_user
DB_PASSWORD=your_password
DB_NAME=akiraforge

# Email Notifications (optional)
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=noreply@akiraforge.local

# Security
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_32_byte_hex_key
```

### Application Config

Edit `config.toml` for application-level settings:

```toml
[app]
name = "Akira Forge"
version = "1.1.3"

[security]
enable_audit_logging = true
enable_crash_recovery = true

[features]
enable_offline_mode = true
enable_memory_system = true
```

## 🚀 Development

### Creating a New Version Branch

```bash
python create_version_branch.py create experimental
# This creates 1.1.4(experimental) or increments appropriately
```

### Version Scheme

- **Master (stable)** - Production-ready releases (1.1(stable))
- **Experimental** - Beta/testing releases (1.1.3(experimental))
- **Unstable** - Development releases

## 🔐 Security

- No hardcoded credentials (uses environment variables)
- No API keys in source code
- All sensitive data encrypted at rest
- Complete audit logging
- Request signing and verification
- Rate limiting and DDoS protection

See [SECURITY.md](SECURITY.md) for detailed security documentation.

## 📝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Support

For issues, feature requests, or questions:
1. Check [existing issues](https://github.com/akiraAI-git/AkiraForge/issues)
2. Create a new issue with detailed description
3. Include test output and error messages

## 📊 Test Results

Latest test run: **32/33 tests PASSED** (96.97%)
- ✅ Database connectivity and operations
- ✅ Project generation from templates
- ✅ API key validation
- ✅ Encryption and cryptography
- ✅ Multi-LLM router
- ✅ Authentication and login
- ✅ Notes and memory systems
- ✅ Security compliance
- ✅ Configuration management
- ✅ File I/O operations
- ✅ Performance benchmarks
- ⚠️ AIMemory initialization (environmental - expected in fresh installs)

## 🎯 Roadmap

- [ ] Web UI dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Real-time collaboration features
- [ ] Advanced analytics
- [ ] Plugin system
- [ ] Self-hosted cloud option

## 💡 Credits

Built by the AkiraForge team with ❤️

---

**Status**: Production-ready (1.1.3 experimental testing phase)
