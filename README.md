# 🚀 PADAS Clipboard Manager

> *Part of the **PADAS DevStudio** ecosystem.*

**PADAS Clipboard Manager** is a lightweight, zero-popup productivity utility built with **Python 3.14** and **PyQt6**. It automates multi-slot data management, selective formatting, and instant cloud image uploads to eliminate repetitive copy-paste tasks.

📱 **Featured on LinkedIn:** [Connect on LinkedIn](https://www.linkedin.com/in/G-Martire/)

---

## ⚡ Quick Overview

- **Cloud Image Upload (`Shift + Alt + E`):** Uploads the latest clipboard screenshot directly to Google Drive and automatically pastes the shareable link in under 2 seconds.
- **Multi-Slot Memory:** Assign, format, lock, and paste multi-slot clipboard contents instantly without modal popups.
- **Portable & Standalone:** Runs as a portable `.exe` for Windows with zero dependencies required.

---

## 📖 Documentation & Hotkey Guide

For the full list of hotkeys, technical architecture, and directory structure, check the detailed guide:

👉 **[Read the Full Technical Documentation & Hotkey Guide (DOCS.md)](DOCS.md)**

---

## 📦 Quick Start

### Download Executable
Grab the ready-to-use portable `.exe` from the **[Releases](../../releases)** section.

### Developer Setup
```powershell
git clone [https://github.com/G-Martire/PADAS-Clipboard-Manager.git](https://github.com/G-Martire/PADAS-Clipboard-Manager.git)
cd PADAS-Clipboard-Manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python applicazioni/multi_copia/multi_copia.py
```

---

## 🔮 Roadmap & Future Developments

- [ ] **Internationalization (i18n):** Multi-language interface support (English / Italian).
- [ ] **Custom Hotkeys Engine:** Fully rebindable keyboard shortcuts tailored to different layout formats.
- [ ] **Cross-Platform Compilation:** Automated builds for macOS and Linux.

## MIT License - see LICENSE for details.
