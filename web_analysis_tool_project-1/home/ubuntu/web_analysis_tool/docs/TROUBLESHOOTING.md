# Web Analysis Tool - Troubleshooting Guide

## 1. Introduction

This troubleshooting guide is designed to help you resolve common issues you might encounter while installing or using the Web Analysis Tool. If you don't find a solution here, please review the application logs (see Section 3) for more detailed error messages, which can provide further clues.

## 2. Installation Issues

### 2.1. Python Not Found or Incorrect Version

*   **Symptom:** Commands like `python -m venv venv` or `python gui/main_app.py` fail with errors like "python: command not found" or messages indicating an incompatible Python version.
*   **Solution:**
    1.  Ensure Python 3.8 or higher is installed. You can check your version with `python --version` or `python3 --version`.
    2.  Make sure Python's installation directory (and its `Scripts` subdirectory on Windows) is added to your system's PATH environment variable.
    3.  If you have multiple Python versions, you might need to use `python3` instead of `python` in commands.
    4.  Reinstall Python if necessary, ensuring the "Add Python to PATH" option is checked during installation.

### 2.2. GnuPG (GPG) Not Found or Not Working

*   **Symptom:** The PGP Management tab shows errors, key generation fails, or logs indicate "GnuPG binary not found" or "Failed to initialize GPG".
*   **Solution:**
    1.  **Verify GnuPG Installation:** Open a new terminal/command prompt and type `gpg --version`. If this command fails, GnuPG is not installed correctly or not in your PATH.
    2.  **Install GnuPG:** Follow the instructions in `INSTALLATION.md` for your operating system (Gpg4win for Windows, Homebrew for macOS, package manager for Linux).
    3.  **Check PATH:** Ensure the directory containing the `gpg` executable is in your system's PATH environment variable. You may need to restart your terminal or system after updating the PATH.
    4.  **Specify GPG Binary Path (Advanced):** If GPG is installed in a non-standard location, future versions of the tool might allow specifying the path to the GPG binary in the settings. For now, ensure it's in the PATH.
    5.  **GPG Home Directory:** The tool attempts to use a dedicated GPG home directory (e.g., `~/.web_analysis_tool_data/gnupg_home`). Ensure there are no permission issues with creating or accessing this directory.

### 2.3. `pip install -r requirements.txt` Fails

*   **Symptom:** Errors occur during the installation of Python packages.
*   **Solution:**
    1.  **Activate Virtual Environment:** Ensure your Python virtual environment is activated before running `pip install`.
    2.  **Internet Connection:** Check your internet connection, as pip needs to download packages.
    3.  **Build Tools for `lxml` or other packages:** Some packages (like `lxml` on certain systems) might require compilation and need system-level build tools or development libraries (e.g., `python3-dev`, `libxml2-dev`, `libxslt1-dev` on Debian/Ubuntu; Xcode Command Line Tools on macOS). Check the specific error message for clues about the failing package and search for its installation prerequisites for your OS.
    4.  **Permissions:** If not using a virtual environment (not recommended), you might need administrator/sudo privileges to install packages globally (e.g., `sudo pip install -r requirements.txt`). However, using a virtual environment is strongly preferred to avoid this.
    5.  **Outdated pip/setuptools:** Try upgrading pip and setuptools: `pip install --upgrade pip setuptools`.

### 2.4. PyQt6 Installation Issues

*   **Symptom:** Errors specifically related to `PyQt6` during `pip install`.
*   **Solution:**
    1.  Ensure you are using a compatible Python version (3.8+).
    2.  `PyQt6` provides wheels for most common platforms, so direct compilation is rare. If issues occur, check the PyPi page for `PyQt6` for any specific OS notes or try installing a specific wheel if available for your platform.
    3.  Ensure your `pip` is up to date.

## 3. Runtime Issues

### 3.1. Application Fails to Start

*   **Symptom:** Running `python gui/main_app.py` results in an immediate error or the GUI does not appear.
*   **Solution:**
    1.  **Check Console Output:** Look for error messages in the terminal/command prompt where you launched the application. These often provide direct clues.
    2.  **Check Application Logs:** The tool logs its activity and errors. Look for `app.log` in the application's data directory (e.g., `~/.web_analysis_tool_data/logs/app.log`).
    3.  **Dependencies:** Ensure all dependencies from `requirements.txt` were installed correctly in the active virtual environment.
    4.  **Python Version:** Double-check you are running with the correct Python version.

### 3.2. Data Collection Fails for a Specific URL

*   **Symptom:** The tool reports an error when trying to collect data from a website.
*   **Solution:**
    1.  **Check URL:** Ensure the URL is correct and accessible in a regular web browser.
    2.  **Internet Connection:** Verify your internet connectivity.
    3.  **Website Blocking/Firewall:** The target website might be blocking automated requests (e.g., based on User-Agent, IP address, or request frequency). This tool is for educational use on permitted sites; aggressive scraping can lead to blocks.
    4.  **HTTP Errors (4xx/5xx):** A 403 Forbidden error means you don't have access. A 404 Not Found means the page doesn't exist. 5xx errors indicate server-side problems on the target website.
    5.  **SSL/TLS Issues:** For `https://` sites, there might be SSL certificate issues. The `requests` library usually handles this well, but complex SSL configurations or outdated system SSL libraries could cause problems.
    6.  **Timeout:** The website might be too slow to respond. The tool has a timeout, which might be configurable in future versions.
    7.  **Dynamic Content:** The data collector primarily fetches and parses static HTML. If a website heavily relies on JavaScript to load content, the collector might not see all of it. More advanced scraping techniques (like using a headless browser, e.g., Playwright or Selenium) would be needed for such sites, which is beyond the current scope of this tool's basic collector.
    8.  **Review Logs:** Check `app.log` for detailed error messages from the `DataCollector` module.

### 3.3. Backend Analysis Shows Limited or No Results

*   **Symptom:** The Backend Analysis tab doesn't show much information.
*   **Solution:**
    1.  **Data Quality:** The quality of backend analysis depends on the data collected. If data collection was incomplete or problematic, analysis will be affected.
    2.  **Website Complexity:** Simple websites or those using obscure/custom technologies might not be fully identified by the `builtwith` library or other pattern-matching techniques.
    3.  **API Endpoint Discovery:** This is a heuristic process. Not all APIs are publicly advertised or easily discoverable through static analysis of page content.
    4.  **Authentication Analysis:** This is based on common patterns. Websites with custom or non-standard authentication flows might not be fully interpreted.

### 3.4. PGP Operations Fail (Key Generation, Encryption, Decryption)

*   **Symptom:** Errors occur in the PGP Key Management tab.
*   **Solution:**
    1.  **GnuPG Installation:** Re-verify GnuPG is correctly installed and accessible (see Section 2.2).
    2.  **GPG Home Permissions:** Ensure the application has permissions to read/write to its dedicated GPG home directory.
    3.  **Passphrases:** Ensure you are entering the correct passphrase for private key operations. Passphrases are case-sensitive.
    4.  **Key Availability:** For encryption, the recipient's public key must be in the keyring. For decryption, the corresponding private key must be present.
    5.  **Corrupted Keys/Keyring:** In rare cases, the GPG keyring might become corrupted. If using a dedicated GPG home for the tool, you might try (with caution, as it deletes keys managed by the tool) removing or renaming the tool's GPG home directory to let it recreate a fresh one. You would lose any keys generated solely within the tool unless backed up.
    6.  **GPG Agent:** Issues with the GPG agent (if used by your system's GPG) can sometimes interfere. Check GPG agent status if you suspect this.
    7.  **Review Logs:** `app.log` will contain detailed error messages from `PGPManager` and underlying GnuPG calls (stderr from GPG is often logged).

### 3.5. GUI Freezes or Behaves Unexpectedly

*   **Symptom:** The application becomes unresponsive or UI elements don't work as expected.
*   **Solution:**
    1.  **Long Operations:** Some operations (like extensive data collection or complex PGP key generation) can take time. The GUI should ideally handle this with progress indicators or by running tasks in background threads. If it freezes, wait a reasonable amount of time.
    2.  **Check Logs:** Look for errors in `app.log` or the console output that might indicate what went wrong.
    3.  **Restart Application:** Try closing and restarting the tool.
    4.  **Report Bug:** If the issue is reproducible and seems like a bug in the tool, consider reporting it (if a reporting mechanism is available), providing steps to reproduce, and relevant log excerpts.

## 4. Understanding Log Files

The primary log file for the application is `app.log`, typically located in:
*   `~/.web_analysis_tool_data/logs/app.log` (Linux/macOS)
*   `C:\Users\YourUser\.web_analysis_tool_data\logs\app.log` (Windows)

This file contains timestamped entries for:
*   **INFO:** General operational messages.
*   **WARNING:** Potential issues or unusual situations that don't necessarily stop the application.
*   **ERROR:** Problems that prevented an operation from completing successfully.
*   **CRITICAL:** Severe errors that might affect the overall stability of the application.

When troubleshooting, examining the most recent entries in this log file after an issue occurs is often the most helpful step.

## 5. Frequently Asked Questions (FAQ)

*   **Q1: Can I use this tool on any website?**
    *   **A1:** **NO.** You MUST only use this tool on websites where you have explicit, verifiable permission. Unauthorized use is illegal and unethical. Refer to `ETHICAL_USE.md`.

*   **Q2: Where is the collected data stored?**
    *   **A2:** Typically in `~/.web_analysis_tool_data/collected_data/` (or a similar path depending on your OS), in CSV and JSON formats.

*   **Q3: Are my PGP keys stored securely?**
    *   **A3:** The tool uses GnuPG for key management. The security of your keys depends on the strength of your passphrases and the security of your GnuPG installation and its home directory. The tool aims to use a dedicated GPG home to isolate its keys.

*   **Q4: The tool seems slow when collecting data from large websites. Is this normal?**
    *   **A4:** Yes, collecting and parsing data from large or numerous web pages can be time-consuming and resource-intensive. Be patient and mindful of the load you might be placing on the target server.

*   **Q5: Can this tool find all backend technologies or API endpoints?**
    *   **A5:** No. Technology identification and API discovery are based on common patterns and heuristics. They provide good clues but may not be exhaustive or 100% accurate for all websites, especially those using custom or heavily obfuscated setups.

## 6. Contact / Support (Placeholder)

If you encounter issues not covered by this guide, and if a support channel is provided with the tool, please use that for assistance. Provide as much detail as possible, including:
*   Steps to reproduce the issue.
*   Expected behavior vs. actual behavior.
*   Relevant excerpts from the `app.log` file.
*   Your operating system and Python version.

This troubleshooting guide aims to cover common scenarios. Always prioritize ethical and responsible use of the Web Analysis Tool.

