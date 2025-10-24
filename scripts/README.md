# Scripts & Utilities

This folder contains helper scripts and utilities for the Amplify KPI Calculator Bot.

## 📁 Scripts Overview

### Setup & Validation
- **`setup_helper.py`** - Initial setup helper that checks dependencies and creates directory structure
- **`final_validation.py`** - Comprehensive system validation (recommended for testing)
- **`validate_system.py`** - Detailed validation suite with unit tests

### Examples
- **`examples_usage_updated.py`** - Current examples using the Amplify-specific CSV export system
- **`examples_usage.py`** - Legacy examples from the original generic KPI bot
- **`quick_start_your_sheets.py`** - Quick start guide for Google Sheets integration

### Testing
- **`test_bot.py`** - Test script for the bot functionality
- **`api_test.py`** - **NEW!** Comprehensive Tableau API testing and exploration
- **`quick_tableau_test.py`** - **NEW!** Quick Tableau API connection verification
- **`TABLEAU_API_GUIDE.md`** - **NEW!** Complete guide for Tableau API testing

## 🚀 Quick Start

### 1. Setup the System
```bash
python scripts/setup_helper.py
```
This will:
- Check dependencies
- Create required directories (exports/, scorecards/, results/)
- Generate sample export files
- Test Google Sheets connection (optional)

### 2. Validate Installation
```bash
python scripts/final_validation.py
```
This runs a complete system test to ensure everything is working correctly.

### 3. See Examples
```bash
python scripts/examples_usage_updated.py
```
Shows various usage examples with the current Amplify system.

## 📝 Notes

- Most scripts should be run from the **project root directory**
- The main application is `main.py` in the root directory
- Place your CSV export files in the `exports/` folder (not in scripts/)
- Generated scorecards will be saved in the `scorecards/` folder

## 🔧 For Development

If you're modifying the system:
1. Use `validate_system.py` for detailed unit testing
2. Use `final_validation.py` for quick end-to-end validation
3. Check `examples_usage_updated.py` for current API usage patterns
