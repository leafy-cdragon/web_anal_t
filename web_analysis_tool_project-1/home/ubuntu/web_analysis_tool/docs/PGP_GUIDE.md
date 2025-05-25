# Web Analysis Tool - PGP Guide

## 1. Introduction to PGP and Its Role in This Tool

Pretty Good Privacy (PGP) is a widely used encryption program that provides cryptographic privacy and authentication for data communication. Within the Web Analysis Tool, the PGP component serves two primary educational purposes:

1.  **Secure Communication:** To help you understand how to generate PGP keys, encrypt messages for others, and decrypt messages sent to you. This demonstrates a fundamental aspect of data security.
2.  **Authentication Concepts:** To provide a (simulated) understanding of how PGP keys can be involved in authentication processes, such as signing challenges to prove identity. This is purely for educational demonstration on systems you own and control.

This guide focuses on the practical use of the PGP features within the Web Analysis Tool. It assumes you have GnuPG (GPG) installed on your system, as detailed in the `INSTALLATION.md` guide. The tool uses `python-gnupg` to interact with your GPG installation, preferably within a dedicated GPG home directory managed by the application to avoid conflicts with your system-wide GPG keys.

**Key Security is Paramount:** The security of your PGP keys, especially your private keys, is crucial. This guide will highlight best practices for managing them.

## 2. Accessing the PGP Management Module

All PGP-related functionalities are accessible through the **"PGP Key Management"** tab in the main application window.

## 3. PGP Key Pair Generation

A PGP key pair consists of a public key and a private key:

*   **Public Key:** You can share this key freely. Others use it to encrypt messages that only you (with your private key) can decrypt. It is also used to verify your digital signatures.
*   **Private Key:** This key MUST be kept secret and protected by a strong passphrase. It is used to decrypt messages sent to you and to create digital signatures.

### Steps to Generate a New Key Pair:

1.  In the "PGP Key Management" tab, locate and click the button for **"Generate New Key Pair"** (or similar wording).
2.  A dialog box will appear, prompting you for the following information:
    *   **Real Name:** Your full name (e.g., "Alice Wonderland"). This will be part of the User ID (UID) of your key.
    *   **Email Address:** Your email address (e.g., "alice@example.com"). This is also part of the UID.
    *   **Passphrase:** A strong, unique passphrase to protect your private key. You will need this passphrase to use your private key (e.g., for decryption or signing). Choose a passphrase that is hard to guess but memorable for you.
    *   **Confirm Passphrase:** Re-enter the passphrase to ensure accuracy.
    *   **(Advanced Options - May be defaults)**
        *   **Key Type:** Typically RSA (default and recommended).
        *   **Key Length:** Usually 2048 bits or 4096 bits (default, e.g., 2048, is generally secure and recommended for compatibility).
3.  After filling in the details, click the "Generate" or "OK" button.
4.  The key generation process may take a few moments as the system needs to gather entropy (randomness).
5.  Upon successful generation, a confirmation message will appear, usually displaying the **fingerprint** of your new key. The fingerprint is a unique shorter string that identifies your key.

Your new key pair is now stored in the GPG keyring managed by the application.

## 4. Managing Your PGP Keys

The PGP Management tab provides several functions to manage your keys:

### 4.1. Listing Keys

*   **List Public Keys:** Displays a list of all public keys currently in the application's GPG keyring. This includes your own public keys and any public keys you have imported from others.
*   **List Private Keys:** Displays a list of all private keys for which you hold the secret part in the application's GPG keyring.

For each key, information such as the User ID (UID - typically name and email), key fingerprint, key ID, creation date, and expiration date (if set) will be shown.

### 4.2. Exporting Keys

Exporting allows you to create a file containing your key, which can then be shared or backed up.

1.  Identify the key you wish to export (usually by its fingerprint or Key ID from the list).
2.  Click **"Export Key"** (or similar).
3.  You will be prompted to:
    *   Specify the **Key ID or Fingerprint** of the key to export.
    *   Choose whether to export the **Public Key** or the **Private Key**.
        *   **Exporting Public Key:** This is common. The resulting file (e.g., `my_public_key.asc`) can be sent to others or uploaded to key servers.
        *   **Exporting Private Key:** **HANDLE WITH EXTREME CAUTION.** Only do this for backup purposes and store the exported private key in a very secure, encrypted location. If this file is compromised, your digital identity associated with this key is compromised.
    *   Select a location and filename for the exported key file. ASCII-armored format (`.asc`) is standard for text-based sharing.
4.  Confirm the export.

### 4.3. Importing Keys

Importing allows you to add others' public keys to your keyring (so you can encrypt messages to them) or to restore your own keys from a backup.

1.  Click **"Import Key"** (or similar).
2.  A file dialog will appear. Select the key file you wish to import (usually a `.asc` or `.gpg` file).
3.  The tool will attempt to import the key(s) from the file into its GPG keyring.
4.  A status message will indicate the outcome of the import (e.g., number of keys processed, fingerprints of imported keys).

### 4.4. Deleting Keys

This action removes keys from the application's GPG keyring.

1.  Identify the key you wish to delete by its fingerprint.
2.  Click **"Delete Key"** (or similar).
3.  You will be prompted to:
    *   Enter the **Fingerprint** of the key to delete.
    *   Specify whether to delete the **Public Key** or the **Private Key** (if both parts exist).
        *   Deleting a public key just removes it from your local list.
        *   **Deleting a Private Key:** This is a **destructive and irreversible action** if you do not have a backup. You will permanently lose the ability to decrypt messages encrypted with the corresponding public key and to sign with that private key.
4.  Confirm the deletion. You may be asked for your GPG passphrase if deleting a protected private key.

## 5. Cryptographic Operations

### 5.1. Encrypting a Message

To send a secure message that only the intended recipient(s) can read:

1.  Navigate to the encryption section within the PGP Management tab.
2.  **Enter your message** in the provided text area.
3.  **Specify Recipient(s):** Enter the Key ID, fingerprint, or email address associated with the recipient's public key. Their public key must be present in your application's GPG keyring (imported previously).
4.  **(Optional) Sign the Message:** You can choose to digitally sign the encrypted message with one of your private keys. This assures the recipient that the message genuinely came from you and has not been tampered with. If you choose to sign, you may need to enter the passphrase for your signing private key.
5.  Click **"Encrypt"**.
6.  The resulting encrypted message (usually in ASCII-armored PGP block format) will be displayed. You can copy this block and send it to your recipient (e.g., via email).

### 5.2. Decrypting a Message

To read a message that was encrypted using your public key:

1.  Navigate to the decryption section within the PGP Management tab.
2.  **Paste the entire PGP encrypted message block** (including `-----BEGIN PGP MESSAGE-----` and `-----END PGP MESSAGE-----` lines) into the text area.
3.  Click **"Decrypt"**.
4.  If the message was encrypted for one of your private keys stored in the application's keyring, you will be prompted to enter the **passphrase for that private key**.
5.  If the passphrase is correct and the key matches, the decrypted plaintext message will be displayed.
6.  If the message was also signed, the decryption process will typically also verify the signature and inform you of its validity and the signer's identity.

## 6. PGP Authentication Simulation (Educational Feature)

This feature is designed to illustrate how PGP signing can be a component of an authentication process. It does **not** perform actual authentication against any live system but simulates the client-side action of signing a challenge.

**ETHICAL USE IS PARAMOUNT:**
*   This simulation should **ONLY** be used against systems you own and have explicitly set up for such educational testing.
*   **NEVER** attempt to use this feature against systems you do not have explicit permission to test in this manner.
*   The tool will display prominent warnings before this simulation can be run.

### How it Works (Conceptually):

1.  **Select Your Private Key:** Choose one of your PGP private keys from the list.
2.  **Enter Passphrase:** Provide the passphrase for the selected private key to unlock it for signing.
3.  **Target System Information (Simulated):** Enter some notional information about the system you are *pretending* to authenticate to. This is for context only.
4.  **Initiate Simulation:** Click the "Simulate Authentication Attempt" button and acknowledge the ethical warnings.
5.  **Action:** The tool will generate a hypothetical challenge string and then use your selected private key and passphrase to create a digital signature of that challenge.
6.  **Result:** The interface will display whether the signing operation was successful. If successful, it means your key was accessed and used to sign data. This *simulates* what your PGP software would do if a real system asked it to sign a challenge for authentication.

This feature helps you understand the role of private key access and digital signatures in PGP-based authentication schemes (like those sometimes used with SSH or certain web applications).

## 7. PGP Best Practices within the Tool

*   **Strong Passphrases:** Always use strong, unique passphrases for your PGP private keys.
*   **Backup Private Keys:** If you generate important keys, export the private key (securely!) and back it up in a safe, encrypted location (e.g., an encrypted USB drive stored securely).
*   **Dedicated GPG Home:** The tool's use of a dedicated GPG home (`~/.web_analysis_tool_data/gnupg_home` or similar) is a good practice as it isolates these keys from your system-wide GPG keys, which might be used for other critical purposes.
*   **Verify Fingerprints:** When importing public keys from others, verify their fingerprints through a trusted channel if possible to ensure you are not importing a fraudulent key.
*   **Regularly Review Keys:** Periodically review the keys in your keyring.

This PGP guide should provide you with the necessary knowledge to use the PGP functionalities of the Web Analysis Tool effectively and responsibly. Always prioritize security and ethical conduct.

