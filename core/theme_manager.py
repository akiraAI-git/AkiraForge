from pathlib import Path

class ThemeManager:
    _stylesheet = None
    
    @staticmethod
    def get_stylesheet():
        if ThemeManager._stylesheet is None:
            theme_file = Path(__file__).parent.parent / "resources" / "styles" / "dark_theme.qss"
            try:
                with open(theme_file, 'r') as f:
                    ThemeManager._stylesheet = f.read()
            except Exception as e:
                print(f"Warning: Could not load theme file: {e}")
                ThemeManager._stylesheet = ""
        return ThemeManager._stylesheet
    
    @staticmethod
    def apply_to_app(app):
        stylesheet = ThemeManager.get_stylesheet()
        if stylesheet:
            app.setStyleSheet(stylesheet)
    
    @staticmethod
    def apply_to_widget(widget):
        stylesheet = ThemeManager.get_stylesheet()
        if stylesheet:
            widget.setStyleSheet(stylesheet)
