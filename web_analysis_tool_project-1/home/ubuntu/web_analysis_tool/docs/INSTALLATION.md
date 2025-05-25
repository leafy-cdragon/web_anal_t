# Web Analysis Tool - Installation Guide

## 1. Introduction

This guide provides detailed instructions for installing the Web Analysis Tool and its dependencies on your system. The tool is developed in Python and designed to be cross-platform (Windows, macOS, Linux), but specific steps might vary slightly depending on your operating system.

**Prerequisites:** Before proceeding with the installation, ensure you have the following software installed on your system:

*   **Python 3:** Version 3.8 or higher is recommended. You can download Python from [python.org](https://www.python.org/). During installation, ensure Python is added to your system's PATH environment variable.
*   **GnuPG (GPG):** This is essential for the PGP Key Management features. The `python-gnupg` library used by the tool is a wrapper around the GnuPG executable.
    *   **Windows:** Download Gpg4win from [gpg4win.org](https://www.gpg4win.org/).
    *   **macOS:** You can install GnuPG using Homebrew: `brew install gnupg`.
    *   **Linux:** GnuPG is usually available through your distribution's package manager. For example, on Debian/Ubuntu: `sudo apt-get install gnupg`.
    Ensure the `gpg` command-line tool is accessible from your system's PATH.
*   **Graphviz (Optional, for advanced visualization):** If you intend to use features that generate graphical visualizations of website structures (beyond simple text maps), Graphviz needs to be installed. The Python `graphviz` library interfaces with this.
    *   Download from [graphviz.org/download/](https://graphviz.org/download/).
    *   Ensure the Graphviz `dot` executable is in your system's PATH.

## 2. Obtaining the Tool

The Web Analysis Tool source code will be provided as a package (e.g., a ZIP file). Download this package and extract it to a directory of your choice on your local machine. This directory will be referred to as the `project_root`.

Example: `C:\Users\YourUser\Documents\WebAnalysisTool` or `/home/youruser/WebAnalysisTool`

## 3. Setting up a Virtual Environment (Recommended)

It is highly recommended to use a Python virtual environment to manage the tool's dependencies and avoid conflicts with other Python projects or your global Python installation.

1.  **Navigate to the project root directory:**
    Open your terminal or command prompt and change to the directory where you extracted the tool.
    ```bash
    cd path/to/your/WebAnalysisTool
    ```

2.  **Create a virtual environment:**
    If you are using Python 3, the `venv` module is built-in.
    ```bash
    python -m venv venv
    ```
    This command creates a new directory named `venv` (or any name you choose) within your `project_root` that will contain the Python interpreter and libraries for this project.

3.  **Activate the virtual environment:**
    *   **Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```
        (If you encounter an execution policy error in PowerShell, you might need to run `Set-ExecutionPolicy Unrestricted -Scope Process` first, then activate.)
    *   **macOS and Linux (bash/zsh):**
        ```bash
        source venv/bin/activate
        ```
    Once activated, your terminal prompt should change to indicate that you are now working within the virtual environment (e.g., `(venv) C:\...` or `(venv) user@host:...$`).

## 4. Installing Dependencies

The tool relies on several Python libraries, which are listed in the `requirements.txt` file located in the `project_root` directory.

1.  **Ensure your virtual environment is activated.**

2.  **Install the required packages using pip:**
    Navigate to the `project_root` directory in your terminal (if not already there) and run:
    ```bash
    pip install -r requirements.txt
    ```
    This command will read the `requirements.txt` file and download and install all the necessary libraries (e.g., `PyQt6`, `requests`, `BeautifulSoup4`, `lxml`, `builtwith`, `python-gnupg`, `graphviz`) into your virtual environment.

    *Note on `lxml`*: On some systems, `lxml` might require build tools or development headers. If you encounter issues installing `lxml`, consult its official documentation for platform-specific installation instructions (often involving installing packages like `python3-dev` and `libxml2-dev`, `libxslt-dev` on Linux, or using pre-compiled wheels on Windows/macOS which pip usually handles automatically).

## 5. Verifying GnuPG Installation

After installing GnuPG, verify that it's correctly installed and accessible from your command line:

```bash
_gpg --version
```

This command should output the GnuPG version information. If it doesn't, ensure GnuPG's installation directory (containing `gpg.exe` or `gpg`) is added to your system's PATH environment variable and restart your terminal or system.

The PGP Management component of the Web Analysis Tool will attempt to use this GnuPG installation. The tool can be configured to point to a specific GPG binary if it's not in the PATH.

## 6. Initial Configuration (If Applicable)

Upon first launch, or as described in the User Guide, the tool might create a dedicated directory for its data, including logs and a separate GnuPG home directory (e.g., `~/.web_analysis_tool_data/gnupg_home`). This helps isolate the tool's PGP keys from your system's default GPG keyring, which is recommended.

No manual configuration is typically required before the first run, but be aware of where the application stores its data (check the `logger_config.py` and `pgp_manager.py` for default paths if needed).

## 7. Running the Application

Once all dependencies are installed and prerequisites are met:

1.  Ensure your virtual environment is activated.
2.  Navigate to the `src` directory within your `project_root`.
    ```bash
    cd src
    ```
3.  Run the main application script (e.g., `main_app.py` or a designated main entry point):
    ```bash
    python gui/main_app.py
    ```
    (The exact command to run the application will be specified if different from the example above, typically involving a main script in the `src` or `project_root` directory.)

This should launch the Web Analysis Tool's graphical user interface.

## 8. Troubleshooting Installation

Refer to the `TROUBLESHOOTING.md` document for common installation issues and their solutions.

This installation guide provides the necessary steps to get the Web Analysis Tool up and running. Please consult the `USER_GUIDE.md` for instructions on how to use the tool's features.

