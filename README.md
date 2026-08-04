# AI Windows Health Copilot

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
- **AI Advisor (Upcoming):** Natural language justifications for why files are marked for deletion.
- **Automated Maintenance (Upcoming):** Background scheduling using Windows Task Scheduler integration.

## Installation & Setup

### Prerequisites
- Windows 10/11
- Python 3.12+
- Podman Desktop (for the AI Container)

### 1. Host Setup
Clone the repository and install the native dependencies:

```powershell
git clone https://github.com/abbysweb/AI-Powered-Windows-Cleaner.git
cd AI-Powered-Windows-Cleaner
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

See `AGENTS.md` for the strict contributor guidelines.

## Roadmap

- [x] **Phase 1:** Project Initialization & Hybrid Architecture
- [x] **Phase 2:** Core Scanning Engine
- [x] **Phase 3:** Premium GUI Skeleton & Dashboard
- [x] **Phase 4:** Safe Cleaning Engine & Rollback
- [ ] **Phase 5:** Advanced AI Layer (Ollama + Llama)
- [ ] **Phase 6:** Background Scheduler
- [ ] **Phase 7:** UI Finalization & Charting
- [ ] **Phase 8:** Packaging & Distribution

---
*Developed as a premium, industry-standard Windows utility.*
