"""
System-Wide Credential Loader for Desktop Machine
==================================================

This file automatically loads OpenAI API credentials from your desktop user profile.
Set it up ONCE on your machine, and it works for ALL projects!

SETUP INSTRUCTIONS (YOU'VE ALREADY DONE THIS!):
================================================
Created file at: C:\Users\YourUsername\.openai_credentials
With your API keys inside.

HOW IT WORKS:
=============
When you run the trading bot, this script:
1. Checks your home directory for .openai_credentials
2. Loads the API keys automatically
3. Makes them available to ai_config.py
4. No more copying .env files to every project!

SECURITY:
=========
- The credentials file is in your HOME directory (outside git repos)
- It won't be committed to GitHub
- It's private to your user account only
"""

import os
from pathlib import Path

def load_desktop_credentials():
    """
    Load API credentials from desktop user profile.
    Checks multiple locations for maximum compatibility.

    Returns:
        bool: True if credentials loaded successfully, False otherwise
    """
    # Get user home directory (works on Windows, Mac, Linux)
    home = Path.home()

    print(f"🔍 Looking for desktop credentials in: {home}")

    # Check multiple possible locations
    possible_files = [
        home / '.openai_credentials',           # Primary location (Windows/Mac/Linux)
        home / '.openai' / 'credentials',       # Alternative organized location
        home / '.config' / 'openai_credentials', # XDG standard (Linux)
        home / 'openai_credentials.txt',        # Windows-friendly alternative
    ]

    credentials = {}
    found_file = None

    # Try each location
    for cred_file in possible_files:
        if cred_file.exists():
            found_file = cred_file
            print(f"✅ Found desktop credentials at: {cred_file}")
            try:
                with open(cred_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Remove quotes if present
                            value = value.strip('"').strip("'")
                            credentials[key] = value

                # Set as environment variables so ai_config.py can find them
                if 'OPENAI_API_KEY' in credentials:
                    os.environ['OPENAI_API_KEY'] = credentials['OPENAI_API_KEY']
                    api_key_preview = credentials['OPENAI_API_KEY']
                    print(f"✅ Loaded OPENAI_API_KEY from desktop: {api_key_preview[:20]}...{api_key_preview[-4:]} (length: {len(api_key_preview)})")

                if 'OPENAI_PROJECT_ID' in credentials:
                    os.environ['OPENAI_PROJECT_ID'] = credentials['OPENAI_PROJECT_ID']
                    print(f"✅ Loaded OPENAI_PROJECT_ID from desktop")

                print(f"🎉 Desktop credentials loaded successfully from {cred_file}!")
                return True

            except Exception as e:
                print(f"⚠️ Error reading {cred_file}: {e}")
                continue

    # No credentials file found
    print("⚠️ No desktop credentials file found in any of these locations:")
    for i, pf in enumerate(possible_files, 1):
        print(f"   {i}. {pf}")
    print(f"\n💡 TO SET UP DESKTOP CREDENTIALS:")
    print(f"   1. Create file at: {possible_files[0]}")
    print(f"   2. Add your API keys:")
    print(f"      OPENAI_API_KEY=sk-proj-your-key-here")
    print(f"      OPENAI_PROJECT_ID=proj_your-id-here")
    print(f"\n   Windows CMD:")
    print(f"   cd %USERPROFILE%")
    print(f"   notepad .openai_credentials")
    print(f"\n   Mac/Linux Terminal:")
    print(f"   nano ~/.openai_credentials")
    print()
    return False

# Auto-load credentials when this module is imported
# This runs automatically when you do: import load_my_credentials
if __name__ != "__main__":
    load_desktop_credentials()

# If run directly (python load_my_credentials.py), show test results
if __name__ == "__main__":
    print("=" * 80)
    print("DESKTOP CREDENTIALS LOADER TEST")
    print("=" * 80)
    print()

    success = load_desktop_credentials()

    print()
    print("=" * 80)
    if success:
        print("✅ TEST PASSED - Credentials loaded from desktop!")
        print()
        print("Your API key is now available to all Python scripts.")
        print("You can run your trading bot with: python main.py")
    else:
        print("❌ TEST FAILED - No credentials found")
        print()
        print("Follow the setup instructions above to create your credentials file.")
    print("=" * 80)
