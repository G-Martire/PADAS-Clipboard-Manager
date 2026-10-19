# 📚 PADAS Clipboard Manager - Technical Guide & Architecture

This document provides a detailed breakdown of hotkeys, application structure, and design principles for **PADAS Clipboard Manager**.

---

## ⌨️ Full Hotkey Table

All commands operate globally in the background without modal window focus:

| Command / Hotkey | Action |
| :--- | :--- |
| **`Shift + Alt + E`** | Upload last screenshot to Google Drive & paste shareable link |
| **`Shift + Alt + Z` + `[Slot]`** | Copy selection and assign directly to target slot |
| **`Shift + Alt + X` + `[Slot]`** | Assign current `Ctrl+C` clipboard buffer to slot |
| **`Shift + Alt + F` + `[Slot]`** | Copy selective formatting (opens options panel) |
| **`Shift + Alt + G` + `[Preset]` + `[Slot]`** | Apply preset formatting to slot on the fly |
| **`Shift + Alt + S`** | Show / Hide main table interface |
| **`Shift + Alt + D` + `[Preset]`** | Paste content using specified preset format |
| **`Shift + Alt + Q`** | Lock / Unlock target slot (prevents overwrite) |
| **`Shift + Alt + W` + `[Slot]`** | Clear specific unlocked slot |
| **`Shift + Alt + W` + `Q` + `E`** | Clear all unlocked slots in memory |
| **`Shift + Alt + E` + `[Slot 1]` + `[Slot 2]`** | Sequential multi-paste from Slot 1 to Slot 2 |
| **`Shift + Alt + A` + `[Slot 1]` + `[Cols]`** | Split multi-slot content across columns |
| **`Shift + Alt + M` + `[Slot 1]` + `[Slot 2]`** | Batch create multiple files from slot range |
| **`Shift + Alt + R`** | Coordinate-based multi-paste |

---

## 📁 Application File Structure

```text
multi_copia/
├── clipboard/
│   ├── actions_core/
│   │   ├── clipboard_actions.py
│   │   ├── coordinate_utils.py
│   │   ├── drive_uploader.py
│   │   ├── file_maker_actions.py
│   │   ├── keyboard_grid.py
│   │   ├── multi_paste_actions.py
│   │   ├── paste_actions.py
│   │   ├── selective_format.py
│   │   ├── split_save_actions.py
│   │   └── text_splitter.py
│   ├── dialogs_core/
│   │   ├── format_filter.py
│   │   ├── make_files_dialog.py
│   │   ├── matrix_preview.py
│   │   ├── multipaste_logic.py
│   │   ├── multipaste_options.py
│   │   ├── notifications.py
│   │   └── split_save_config.py
│   ├── gui_core/
│   │   ├── gui_core.py
│   │   ├── gui_dialogs.py
│   │   ├── gui_layout.py
│   │   ├── gui_menus.py
│   │   └── gui_table.py
│   ├── keyboard_map_core/
│   │   ├── config_dialog.py
│   │   ├── map_actions.py
│   │   ├── map_core.py
│   │   ├── map_multipaste.py
│   │   ├── map_ui.py
│   │   └── virtual_key.py
│   ├── manager_core/
│   │   ├── base_manager.py
│   │   ├── clipboard_listener.py
│   │   ├── lock_clear_operations.py
│   │   ├── menu_toolbar_events.py
│   │   ├── slot_operations.py
│   │   └── table_keyboard_controller.py
│   ├── actions.py
│   ├── dialogs.py
│   ├── hotkeys.py
│   ├── io.py
│   └── signals.py
├── main.py
├── requirements_MCI.txt
└── requirements_avanzato_MCI.txt
```

---

## 🏗️ Architectural Philosophy & Design Principles

### Anti-Monolithic Modular Design
The project intentionally rejects single-file monolithic scripts. Whenever a module exceeds **~500 lines of code**, it is refactored into domain-specific sub-modules with highly targeted files (averaging **~120 lines each**).

### Core Benefits:
1. **Maintainability & Clean Architecture:** Isolating single responsibilities into specialized sub-folders (`actions_core`, `dialogs_core`, `gui_core`, `keyboard_map_core`, `manager_core`) keeps the codebase readable and easy to navigate.
2. **Resource Efficiency:** Allows selective imports, reducing memory footprint and startup overhead.
3. **AI-Assisted Workflow Optimization:** Keeps file contexts small and modular, drastically reducing token generation costs and avoiding LLM context dilution when updating specific features.
4. **Team Collaboration:** Prevents merge conflicts and allows multiple developers to work simultaneously on different features without touching the same central file.
