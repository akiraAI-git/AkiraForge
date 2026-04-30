#!/usr/bin/env python3
"""
Akira Forge Main Application
=============================

Entry point for the Akira Forge application.
Handles window management, user authentication, and session tracking.

Usage:
    python main.py

Environment Variables:
    See .env file for configuration
"""

import sys
import json
import logging
import threading
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure log directory exists
log_dir = Path.home() / '.akiraforge'
log_dir.mkdir(parents=True, exist_ok=True)

# Setup logging with proper configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'app.log')
    ]
)

# Setup logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    from PyQt6.QtWidgets import QApplication
    QT_IMPL = "PyQt6"
except ImportError:
    try:
        from PySide6.QtWidgets import QApplication
        QT_IMPL = "PySide6"
    except ImportError as e:
        logger.critical("Could not import Qt bindings (PyQt6 or PySide6)")
        print("ERROR: Could not import Qt bindings package (PyQt6 or PySide6).")
        print("Install with: pip install PyQt6")
        sys.exit(1)

# Local imports
from core.db import init_db
from core.theme_manager import ThemeManager
from core.device_login_manager import DeviceLoginManager
from core.maintenance_scheduler import start_maintenance_scheduler, stop_maintenance_scheduler
from core.audit_logger import get_audit_logger
from core.session_tracker import SessionTracker
from core.rate_limiter import RateLimiter
from core.window_factory import WindowFactory
from core.metrics_collector import MetricsCollector
from core.settings_manager import SettingsManager
from core.crash_recovery_manager import CrashRecoveryManager

class AkiraForgeApp:
    """Main application controller for Akira Forge.
    
    Manages:
    - Window lifecycle and switching
    - User authentication and sessions
    - Audit logging and security
    - Service initialization
    """
    
    # Window lazy-loading cache
    _window_cache = {}
    
    def __init__(self):
        """Initialize the application."""
        self.app = QApplication([])
        ThemeManager.apply_to_app(self.app)
        
        # Core services
        self.audit_logger = get_audit_logger()
        self.session_tracker = SessionTracker()
        self.rate_limiter = RateLimiter()
        self.metrics_collector = MetricsCollector()
        self.settings_manager = SettingsManager()
        self.crash_recovery_manager = CrashRecoveryManager()
        
        # Register custom rate limit actions
        self._configure_rate_limits()
        
        # Current session state
        self.current_username: str = None
        self.current_user_id: str = None  # Stores role type (admin/user)
        self.current_session_id: str = None
        
        # Active windows
        self.login_window = None
        self.home_window = None
        self.admin_window = None
        self.builder_window = None
        self.vault_window = None
        self.assistant_window = None
        
        # Setup cleanup on exit
        self.app.aboutToQuit.connect(self.cleanup)
        
        logger.info(f"Application initialized (Qt: {QT_IMPL})")
    
    def _configure_rate_limits(self) -> None:
        """Configure custom rate limits for features."""
        rate_limits = {
            "BUILDER_ACCESS": (100, 3600),        # 100 per hour
            "ASSISTANT_ACCESS": (50, 3600),       # 50 per hour
        }
        
        for action, (count, window) in rate_limits.items():
            self.rate_limiter.set_limit(action, count, window)
            logger.info(f"Rate limit set: {action} = {count} per {window}s")

    def _show_admin_dashboard(self) -> None:
        """Show admin dashboard window."""
        try:
            AdminDashboardWindow = self._lazy_load_window(
                'windows.admin_dashboard_window',
                'AdminDashboardWindow'
            )
            self.admin_window = AdminDashboardWindow(
                self.current_username,
                back_to_forge_callback=self.show_home_screen
            )
            self.admin_window.show()
            logger.info(f"Admin dashboard shown for user '{self.current_username}'")
        except Exception as e:
            logger.error(f"Failed to show admin dashboard: {e}", exc_info=True)

    def _lazy_load_window(self, module_path: str, class_name: str):
        """
        Lazy load a window class.
        
        Args:
            module_path: Module path (e.g., 'windows.login_window')
            class_name: Class name to import
            
        Returns:
            Window class
        """
        try:
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load {class_name} from {module_path}: {e}")
            raise

    def on_login_success(self, username: str, role: str):
        """
        Handle successful login.
        
        Args:
            username: Authenticated username
            role: User role (admin/user)
        """
        try:
            # Update session state
            self.current_username = username
            self.current_user_id = role
            
            # Create session tracking
            self.current_session_id = self.session_tracker.create_session(
                username=username
            )
            
            # Start metrics collection
            self.metrics_collector.start_session()
            
            # Log login event
            self.audit_logger.log_action(
                username=username,
                action="LOGIN",
                details={
                    "role": role,
                    "session_id": self.current_session_id,
                    "qt_framework": QT_IMPL
                },
                is_important=True
            )
            
            logger.info(f"User '{username}' logged in with role '{role}'")
            
            # Save session state for crash recovery
            self.crash_recovery_manager.save_session_state(username, self.current_session_id)
            
            # Close login window
            if self.login_window:
                self.login_window.close()
                self.login_window = None
            
            # Show appropriate home screen
            if role == "admin":
                self._show_admin_dashboard()
            else:
                self.show_home_screen()
        
        except Exception as e:
            logger.error(f"Error handling login: {e}", exc_info=True)
            self.crash_recovery_manager.save_crash_log("LoginError", str(e), traceback.format_exc())
            raise

    def show_home_screen(self):
        """
        Display home/dashboard screen.
        
        Closes all other windows and shows the main home screen.
        """
        try:
            # Close other windows
            if self.admin_window:
                self.admin_window.close()
                self.admin_window = None
            if self.builder_window:
                self.builder_window.close()
                self.builder_window = None
            if self.vault_window:
                self.vault_window.close()
                self.vault_window = None
            if self.assistant_window:
                self.assistant_window.close()
                self.assistant_window = None
            
            # Load and show home screen
            HomeScreen = self._lazy_load_window(
                'windows.home_screen',
                'HomeScreen'
            )
            self.home_window = HomeScreen(
                username=self.current_username,
                callback_launch_forge=self.show_builder_window,
                callback_launch_vault=self.show_vault_window,
                callback_launch_assistant=self.show_assistant_window,
                callback_launch_playboard=self.show_playboard_window,
                callback_logout=self.do_logout,
                callback_update_profile=self.save_user_profile
            )
            self.home_window.show()
            logger.debug(f"Home screen shown for user '{self.current_username}'")
        
        except Exception as e:
            logger.error(f"Failed to show home screen: {e}", exc_info=True)

    def show_builder_window(self):
        """Show builder/project window (async)."""
        try:
            allowed, message = self.rate_limiter.check_rate_limit(
                self.current_username, "BUILDER_ACCESS"
            )
            if not allowed:
                logger.warning(f"Builder access rate limited for {self.current_username}")
                return
            
            self.metrics_collector.record_feature_access("BUILDER_ACCESS")
            
            self.audit_logger.log_action(
                username=self.current_username,
                action="BUILDER_ACCESS",
                details={"session_id": self.current_session_id}
            )
            
            # Launch window asynchronously
            launch_thread = threading.Thread(
                target=self._create_and_show_builder,
                daemon=True
            )
            launch_thread.start()
        
        except Exception as e:
            logger.error(f"Failed to show builder window: {e}", exc_info=True)
    
    def _create_and_show_builder(self):
        """Create and show builder window (runs in background thread)."""
        try:
            import time
            start_time = time.time()
            
            self.builder_window = WindowFactory.create_window(
                'windows.builder_window',
                'BuilderWindow',
                self.current_username,
                self.show_home_screen
            )
            
            launch_time = (time.time() - start_time) * 1000  # Convert to ms
            self.metrics_collector.record_window_launch("builder", launch_time)
            
            self.builder_window.show()
            if self.home_window:
                self.home_window.hide()
            
            logger.debug(f"Builder window shown for user '{self.current_username}' ({launch_time:.2f}ms)")
        
        except Exception as e:
            logger.error(f"Error creating builder window: {e}", exc_info=True)

    def show_vault_window(self):
        """Show vault/secure storage window (async)."""
        try:
            allowed, message = self.rate_limiter.check_rate_limit(
                self.current_username, "VAULT_ACCESS"
            )
            if not allowed:
                logger.warning(f"Vault access rate limited for {self.current_username}")
                return
            
            self.metrics_collector.record_feature_access("VAULT_ACCESS")
            
            self.audit_logger.log_action(
                username=self.current_username,
                action="VAULT_ACCESS",
                details={"session_id": self.current_session_id},
                is_important=True
            )
            
            # Launch window asynchronously
            launch_thread = threading.Thread(
                target=self._create_and_show_vault,
                daemon=True
            )
            launch_thread.start()
        
        except Exception as e:
            logger.error(f"Failed to show vault window: {e}", exc_info=True)
    
    def _create_and_show_vault(self):
        """Create and show vault window (runs in background thread)."""
        try:
            import time
            start_time = time.time()
            
            self.vault_window = WindowFactory.create_window(
                'windows.vault_window',
                'VaultWindow',
                self.current_username,
                self.show_home_screen
            )
            
            launch_time = (time.time() - start_time) * 1000  # Convert to ms
            self.metrics_collector.record_window_launch("vault", launch_time)
            
            self.vault_window.show()
            if self.home_window:
                self.home_window.hide()
            
            logger.debug(f"Vault window shown for user '{self.current_username}' ({launch_time:.2f}ms)")
        
        except Exception as e:
            logger.error(f"Error creating vault window: {e}", exc_info=True)

    def show_assistant_window(self):
        """Show AI assistant window (async)."""
        try:
            allowed, message = self.rate_limiter.check_rate_limit(
                self.current_username, "ASSISTANT_ACCESS"
            )
            if not allowed:
                logger.warning(f"Assistant access rate limited for {self.current_username}")
                return
            
            self.metrics_collector.record_feature_access("ASSISTANT_ACCESS")
            
            self.audit_logger.log_action(
                username=self.current_username,
                action="ASSISTANT_ACCESS",
                details={"session_id": self.current_session_id}
            )
            
            # Launch window asynchronously
            launch_thread = threading.Thread(
                target=self._create_and_show_assistant,
                daemon=True
            )
            launch_thread.start()
        
        except Exception as e:
            logger.error(f"Failed to show assistant window: {e}", exc_info=True)
    
    def _create_and_show_assistant(self):
        """Create and show assistant window (runs in background thread)."""
        try:
            import time
            start_time = time.time()
            
            self.assistant_window = WindowFactory.create_window(
                'windows.ai_assistant_window',
                'AIAssistantWindow',
                self.current_username,
                self.show_home_screen
            )
            
            launch_time = (time.time() - start_time) * 1000  # Convert to ms
            self.metrics_collector.record_window_launch("assistant", launch_time)
            
            self.assistant_window.show()
            if self.home_window:
                self.home_window.hide()
            
            logger.debug(f"Assistant window shown for user '{self.current_username}' ({launch_time:.2f}ms)")
        
        except Exception as e:
            logger.error(f"Error creating assistant window: {e}", exc_info=True)

    def show_playboard_window(self):
        """
        Show playboard/project management window.
        
        Currently not implemented - placeholder for future feature.
        """
        logger.info("Playboard window requested (not yet implemented)")

    def do_logout(self):
        """
        Handle user logout.
        
        Logs the action, clears session, and returns to login screen.
        """
        try:
            # End metrics collection
            session_duration = self.metrics_collector.end_session()
            
            # Log logout event
            self.audit_logger.log_action(
                username=self.current_username,
                action="LOGOUT",
                details={
                    "session_id": self.current_session_id,
                    "session_duration": session_duration
                },
                is_important=True
            )
            
            # End session tracking
            if self.current_session_id:
                self.session_tracker.end_session(self.current_session_id)
            
            # Clear device login
            DeviceLoginManager.clear_device_login(self.current_username)
            
            # Clear crash recovery state
            self.crash_recovery_manager.clear_session_state()
            
            logger.info(f"User '{self.current_username}' logged out (duration: {session_duration:.2f}s)")
            
            # Close windows and return to login
            if self.home_window:
                self.home_window.close()
                self.home_window = None
            
            self.current_username = None
            self.current_user_id = None
            self.current_session_id = None
            
            self.show_login_window()
        
        except Exception as e:
            logger.error(f"Error during logout: {e}", exc_info=True)
            self.show_login_window()

    def save_user_profile(self, username: str, profile_data: dict) -> bool:
        """
        Save user profile data.
        
        Args:
            username: Username
            profile_data: Profile information (bio, picture, etc)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile_dir = Path.home() / ".akiraforge"
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            # Save profile JSON
            profile_file = profile_dir / f"{username}_profile.json"
            with open(profile_file, 'w') as f:
                json.dump(
                    {
                        "bio": profile_data.get("bio", ""),
                        "updated_at": Path(profile_file).stat().st_mtime if profile_file.exists() else None
                    },
                    f,
                    indent=2
                )
            
            # Save profile picture if provided
            if profile_data.get("profile_picture"):
                pic_src = profile_data["profile_picture"]
                pic_path = profile_dir / f"{username}_profile.jpg"
                
                with open(pic_src, 'rb') as src:
                    with open(pic_path, 'wb') as dst:
                        dst.write(src.read())
                
                logger.debug(f"Profile picture saved for '{username}'")
            
            # Log profile update
            self.audit_logger.log_action(
                username=username,
                action="PROFILE_UPDATE",
                details={"session_id": self.current_session_id}
            )
            
            logger.info(f"Profile saved for user '{username}'")
            return True
        
        except Exception as e:
            logger.error(f"Error saving profile for '{username}': {e}", exc_info=True)
            return False

    def show_login_window(self):
        """Display the login window."""
        try:
            LoginWindow = self._lazy_load_window(
                'windows.login_window',
                'LoginWindow'
            )
            self.login_window = LoginWindow(self.on_login_success)
            self.login_window.show()
            logger.debug("Login window displayed")
        except Exception as e:
            logger.error(f"Failed to show login window: {e}", exc_info=True)
            sys.exit(1)

    def cleanup(self):
        """
        Clean up resources on application exit.
        
        Closes all windows, stops services, saves metrics and recovery state.
        """
        try:
            logger.info("Starting application cleanup...")
            
            # Save application metrics
            metrics = self.metrics_collector.get_metrics()
            logger.info(f"Application metrics: {metrics}")
            
            # Stop services
            stop_maintenance_scheduler()
            
            # Log logout if user was logged in
            if self.current_username and self.current_session_id:
                try:
                    # End metrics
                    session_duration = self.metrics_collector.end_session()
                    
                    self.audit_logger.log_action(
                        username=self.current_username,
                        action="APP_EXIT",
                        details={
                            "session_id": self.current_session_id,
                            "session_duration": session_duration,
                            "metrics": metrics
                        },
                        is_important=True
                    )
                    self.session_tracker.end_session(self.current_session_id)
                    
                    # Clear recovery state on clean exit
                    self.crash_recovery_manager.clear_session_state()
                except Exception as e:
                    logger.warning(f"Failed to log app exit: {e}")
            
            # Close all windows
            windows_to_close = [
                ("login", self.login_window),
                ("home", self.home_window),
                ("admin", self.admin_window),
                ("builder", self.builder_window),
                ("vault", self.vault_window),
                ("assistant", self.assistant_window),
            ]
            
            for window_name, window in windows_to_close:
                if window:
                    try:
                        window.close()
                    except Exception as e:
                        logger.warning(f"Error closing {window_name} window: {e}")
            
            logger.info("Application cleanup completed")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)

    def run(self):
        """
        Run the application.
        
        Initializes services and displays the login screen.
        Checks for crash recovery state and restores if available.
        """
        try:
            logger.info(f"Starting Akira Forge application (Qt: {QT_IMPL})")
            
            # Check for crash recovery
            recovery_state = self.crash_recovery_manager.load_session_state()
            if recovery_state:
                logger.info(f"Found recovery state for user '{recovery_state.get('username')}'")
                # Could auto-recover session here, but for now just log it
            
            # Show login window first
            self.show_login_window()
            
            # Initialize services in background
            def init_services():
                """Initialize database and services."""
                try:
                    logger.info("Initializing database...")
                    init_db()
                    logger.info("Database initialized successfully")
                except Exception as e:
                    logger.warning(
                        f"Database initialization failed (offline mode available): {e}"
                    )
                
                try:
                    logger.info("Starting maintenance scheduler...")
                    start_maintenance_scheduler()
                    logger.info("Maintenance scheduler started")
                except Exception as e:
                    logger.error(f"Failed to start maintenance scheduler: {e}", exc_info=True)
                
                # Cleanup old crash logs
                cleaned = self.crash_recovery_manager.cleanup_old_crashes(keep_count=5)
                if cleaned > 0:
                    logger.debug(f"Cleaned up {cleaned} old crash logs")
            
            # Run initialization in daemon thread
            init_thread = threading.Thread(target=init_services, daemon=True)
            init_thread.start()
            
            # Start application
            logger.info("Application ready")
            sys.exit(self.app.exec())
        
        except Exception as e:
            logger.critical(f"Fatal error in application: {e}", exc_info=True)
            self.crash_recovery_manager.save_crash_log(
                "FatalError",
                str(e),
                traceback.format_exc()
            )
            sys.exit(1)

if __name__ == "__main__":
    AkiraForgeApp().run()