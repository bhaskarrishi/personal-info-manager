# Personal Information Manager

A comprehensive, secure desktop application for managing personal information including passwords, financial data, insurance policies, real estate properties, documents, and reminders.

## Features

### Core Modules
1. **Profile Management** - Manage personal profile information, contact details, and photo
2. **Password Vault** - Securely store and manage passwords with encryption
3. **Financial Investments** - Track investments, stocks, and financial assets
4. **Insurance Policies** - Manage insurance policies with expiry tracking
5. **Real Estate** - Track property ownership, mortgages, and valuations
6. **Passport/Citizenship** - Store passport and citizenship documents for family members
7. **Health Cards** - Manage health insurance cards for the family
8. **Services/Billing** - Track subscriptions, bills, and payment schedules
9. **Reminders/To-Do** - Organize tasks with priorities and due dates

### Security Features
- **Bcrypt Password Hashing** - All user passwords are securely hashed
- **Fernet Encryption** - Sensitive data like password vault entries are encrypted
- **SQL Injection Prevention** - Parameterized queries throughout
- **Session Management** - Secure session handling with timeout
- **Input Validation** - Comprehensive validation for all user inputs

## Technology Stack

- **Frontend**: PyQt6 - Modern Python GUI framework
- **Backend**: Python 3.8+
- **Database**: MySQL 8.0+
- **Encryption**: Cryptography library (Fernet), bcrypt
- **Environment Management**: python-dotenv

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/bhaskarrishi/personal-info-manager.git
cd personal-info-manager
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

1. **Create MySQL Database**:
```bash
mysql -u root -p
```

```sql
CREATE DATABASE personal_info_manager;
EXIT;
```

2. **Import Database Schema**:
```bash
mysql -u root -p personal_info_manager < database/schema.sql
```

### Step 5: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your configuration:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=personal_info_manager
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
SECRET_KEY=your_secret_encryption_key
```

**Important**: Generate a secure SECRET_KEY for encryption:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Step 6: Run the Application

```bash
python src/main.py
```

## Usage

1. **First Time Setup**:
   - Launch the application
   - Click "Sign Up" to create a new account
   - Enter username, email, and password
   - Accept terms and conditions
   - Log in with your credentials

2. **Navigation**:
   - Use the left sidebar to navigate between modules
   - Each module provides Add, Edit, and Delete functionality
   - Use search and filter features to find specific entries

3. **Password Vault**:
   - Store passwords securely with encryption
   - Use the password generator for strong passwords
   - Copy passwords to clipboard (auto-clears after use)
   - Organize by categories

4. **Reminders**:
   - Set due dates for tasks
   - Assign priorities (Low, Medium, High)
   - Mark tasks as complete
   - Filter by category and status

## Project Structure

```
personal-info-manager/
├── config.py                 # Application configuration
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
├── database/
│   ├── schema.sql           # MySQL database schema
│   └── db_manager.py        # Database connection manager
└── src/
    ├── main.py              # Application entry point
    ├── app.py               # Main application class
    ├── auth/
    │   ├── __init__.py
    │   ├── login_window.py      # Login screen
    │   ├── signup_window.py     # Registration screen
    │   └── auth_manager.py      # Authentication logic
    ├── ui/
    │   ├── __init__.py
    │   └── main_dashboard.py    # Main dashboard
    ├── modules/
    │   ├── __init__.py
    │   ├── profile_window.py
    │   ├── password_vault_window.py
    │   ├── financial_window.py
    │   ├── insurance_window.py
    │   ├── real_estate_window.py
    │   ├── passport_window.py
    │   ├── health_cards_window.py
    │   ├── services_window.py
    │   └── reminders_window.py
    ├── utils/
    │   ├── __init__.py
    │   ├── encryption.py        # Encryption utilities
    │   ├── validators.py        # Input validation
    │   └── styles.py            # UI stylesheets
    └── dialogs/
        ├── __init__.py
        ├── add_edit_dialog.py
        ├── confirmation_dialog.py
        └── password_generator_dialog.py
```

## Screenshots

*Screenshots will be added here once the application is running*

## Future Enhancements

- [ ] Document attachment support
- [ ] Data export functionality (CSV, PDF)
- [ ] Automatic backup system
- [ ] Multi-language support
- [ ] Mobile companion app
- [ ] Cloud sync capabilities
- [ ] Two-factor authentication
- [ ] Biometric authentication support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Never commit your `.env` file to version control
- Keep your SECRET_KEY secure and unique
- Regularly update dependencies for security patches
- Use strong passwords for the application
- Regularly backup your database

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Acknowledgments

- PyQt6 for the excellent GUI framework
- MySQL for reliable database management
- The Python community for amazing libraries

---

**Note**: This application stores sensitive personal information. Ensure you:
- Use strong encryption keys
- Keep regular backups
- Secure your database credentials
- Use the application on trusted devices only
