DB_HOST = os.getenv("HOME_DB_HOST") or os.getenv("OFFICE_DB_HOST") or "localhost"
    DB_USER = os.getenv("DB_USER", "forge_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "akira_forge")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

    AKIRA_ENCRYPTION_KEY = os.getenv("AKIRA_ENCRYPTION_KEY")

    MACHINE_UUID = os.getenv("MACHINE_UUID")
    OFFLINE_ADMIN_HASH = os.getenv("OFFLINE_ADMIN_HASH")

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@akiraforge.com")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "1800"))

    @staticmethod
    def validate():
        errors = []

        if not SecurityConfig.DB_PASSWORD:
            errors.append("DB_PASSWORD not set in environment")

        if not SecurityConfig.GROQ_API_KEY:
            errors.append("GROQ_API_KEY not set in environment")

        if not SecurityConfig.OFFLINE_ADMIN_HASH:
            errors.append("OFFLINE_ADMIN_HASH not set in environment")

        if not SecurityConfig.STRIPE_SECRET_KEY:
            print("[WARNING] STRIPE_SECRET_KEY not set - premium features disabled")

        if errors:
            print("[ERROR] Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("[OK] All security configuration validated")
        return True

    @staticmethod
    def print_config_status():
        print("\n[CONFIG] Security Configuration Status:")
        print(f"   Database: {bool(SecurityConfig.DB_PASSWORD)} [OK]" if SecurityConfig.DB_PASSWORD else "   Database: [MISSING]")
        print(f"   Groq API: {bool(SecurityConfig.GROQ_API_KEY)} [OK]" if SecurityConfig.GROQ_API_KEY else "   Groq API: [MISSING]")
        print(f"   Stripe: {bool(SecurityConfig.STRIPE_SECRET_KEY)} [OK]" if SecurityConfig.STRIPE_SECRET_KEY else "   Stripe: [optional]")
        print(f"   Admin Hash: {bool(SecurityConfig.OFFLINE_ADMIN_HASH)} [OK]" if SecurityConfig.OFFLINE_ADMIN_HASH else "   Admin Hash: [MISSING]")
        print(f"   Encryption Key: {bool(SecurityConfig.AKIRA_ENCRYPTION_KEY)} [OK]" if SecurityConfig.AKIRA_ENCRYPTION_KEY else "   Encryption Key: [Optional]")
        print(f"   Debug Mode: {'ON (development)' if SecurityConfig.DEBUG_MODE else 'OFF (production)'}")
        print()

SecurityConfig.validate()
