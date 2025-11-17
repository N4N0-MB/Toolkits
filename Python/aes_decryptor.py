import pyAesCrypt
import os
import sys
import argparse
import time

def main():
# --- ARGUMENT SETUP --- #
    parser = argparse.ArgumentParser(
        description="Brute-force script for pyAesCrypt (.aes) files.",
        epilog="Example: python3 AesDecrypter.py -f secret.zip.aes -w /usr/share/wordlists/path"
    )
    
    # Argument for the encrypted file
    parser.add_argument(
        "-f", "--file",
        dest="encrypted_file",
        required=True,
        help="Path to the encrypted .aes file."
    )
    
    # Argument for the wordlist
    parser.add_argument(
        "-w", "--wordlist",
        dest="wordlist_path",
        required=True,
        help="Path to the dictionary or wordlist."
    )
    
    args = parser.parse_args()

# --- VARs SETUP --- #
    encrypted_file = args.encrypted_file
    wordlist_path = args.wordlist_path
    
    # Automatically derive the output name
    # "secret.zip.aes" will become "secret.zip"
    decrypted_file = os.path.splitext(encrypted_file)[0]
    
    bufferSize = 64 * 1024  # 64k
    
# --- FILE VALIDATION --- #
    if not os.path.exists(encrypted_file):
        print(f"\n⚠️ Error: Encrypted file not found at '{encrypted_file}'.")
        sys.exit(1)

    if not encrypted_file.endswith(".aes"):
        print(f"\n⚠️ Error: The input file must be a AES file. Provided file: '{encrypted_file}'")
        sys.exit(1)

    if not os.path.exists(wordlist_path):
        print(f"\n⚠️ Error: Wordlist not found at '{wordlist_path}'.")
        sys.exit(1)

    try:
        filesize = os.path.getsize(encrypted_file)
    except Exception as e:
        print(f"\n⚠️ Error reading size of '{encrypted_file}': {e}")
        sys.exit(1)

    print(f"\n🔒 Target: {encrypted_file} [ Output: {decrypted_file} ]")
    print(f"🗒️ Wordlist: {wordlist_path}\n")
    print("--- Starting attack ---")
    
    password_found = False
    start_time = time.time()

# --- BRUTE-FORCE LOOP --- #
    try:
        # Open the wordlist with utf-8 encoding and ignore errors
        with open(wordlist_path, "r", encoding='utf-8', errors='ignore') as f_wordlist:
            for i, line in enumerate(f_wordlist):
                password = line.strip()
                if not password:
                    continue

                try:
                    # Print on the same line to avoid flooding the console
                    sys.stdout.write(f"\r🔵 Trying (Attempt #{i+1}): {password.ljust(40)}")
                    sys.stdout.flush()

                    with open(encrypted_file, "rb") as fIn:
                        with open(decrypted_file, "wb") as fOut:
                            # Attempt to decrypt
                            pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize)
                    
                    # --- SUCCESS --- #
                    end_time = time.time()
                    elapsed = end_time - start_time
                    
                    print("\n")
                    print(f"🟢 PASSWORD FOUND!")
                    print(f"🔑 Password: {password}")
                    print(f"⛓️‍💥 Attempts: {i+1}")
                    print(f"⏳ Time: {elapsed:.2f} seconds")
                    print(f"💾 File saved as: {decrypted_file}")

                    password_found = True
                    break  # Break out of the 'for' loop

                except ValueError:
                    # Incorrect password, continue to the next one
                    continue 
                
                except Exception as e:
                    print(f"\n⚠️ Unexpected error with pass '{password}': {e}")
                    continue

    except KeyboardInterrupt:
        print("\n🟡 Process interrupted by user (Ctrl+C).")

    except Exception as e:
        print(f"\n⚠️ Fatal error reading wordlist: {e}")

    finally:
        if not password_found:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"🔴 Attack finished after {elapsed:.2f}s. Password not found.")
            
            # Clean up the output file if it was created empty or corrupt
            if os.path.exists(decrypted_file) and not password_found:
                if os.path.getsize(decrypted_file) == 0:
                    os.remove(decrypted_file)

# --- SCRIPT ENTRY POINT --- #
if __name__ == "__main__":
    main()