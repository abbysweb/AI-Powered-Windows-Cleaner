# AI-Powered Windows Cleaner

A modern, intelligent system utility designed to optimize and clean your Windows machine. Built with Python and PySide6, this cleaner not only removes traditional temporary files and caches but also provides smart features to identify large files, duplicates, and unnecessary startup items.

## Features

- **System Cleaning**: Safely removes Windows temporary files, user temporary files, recycle bin contents, delivery optimization cache, shader caches, and thumbnail caches.
- **Browser Caches**: Clears cache data for major browsers including Google Chrome, Microsoft Edge, Brave, Firefox, and Waterfox.
- **AI-Powered Analysis**: 
  - Duplicate file finder
  - Large file analyzer
  - Startup items analyzer
- **Task Scheduling**: Easily schedule automatic background cleaning (e.g., Weekly, Daily, or On Start).
- **Customizable Settings**: Choose between Quick, Standard, and Deep cleaning profiles, set maximum file age limits, and configure specific file/path exclusions.
- **Intuitive GUI**: A sleek and responsive graphical user interface built with PySide6.

## Requirements

- Python 3.10 or higher
- Administrator Privileges (required for scanning and cleaning certain system locations)
- Windows Operating System

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abbysweb/AI-Powered-Windows-Cleaner.git
   cd AI-Powered-Windows-Cleaner
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To launch the graphical interface, simply run the main script:
```bash
python main.py
```

### Auto-Clean Mode
You can also run the cleaner in a headless auto-clean mode, which is used primarily by the background task scheduler:
```bash
python main.py --auto-clean
```

## Logs
The application generates detailed logs located in the `logs/` directory for troubleshooting and tracking cleaning sessions.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
