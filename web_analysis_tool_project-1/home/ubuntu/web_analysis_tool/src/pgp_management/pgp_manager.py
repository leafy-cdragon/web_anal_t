# pgp_manager.py

import gnupg
import logging # Use standard logging
import os

# Import custom exceptions
from ..utils.custom_exceptions import PGPManagementError, ConfigurationError

# Get a logger for this module
logger = logging.getLogger(__name__)

class PGPManager:
    """Manages PGP key generation, storage, and cryptographic operations."""

    def __init__(self, gpg_home=None, gpg_binary=None):
        """
        Initializes the PGPManager.

        Args:
            gpg_home (str, optional): The path to the GnuPG home directory. 
                                      If None, python-gnupg will use the default GPG home.
                                      It is highly recommended to use a dedicated directory for the application keys.
            gpg_binary (str, optional): Path to the GPG binary. If None, it will be searched in PATH.
        """
        self.gpg = None
        try:
            if gpg_home:
                if not os.path.exists(gpg_home):
                    # Ensure the parent directory exists before creating gpg_home
                    parent_gpg_home = os.path.dirname(gpg_home)
                    if parent_gpg_home and not os.path.exists(parent_gpg_home):
                         os.makedirs(parent_gpg_home, exist_ok=True)
                    os.makedirs(gpg_home, mode=0o700, exist_ok=True) # Ensure directory is private
                logger.info(f"Using GPG home directory: {gpg_home}")
            
            self.gpg = gnupg.GPG(gnupghome=gpg_home, gpgbinary=gpg_binary)
            
            # Test GPG availability and version
            version_info = self.gpg.version
            if not version_info:
                error_msg = "GnuPG binary not found or GPG version could not be determined. Please ensure GnuPG is installed and in your PATH, or specify the binary path."
                logger.error(error_msg)
                # self.gpg will likely be None or unusable here, subsequent calls will fail gracefully.
                raise ConfigurationError(error_msg)
            logger.info(f"GnuPG initialized. Version: {version_info}")

        except FileNotFoundError as fnf_error: # Specifically if gpg_binary path is wrong
            error_msg = f"GnuPG binary not found at specified path or in PATH: {fnf_error}. Ensure GnuPG is installed and configured correctly."
            logger.error(error_msg)
            self.gpg = None # Ensure gpg is None if initialization fails
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Failed to initialize GPG: {e}. Ensure GnuPG is installed and configured correctly."
            logger.error(error_msg, exc_info=True)
            self.gpg = None # Ensure gpg is None if initialization fails
            raise ConfigurationError(error_msg)

    def _ensure_gpg_available(self):
        if not self.gpg or not self.gpg.version: # Check version again as a proxy for successful init
            raise PGPManagementError("GnuPG is not available or not properly initialized. Please check application logs and GPG setup.")

    def generate_key_pair(self, name_real, name_email, passphrase, key_type="RSA", key_length=2048):
        """
        Generates a new PGP key pair.
        Returns gnupg.GenKey object or raises PGPManagementError.
        """
        self._ensure_gpg_available()
        logger.info(f"Attempting to generate PGP key for {name_email} with type {key_type} and length {key_length}.")
        
        # Check if passphrase is provided
        if not passphrase:
            logger.error("Passphrase is required to generate a PGP key.")
            raise PGPManagementError("Passphrase cannot be empty for key generation.")

        input_data = self.gpg.gen_key_input(
            name_real=name_real,
            name_email=name_email,
            passphrase=passphrase,
            key_type=key_type,
            key_length=key_length,
            expire_date=0 # 0 means key does not expire
        )
        try:
            key = self.gpg.gen_key(input_data)
            if key and key.fingerprint:
                logger.info(f"Successfully generated PGP key. Fingerprint: {key.fingerprint}")
                return key
            else:
                # python-gnupg might return a result object even on failure, or None
                # The status and stderr attributes of the result object are important.
                status = key.status if hasattr(key, "status") else "Unknown status"
                stderr = key.stderr if hasattr(key, "stderr") else "No stderr output"
                logger.error(f"Failed to generate PGP key for {name_email}. Status: {status}. Stderr: {stderr}")
                raise PGPManagementError(f"Failed to generate PGP key. GPG Status: {status}. Details: {stderr}")
        except Exception as e:
            logger.error(f"Exception during PGP key generation for {name_email}: {e}", exc_info=True)
            raise PGPManagementError(f"An unexpected error occurred during key generation: {e}")

    def list_keys(self, secret=False):
        """Lists available PGP keys. Returns list of key dicts or raises PGPManagementError."""
        self._ensure_gpg_available()
        try:
            keys = self.gpg.list_keys(secret)
            logger.info(f"Found {len(keys)} {"private" if secret else "public"} keys.")
            return keys
        except Exception as e:
            logger.error(f"Error listing PGP keys (secret={secret}): {e}", exc_info=True)
            raise PGPManagementError(f"Failed to list PGP keys: {e}")

    def export_key(self, keyid, output_file, secret=False, armor=True):
        """Exports a PGP key. Returns True on success or raises PGPManagementError."""
        self._ensure_gpg_available()
        if secret:
            logger.warning(f"Attempting to export SECRET key {keyid} to {output_file}. This is a sensitive operation.")
            key_data = self.gpg.export_keys(keyid, secret=True, armor=armor)
        else:
            logger.info(f"Exporting public key {keyid} to {output_file}")
            key_data = self.gpg.export_keys(keyid, secret=False, armor=armor)

        if key_data:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(key_data)
                logger.info(f"Key {keyid} successfully exported to {output_file}")
                return True
            except IOError as e:
                logger.error(f"IOError writing key to file {output_file}: {e}")
                raise PGPManagementError(f"Failed to write key to file {output_file}: {e}")
        else:
            logger.error(f"Failed to export key {keyid}. Key not found or error during export.")
            raise PGPManagementError(f"Failed to export key {keyid}. Check if key exists and GPG logs.")

    def import_key(self, key_file_path):
        """Imports a PGP key. Returns gnupg.ImportResult or raises PGPManagementError."""
        self._ensure_gpg_available()
        try:
            with open(key_file_path, "r", encoding="utf-8") as f:
                key_data = f.read()
            import_result = self.gpg.import_keys(key_data)
            if import_result and import_result.fingerprints:
                logger.info(f"Key import result: Fingerprints imported: {import_result.fingerprints}")
            elif import_result:
                 logger.warning(f"Key import processed, but no fingerprints reported. Status: {import_result.results}")
            else:
                logger.error(f"Key import failed for {key_file_path}. Result: {import_result}")
                raise PGPManagementError(f"Key import failed. GPG result: {import_result.results if import_result else \"No result\"}")
            return import_result
        except IOError as e:
            logger.error(f"IOError reading key file {key_file_path}: {e}")
            raise PGPManagementError(f"Failed to read key file {key_file_path}: {e}")
        except Exception as e:
            logger.error(f"Error importing key from {key_file_path}: {e}", exc_info=True)
            raise PGPManagementError(f"An unexpected error occurred during key import: {e}")

    def delete_key(self, fingerprint, secret=False):
        """Deletes a PGP key. Returns True on success or raises PGPManagementError."""
        self._ensure_gpg_available()
        action = "SECRET" if secret else "public"
        log_message = f"Attempting to delete {action} key with fingerprint {fingerprint}. This is a destructive operation if secret=True."
        if secret: logger.warning(log_message)
        else: logger.info(log_message)
        
        try:
            # Pass expect_passphrase=True if the key might be passphrase protected for deletion (though usually not for public keys)
            # For secret keys, GPG might prompt if not handled by agent or if passphrase not supplied to python-gnupg directly.
            # This tool assumes user handles GPG agent or enters passphrase if prompted by GPG CLI via python-gnupg.
            result = self.gpg.delete_keys(fingerprint, secret=secret)
            if result and "ok" in result.status.lower():
                logger.info(f"Successfully processed delete request for {action} key {fingerprint}. Status: {result.status}")
                return True
            elif result and ("not found" in result.status.lower() or "no such key" in result.status.lower()):
                logger.info(f"{action.capitalize()} key {fingerprint} not found for deletion. Status: {result.status}")
                return True # Key is not present, so deletion is effectively successful.
            else:
                status_msg = result.status if result else "Unknown error from GPG"
                stderr_msg = result.stderr if result and hasattr(result, "stderr") else "N/A"
                logger.error(f"Failed to delete {action} key {fingerprint}. Status: {status_msg}, Stderr: {stderr_msg}")
                raise PGPManagementError(f"Failed to delete {action} key {fingerprint}. GPG Status: {status_msg}. Details: {stderr_msg}")
        except Exception as e:
            logger.error(f"Exception during key deletion for fingerprint {fingerprint} (secret={secret}): {e}", exc_info=True)
            raise PGPManagementError(f"An unexpected error occurred during key deletion: {e}")

    def encrypt_message(self, recipients, message, armor=True, sign=None, passphrase=None):
        """Encrypts a message. Returns encrypted string or raises PGPManagementError."""
        self._ensure_gpg_available()
        if not recipients:
            raise PGPManagementError("Recipients list cannot be empty for encryption.")
        if not message:
            # Allow encrypting empty message, GPG handles this.
            logger.warning("Encrypting an empty message.")

        try:
            encrypted_data = self.gpg.encrypt(message, recipients, armor=armor, sign=sign, passphrase=passphrase, always_trust=True)
            if encrypted_data.ok:
                logger.info("Message encrypted successfully.")
                return str(encrypted_data)
            else:
                logger.error(f"Failed to encrypt message. Status: {encrypted_data.status}, Stderr: {encrypted_data.stderr}")
                raise PGPManagementError(f"Encryption failed. GPG Status: {encrypted_data.status}. Details: {encrypted_data.stderr}")
        except Exception as e:
            logger.error(f"Exception during message encryption: {e}", exc_info=True)
            raise PGPManagementError(f"An unexpected error occurred during encryption: {e}")

    def decrypt_message(self, encrypted_message, passphrase=None):
        """Decrypts a PGP message. Returns decrypted string or raises PGPManagementError."""
        self._ensure_gpg_available()
        if not encrypted_message:
            raise PGPManagementError("Encrypted message cannot be empty for decryption.")

        try:
            decrypted_data = self.gpg.decrypt(encrypted_message, passphrase=passphrase)
            if decrypted_data.ok:
                logger.info("Message decrypted successfully.")
                return str(decrypted_data)
            elif "no secret key" in str(decrypted_data.stderr).lower() or decrypted_data.status == "no secret key":
                logger.error(f"Decryption failed: No secret key available for the encrypted message. Status: {decrypted_data.status}, Stderr: {decrypted_data.stderr}")
                raise PGPManagementError("Decryption failed: No secret key available for one or more recipients.")
            elif "bad passphrase" in str(decrypted_data.stderr).lower() or decrypted_data.status == "bad passphrase":
                 logger.error(f"Decryption failed: Bad passphrase. Status: {decrypted_data.status}, Stderr: {decrypted_data.stderr}")
                 raise PGPManagementError("Decryption failed: Incorrect passphrase provided.")
            else:
                logger.error(f"Failed to decrypt message. Status: {decrypted_data.status}, Stderr: {decrypted_data.stderr}")
                raise PGPManagementError(f"Decryption failed. GPG Status: {decrypted_data.status}. Details: {decrypted_data.stderr}")
        except Exception as e:
            logger.error(f"Exception during message decryption: {e}", exc_info=True)
            raise PGPManagementError(f"An unexpected error occurred during decryption: {e}")

    def attempt_pgp_authentication_simulation(self, key_fingerprint, passphrase, target_system_info):
        """
        Simulates an attempt to use a PGP key for authentication.
        THIS IS A PLACEHOLDER AND CONCEPTUAL FUNCTION.
        Actual PGP authentication depends heavily on the target system's implementation.
        This function should ONLY be used for educational demonstration on systems the user OWNS.
        Returns dict with simulation status or raises PGPManagementError for GPG issues.
        """
        self._ensure_gpg_available()
        logger.warning("--- PGP AUTHENTICATION SIMULATION (EDUCATIONAL USE ONLY) ---")
        logger.warning("ETHICAL USE WARNING: This function is for educational demonstration on systems you OWN and have EXPLICITLY configured for PGP authentication tests.")
        logger.warning("Attempting unauthorized access to any system is illegal and unethical.")
        
        private_keys = self.list_keys(secret=True)
        target_key = next((key for key in private_keys if key["fingerprint"] == key_fingerprint), None)
        if not target_key:
            msg = f"Private key with fingerprint {key_fingerprint} not found in keyring for simulation."
            logger.error(msg)
            # This is not a GPG operational error, but a logic error for the simulation
            return {"success": False, "message": msg, "details": "Key not found."}

        logger.info(f"Simulating authentication for system: {target_system_info.get("type", "unknown")} at {target_system_info.get("host", "unknown_host")} using key {key_fingerprint}")
        
        challenge_data = f"simulated_challenge_from_{target_system_info.get("host", "target")}_{datetime.utcnow().timestamp()}"
        try:
            # Test signing capability with the key and passphrase
            signed_data = self.gpg.sign(challenge_data, keyid=key_fingerprint, passphrase=passphrase, clearsign=False, detach=True)
            if signed_data and signed_data.ok:
                logger.info("Successfully signed simulated challenge data with the PGP key.")
                return {
                    "success": True, 
                    "message": "PGP authentication simulation: Key accessed and challenge signed (simulated).",
                    "details": "This is a conceptual step. Actual authentication requires a compatible target system and protocol (e.g., SSH agent, PGP-based web challenge).",
                    "simulated_challenge": challenge_data,
                    "simulated_signature_status": str(signed_data.status)
                }
            else:
                err_msg = f"Failed to sign simulated challenge. GPG status: {signed_data.status if signed_data else "N/A"}, stderr: {signed_data.stderr if signed_data else "N/A"}"
                logger.error(err_msg)
                # This indicates a problem with the key or passphrase during the GPG operation
                raise PGPManagementError(f"Simulation signing failed: {err_msg}")
        except PGPManagementError: # Re-raise if it is already our specific error
            raise
        except Exception as e:
            logger.error(f"Exception during simulated PGP authentication signing: {e}", exc_info=True)
            raise PGPManagementError(f"An unexpected error occurred during simulated PGP authentication signing: {e}")

# Example Usage (for testing purposes, will be called from GUI later)
if __name__ == "__main__":
    # This setup should ideally be in the main application entry point
    from ..utils.logger_config import setup_logging
    # Determine the project root to set up test GPG home relative to it
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_path, "..", "..")) # Adjust if structure changes
    test_gpg_home_path = os.path.join(project_root, "test_gnupg_home")
    
    # Ensure the test GPG home directory exists
    if not os.path.exists(test_gpg_home_path):
        os.makedirs(test_gpg_home_path, mode=0o700)
    
    # Setup logging for the test
    setup_logging(logging.DEBUG)
    logger.info(f"PGPManager test initiated. Using GPG home: {test_gpg_home_path}")

    try:
        pgp_manager = PGPManager(gpg_home=test_gpg_home_path)

        logger.info("--- PGP Manager Test --- GPG Initialized ---")
        
        key_name = "Test User PGPManager"
        key_email = "test.pgpmanager@example.com"
        key_pass = "testpass12345"
        test_fingerprint = None

        try:
            logger.info("\n--- Generating Test Key ---")
            generated_key = pgp_manager.generate_key_pair(key_name, key_email, key_pass)
            test_fingerprint = generated_key.fingerprint
            logger.info(f"Key generated. Fingerprint: {test_fingerprint}")

            logger.info("\n--- Listing Public Keys ---")
            public_keys = pgp_manager.list_keys()
            for pk in public_keys:
                logger.debug(f"  Public Key UID: {pk.get("uids")}, Fingerprint: {pk.get("fingerprint")}")

            logger.info("\n--- Listing Private Keys ---")
            private_keys = pgp_manager.list_keys(secret=True)
            for sk in private_keys:
                logger.debug(f"  Private Key UID: {sk.get("uids")}, Fingerprint: {sk.get("fingerprint")}")

            logger.info("\n--- Exporting Public Key ---")
            public_key_file = os.path.join(test_gpg_home_path, "test_public_key.asc")
            if pgp_manager.export_key(test_fingerprint, public_key_file):
                logger.info(f"Public key exported to {public_key_file}")
                # Try importing it back
                logger.info("\n--- Importing Public Key ---")
                pgp_manager.import_key(public_key_file)
                os.remove(public_key_file) # Clean up exported key file

            logger.info("\n--- Encrypting/Decrypting Message ---")
            message_to_encrypt = "This is a secret message for the PGPManager test!"
            encrypted_msg = pgp_manager.encrypt_message([test_fingerprint], message_to_encrypt, sign=test_fingerprint, passphrase=key_pass)
            if encrypted_msg:
                logger.debug(f"Encrypted: {encrypted_msg[:150]}...")
                decrypted_msg = pgp_manager.decrypt_message(encrypted_msg, passphrase=key_pass)
                if decrypted_msg:
                    logger.info(f"Decrypted: {decrypted_msg}")
                else:
                    logger.error("Decryption failed during test.") # Should be caught by PGPManagementError
            else:
                logger.error("Encryption failed during test.") # Should be caught by PGPManagementError

            logger.info("\n--- Simulating PGP Authentication (Educational Only) ---")
            auth_sim_result = pgp_manager.attempt_pgp_authentication_simulation(
                test_fingerprint, 
                key_pass, 
                {"type": "simulated_ssh_test", "host": "localhost_pgp_test_rig"}
            )
            logger.info(f"Auth Sim Result: {auth_sim_result}")

        except PGPManagementError as e:
            logger.error(f"PGPManager operational error during test: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected generic error during PGPManager test operations: {e}", exc_info=True)
        finally:
            if test_fingerprint:
                logger.info("\n--- Deleting Test Key (Cleanup) ---")
                try:
                    pgp_manager.delete_key(test_fingerprint, secret=True)
                    pgp_manager.delete_key(test_fingerprint, secret=False) # Public part
                    logger.info("Test key deletion processed.")
                except PGPManagementError as e:
                    logger.error(f"Error during test key cleanup: {e}")
    
    except ConfigurationError as e:
        logger.critical(f"PGPManager Test Aborted: GPG Configuration Error - {e}. Ensure GnuPG is installed and accessible.")
    except Exception as e:
        logger.critical(f"PGPManager Test Aborted: Unexpected critical error during PGPManager initialization - {e}", exc_info=True)

    logger.info("PGPManager test finished.")

