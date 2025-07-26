# 🚀 Business Lead Automation System

A comprehensive lead generation and outreach automation system designed for Turkish businesses. Automate Google Maps scraping, website analysis, and WhatsApp messaging with built-in compliance features.

## ✨ Features

- 🗺️ **Google Maps Scraping**: Automated business data collection with anti-detection
- 🌐 **Website Detection**: Analyze website existence and quality
- 💬 **WhatsApp Automation**: Send personalized messages via WhatsApp Web
- 📝 **Message Templates**: Pre-built Turkish business templates
- 📊 **Excel Integration**: Complete data management with automatic backups
- ⚡ **Rate Limiting**: Built-in compliance and safety features
- 📈 **Analytics Dashboard**: Advanced filtering, sorting, and statistics
- 🎯 **Lead Qualification**: Identify high-value prospects automatically

## 🛠️ Installation

### Prerequisites

- Python 3.13+
- Chrome Browser (for Google Maps scraping)
- Tkinter (for GUI)

### Setup

1. **Clone the repository:**

```bash
git clone git@github.com:batuserifcann/Lead-Generation-Gmap.git
cd Lead-Generation-Gmap
```

2. **Create virtual environment:**

```bash
python -m venv lead_automation_env
source lead_automation_env/bin/activate  # Linux/Mac
# or
lead_automation_env\Scripts\activate     # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Install system dependencies:**

**Arch Linux:**

```bash
sudo pacman -S tk google-chrome
```

**Ubuntu/Debian:**

```bash
sudo apt-get install python3-tk google-chrome-stable
```

**Windows:**

- Download and install Chrome browser
- Tkinter comes with Python

## 🚀 Quick Start

### GUI Application

```bash
python main.py
```

### CLI Demo (Test without GUI)

```bash
python cli_demo.py
```

## 📖 Usage Guide

### 1. Data Management

- **Load Excel File**: Import existing business data
- **Create New File**: Start with a fresh database
- **Search & Filter**: Find specific businesses by industry, location, or status

### 2. Google Maps Scraping

- Enter search terms (e.g., "restaurants in Istanbul")
- Set location and search parameters
- Click "Start Scraping" to collect business data
- Monitor progress and review results

### 3. Website Analysis

- Load businesses with website URLs
- Click "Check Websites" to analyze website status
- Review quality assessments and contact information

### 4. WhatsApp Messaging

- Click "Connect WhatsApp" and scan QR code
- Customize message templates
- Select target businesses (e.g., those without websites)
- Send personalized messages with rate limiting

### 5. Analytics & Reporting

- View comprehensive statistics
- Filter by industry, location, or contact status
- Export filtered data to Excel
- Track campaign performance

## 📝 Message Templates

The system includes pre-built Turkish templates for:

- **Restaurant Website Offers**: Specialized for food businesses
- **Construction Services**: Tailored for construction companies
- **General Business**: Universal template for any industry
- **Follow-up Messages**: For continued engagement

Templates support personalization with business data:

- `{business_name}` - Business name
- `{location}` - Business location
- `{industry}` - Business industry
- `{address}` - Full address
- `{phone}` - Phone number

## ⚙️ Configuration

### Rate Limiting Settings

- **Messages per hour**: Default 20 (configurable)
- **Delay between messages**: Default 30 seconds
- **Anti-detection**: Random delays and user agents

### Data Storage

- **Format**: Excel (.xlsx)
- **Backups**: Automatic timestamped backups
- **Location**: `data/` directory

## 🔒 Compliance Features

- **Rate Limiting**: Prevents spam and account restrictions
- **Anti-Detection**: Randomized delays and browser fingerprinting
- **Data Validation**: Input sanitization and error handling
- **Audit Logging**: Complete activity tracking
- **Session Management**: Proper cleanup and resource management

## 📊 System Architecture

```
├── Core Modules
│   ├── Excel Manager (Data storage)
│   ├── Google Maps Scraper (Data collection)
│   ├── Website Detector (Website analysis)
│   ├── WhatsApp Automation (Messaging)
│   ├── Message Templates (Template management)
│   └── Rate Limiter (Compliance)
├── GUI Application
│   ├── Data Management Interface
│   ├── Scraping Controls
│   ├── Website Analysis Tools
│   ├── WhatsApp Integration
│   └── Analytics Dashboard
└── Utilities
    ├── Configuration Management
    ├── Logging System
    └── Input Validation
```

## 🧪 Testing

### Run All Tests

```bash
python test_final_integration.py
```

### Individual Component Tests

```bash
python test_phase2.py  # Data Management
python test_phase3.py  # Google Maps Scraping
python test_phase4.py  # Website Detection
python test_phase5.py  # WhatsApp Automation
```

### CLI Demo

```bash
python cli_demo.py
```

## 📁 Project Structure

```
Lead-Generation-Gmap/
├── core/                   # Core functionality modules
├── gui/                    # GUI application
├── utils/                  # Utility functions
├── tests/                  # Unit tests
├── data/                   # Data storage (created automatically)
├── main.py                 # GUI application entry point
├── cli_demo.py            # Command-line demo
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚠️ Important Notes

- **WhatsApp Web**: Requires manual QR code scanning for first login
- **Google Maps**: Requires Chrome browser installation
- **Rate Limits**: Adjust settings based on your usage requirements
- **Data Backups**: Automatic backups are created before major operations
- **Compliance**: Always respect platform terms of service and local regulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the logs in `data/logs/app.log`
2. Run the CLI demo to test individual components
3. Ensure all dependencies are installed correctly
4. Verify Chrome browser is available for scraping

## 🎯 Use Cases

- **Digital Agencies**: Automate lead generation for web design services
- **Marketing Companies**: Scale outreach campaigns efficiently
- **Sales Teams**: Identify and contact prospects systematically
- **Business Development**: Build targeted prospect databases
- **Freelancers**: Streamline client acquisition process

---

**🚀 Ready to automate your lead generation? Get started with the CLI demo or launch the full GUI application!**
