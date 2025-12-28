"""
Main application entry point for Personal Information Manager.
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.app import PersonalInfoManager
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    try:
        # Create application instance
        app = QApplication(sys.argv)
        app.setApplicationName(Config.APP_NAME)
        app.setApplicationVersion(Config.APP_VERSION)
        
        # Set application-wide style
        app.setStyle('Fusion')
        
        logger.info(f"Starting {Config.APP_NAME} v{Config.APP_VERSION}")
        
        # Create and show main application window
        window = PersonalInfoManager()
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            'Application Error',
            f'A critical error occurred:\n{str(e)}\n\nPlease check the log file for details.'
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
