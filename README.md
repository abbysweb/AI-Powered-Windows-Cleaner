# AI-Powered-Windows-Cleaner

An intelligent Windows storage optimization and system maintenance assistant that safely analyzes disk usage, identifies unnecessary files, explains cleanup recommendations in natural language, and performs intelligent system maintenance.

Unlike traditional cleaners, the application **justifies every recommendation**, **estimates risk**, and **learns from user preferences**.

## Core Architecture

This project uses an **Industry-Standard Hybrid Architecture**:
- **Native Windows Host (GUI & Scanner):** PySide6 GUI and Python scanning engine running locally with Admin privileges to access the filesystem and manage Windows components.
- **Containerized AI Backend (Podman):** A lightweight FastAPI container running the AI models (Ollama/Llama) and vector databases. This keeps the Windows host clean of heavy ML dependencies while exposing a local API for the GUI to interact with.

## Features

- **System Scanner (Phase 1 & 2):** Scans disk usage, RAM, CPU, OS details, and categorizes storage waste (Windows Temp, Downloads, Recycle Bin).
- **Premium Dashboard (Phase 3):** A sleek, dark-mode PySide6 interface that visualizes storage usage (via PyQtGraph) and health scores.
- **Safe Cleaning Engine (Phase 4):** A quarantine-first cleaning engine. High-risk deletions are backed up locally for safe rollback.
- **AI Advisor Client (Phase 5):** Natural language justifications for why files are marked for deletion, powered by a local Podman AI container.
- **Deep File Scanner (Phase 6):** Advanced hashlib-based duplicate file scanning and customizable large file detection.
- **Personalization Engine (Phase 7):** SQLite-based history logs, custom user preferences, and dynamic ignore lists.
- **Automated Maintenance (Phase 8):** Background scheduling using Windows Task Scheduler integration and native PyInstaller packaging.

## Installation & Setup

### Prerequisites
- Windows 10/11
- Python 3.12+
- Podman Desktop (for the AI Container)

### 1. Host Setup
Clone the repository and install the native dependencies:

```powershell
git clone https://github.com/abbysweb/AI-Windows-Health-Copilot.git
cd AI-Windows-Health-Copilot
pip install -r requirements.txt
```

### 2. AI Backend Setup (Podman)
Ensure Podman is running, then spin up the backend API:

```powershell
podman-compose up -d --build
```

### 3. Run the Copilot
Run the desktop application:

```powershell
python app.py
```

## Development Lifecycle

This project is strictly bound to a **Phase-Based Development Lifecycle**.
Every phase undergoes:
- Architecture Design
- Implementation
- 100% Type Checking (Mypy)
- 100% Linting (Ruff/Black)
- Unit Testing (Pytest)
- A formally generated **Diagnosis Report** before approval.

## Roadmap

- [x] **Phase 1: Project Initialization & Architecture Design**
- [x] **Phase 2: Core Scanning Engine**
- [x] **Phase 3: Premium UI/UX Dashboard**
- [x] **Phase 4: Safe Cleaning Engine & Rollback**
- [x] **Phase 5: Advanced AI Layer (Ollama + Llama)**
- [x] **Phase 6: Deep File Scanning (Large Files & Duplicates)**
- [x] **Phase 7: Personalization & Learning Engine (SQLite, Ignore Lists)**
- [x] **Phase 8: Final Polish, Scheduling, & Packaging**
- [x] **Phase 9: Premium UI Overhaul (Multi-view, Charts, AI Chat)**

---
## Author

**Abdullah Al Mamun**  
BSc, MSc - Software Engineering  
TU Wien (Vienna, Austria) & Daffodil International University  
mamun.swe.de@gmail.com | [https://github.com/abbysweb](https://github.com/abbysweb)  
ORCID: [0009-0006-7473-0024](https://orcid.org/0009-0006-7473-0024)
