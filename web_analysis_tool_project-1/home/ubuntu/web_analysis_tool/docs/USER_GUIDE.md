# Web Analysis Tool - User Guide

## 1. Introduction

Welcome to the Web Analysis Tool! This guide will walk you through the various features and functionalities of the application, helping you understand how to collect data from websites, analyze their backend structures, and manage PGP keys for educational purposes. Please ensure you have read the `README.md` and `INSTALLATION.md` documents before proceeding, and always adhere to the `ETHICAL_USE.md` guidelines.

**Core Principle:** This tool is for learning and authorized analysis only. Misuse can have serious legal and ethical consequences.

## 2. Launching the Application

After successfully installing the tool and its dependencies (as detailed in `INSTALLATION.md`):

1.  Activate your Python virtual environment (if you created one).
2.  Navigate to the `src` directory within the tool's installation folder.
3.  Run the main application script:
    ```bash
    python gui/main_app.py 
    ```
    (Or the designated main script if different).

Upon launch, you will be greeted with the main application window, which features a tabbed interface for different modules.

## 3. Understanding the Interface

The main window is organized into several tabs:

*   **Data Collection:** For specifying target websites and initiating data scraping.
*   **Backend Analysis:** For viewing analysis results of collected website data.
*   **PGP Key Management:** For generating, listing, importing, exporting, encrypting/decrypting with PGP keys, and simulating PGP authentication.
*   **Settings & Logs:** For configuring application settings (if any) and viewing activity logs.

### 3.1. Initial Ethical Warning

Upon first launch, and periodically, an ethical use reminder will be displayed. It is crucial to understand and respect these guidelines. Proceeding implies your agreement to use the tool responsibly and legally.

## 4. Data Collection Module

This module allows you to fetch and store information from websites.

### 4.1. Collecting Data from a Website

1.  **Navigate to the "Data Collection" Tab.**
2.  **Enter the URL:** In the "Target Website" group box, input the full URL of the website you have permission to analyze (e.g., `https://example.com`) into the "URL" field.
3.  **Configure Collection Options (if available):** Future versions may allow specifying what to collect (e.g., only metadata, full text, specific elements). For now, default collection includes metadata, links, text preview, and HTTP logs.
4.  **Initiate Collection:** Click the "Collect Data" button.
    *   **Ethical Reminder:** Ensure you have explicit permission to scrape the target URL.
5.  **View Results:** The "Collection Results" text area will display a summary of the operation, including:
    *   The target URL.
    *   HTTP status code of the request.
    *   Extracted metadata (title, description).
    *   Number of links found.
    *   A preview of the extracted text content.
    *   Paths to the saved CSV and JSON files containing the detailed collected data.
    *   Logged HTTP headers.

### 4.2. Understanding Collected Data Files

*   **CSV File:** Contains a structured summary of the collected data, typically one row per primary page analyzed, including metadata, URL, timestamp, text preview, and link counts/samples. This format is useful for quick overviews or import into spreadsheet software.
*   **JSON File:** Contains a more detailed and hierarchical representation of all collected data for the target URL, including full metadata, complete HTTP logs (request/response headers, status code), all extracted links, and potentially the full text content. This format is better for programmatic access or detailed inspection.

These files are saved in the `collected_data` directory (or a configured output directory) within the application's data folder (e.g., `~/.web_analysis_tool_data/collected_data`).

### 4.3. Filtering and Searching Data (Conceptual)

The current GUI provides a basic display. Future enhancements would involve features within the GUI to load, filter, and search through the collected CSV/JSON files directly.

## 5. Backend Analysis Module

This module uses the data collected by the Data Collection module (or can be pointed to specific URLs/data) to provide insights into a website's backend.

### 5.1. Performing Backend Analysis

1.  **Navigate to the "Backend Analysis" Tab.**
2.  **Load Data/Specify Target:** (Functionality to be fully implemented in GUI)
    *   Ideally, this tab would allow you to select a previously collected data set (e.g., a JSON file from the Data Collection module) or specify a new URL for direct analysis (which would internally use the Data Collector).
    *   For the current placeholder, it might operate on the last collected data or a predefined example.
3.  **Initiate Analysis:** Click an "Analyze" button.
4.  **View Analysis Results:** The results area on this tab will display:
    *   **Identified Technologies:** A list of technologies detected on the website (e.g., web server, CMS, programming languages, JavaScript frameworks).
    *   **Authentication Mechanism Analysis:** Information about detected login forms, use of session cookies, presence of HTTP authentication headers, or indicators of JWT usage.
    *   **Discovered API Endpoints:** A list of potential API URLs found through parsing page content and links.
    *   **Site Structure Map:** A textual or dictionary-based representation of the website's internal link structure, giving an overview of its organization.

### 5.2. Interpreting Analysis Results

*   **Technology Identification:** Helps understand the software stack used to build and run the website. This is based on patterns and signatures and might not always be exhaustive or perfectly accurate.
*   **Authentication Analysis:** Provides clues about how users log in. This is based on common web patterns.
*   **API Endpoints:** These are *potential* endpoints. Further investigation (respecting terms of service) would be needed to understand their function.
*   **Site Structure Map:** Helps visualize how pages are interconnected.

## 6. PGP Key Management Module

This module provides tools for managing PGP keys and performing cryptographic operations. It interfaces with an underlying GnuPG installation.

**Important GnuPG Prerequisite:** Ensure GnuPG is correctly installed and accessible on your system as per the `INSTALLATION.md` guide. The tool will attempt to use a dedicated GPG home directory (e.g., `~/.web_analysis_tool_data/gnupg_home`) to avoid interfering with your system's default GPG keyring.

### 6.1. Generating a New PGP Key Pair

1.  **Navigate to the "PGP Key Management" Tab.**
2.  **Access Key Generation:** Click a button like "Generate New Key Pair".
3.  **Enter Key Details:** A dialog will prompt you for:
    *   **Real Name:** Your name (e.g., "John Doe").
    *   **Email Address:** Your email (e.g., "john.doe@example.com").
    *   **Passphrase:** A strong passphrase to protect your new private key. Confirm the passphrase.
    *   **(Optional) Key Type and Length:** Defaults are usually RSA 2048-bit or higher, which are secure.
4.  **Generate:** Confirm the details. Key generation might take a few moments.
5.  **Confirmation:** Upon success, the new key's fingerprint will be displayed.

### 6.2. Listing PGP Keys

*   Click "List Public Keys" or "List Private Keys" to see the keys currently managed by the tool's GPG instance. Details like User ID (UID) and fingerprint will be shown.

### 6.3. Exporting PGP Keys

1.  Select a key from the list (or enter its Key ID/fingerprint).
2.  Choose to export the **public key** or (with extreme caution) the **private key**.
3.  Specify a filename and location to save the key (e.g., `my_public_key.asc`).
    *   **Public Keys (.asc):** Safe to share. Used by others to encrypt messages for you or verify your signatures.
    *   **Private Keys:** Must be kept absolutely secret. Anyone with your private key and passphrase can decrypt your messages and sign as you.

### 6.4. Importing PGP Keys

1.  Click "Import Key".
2.  Select a key file (e.g., a `.asc` file containing a public key you received).
3.  The tool will attempt to import it into its GPG keyring.

### 6.5. Deleting PGP Keys

1.  Select a key by its fingerprint.
2.  Choose to delete the public or private key part.
    *   **Warning:** Deleting a private key is irreversible if you don't have a backup. You will lose access to data encrypted with the corresponding public key and the ability to sign with that key.

### 6.6. Encrypting a Message

1.  Go to the encryption section.
2.  Enter or paste the message you want to encrypt.
3.  Specify the recipient(s) by their Key ID or email address (their public key must be in your keyring).
4.  Optionally, choose to sign the message with one of your private keys (requires passphrase).
5.  Click "Encrypt". The ASCII armored encrypted message will be displayed, ready to be copied.

### 6.7. Decrypting a Message

1.  Go to the decryption section.
2.  Paste the PGP encrypted message.
3.  If the message was encrypted to one of your private keys, the tool will attempt to decrypt it. You may be prompted for your passphrase.
4.  The decrypted message will be displayed.

### 6.8. PGP Authentication Simulation (Educational Use Only)

This feature is strictly for understanding how PGP *could* be used in authentication (e.g., signing a challenge).

1.  **Select one of your private keys.**
2.  **Enter the passphrase for the selected key.**
3.  **Specify (conceptually) target system information.** This is for simulation context.
4.  **Click "Simulate Authentication Attempt".**
    *   **CRITICAL ETHICAL WARNING:** A prominent warning will appear. You MUST only proceed if you are targeting a system you OWN and have EXPLICITLY configured for such an educational test. This feature DOES NOT perform real authentication against arbitrary systems.
5.  **View Simulation Results:** The tool will simulate signing a hypothetical challenge with your key and display the outcome (e.g., "Challenge signed successfully (simulated)"). This demonstrates key access and signing capability, not actual system access.

## 7. Settings & Logs Tab

*   **Settings:** This section may be used for future application-level configurations (e.g., default output directories, GPG binary path if not in system PATH).
*   **Logs:** This area will display application logs in real-time or allow you to open the log file (`~/.web_analysis_tool_data/logs/app.log`). Logs are crucial for troubleshooting and understanding tool activity.

## 8. Best Practices and Reminders

*   **Ethical Conduct:** Always obtain permission before analyzing any website not your own.
*   **Passphrase Security:** Use strong, unique passphrases for your PGP keys and keep them confidential.
*   **Private Key Security:** Protect your private PGP keys. Do not share them. Consider backing them up securely.
*   **Resource Usage:** Extensive web scraping can be resource-intensive for both your machine and the target server. Be mindful and avoid overloading servers.
*   **Legal Compliance:** Familiarize yourself with relevant laws (e.g., CFAA in the US, GDPR in Europe) and website terms of service regarding data collection and security testing.

## 9. Exiting the Application

Close the main window or use the application's File > Exit menu (if available) to quit the Web Analysis Tool.

This user guide provides an overview of the Web Analysis Tool's functionalities. For more specific details on PGP, refer to `PGP_GUIDE.md`, and for troubleshooting, see `TROUBLESHOOTING.md`. Always prioritize ethical and responsible use.

