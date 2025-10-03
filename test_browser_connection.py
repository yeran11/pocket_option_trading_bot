"""
Browser Connection Test
Tests Chrome/Chromium setup and Pocket Option connectivity
"""
import os
import platform
import sys
import time

def check_system():
    """Check system requirements"""
    print("=" * 60)
    print("SYSTEM CHECK")
    print("=" * 60)

    # Check OS
    os_platform = platform.platform().lower()
    print(f"✓ Operating System: {platform.platform()}")
    print(f"✓ Python Version: {sys.version.split()[0]}")

    # Check Chrome
    chrome_paths = {
        'linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/snap/bin/chromium'
        ],
        'darwin': [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium'
        ],
        'windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ]
    }

    chrome_found = False
    if 'linux' in os_platform:
        for path in chrome_paths['linux']:
            if os.path.exists(path):
                print(f"✓ Chrome/Chromium found: {path}")
                chrome_found = True
                break
    elif 'darwin' in os_platform or 'macos' in os_platform:
        for path in chrome_paths['darwin']:
            if os.path.exists(path):
                print(f"✓ Chrome/Chromium found: {path}")
                chrome_found = True
                break
    elif 'windows' in os_platform:
        for path in chrome_paths['windows']:
            if os.path.exists(path):
                print(f"✓ Chrome found: {path}")
                chrome_found = True
                break

    if not chrome_found:
        print("❌ Chrome/Chromium NOT found!")
        print("\nPlease install Chrome:")
        if 'linux' in os_platform:
            print("  Ubuntu/Debian: sudo apt install google-chrome-stable")
            print("  OR: sudo apt install chromium-browser")
        elif 'darwin' in os_platform or 'macos' in os_platform:
            print("  Download from: https://www.google.com/chrome/")
        elif 'windows' in os_platform:
            print("  Download from: https://www.google.com/chrome/")
        return False

    return True


def check_dependencies():
    """Check Python dependencies"""
    print("\n" + "=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)

    required = {
        'selenium': 'selenium',
        'undetected_chromedriver': 'undetected-chromedriver',
        'tkinter': 'tkinter (built-in)',
    }

    all_ok = True
    for module, package in required.items():
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            if module != 'tkinter':
                print(f"   Install with: pip install {package}")
            all_ok = False

    return all_ok


def test_browser_launch():
    """Test if browser can be launched"""
    print("\n" + "=" * 60)
    print("BROWSER LAUNCH TEST")
    print("=" * 60)

    try:
        import undetected_chromedriver as uc

        print("Setting up Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')

        print("Launching Chrome... (this may take 10-30 seconds first time)")
        print("Chrome will download driver if needed...")

        driver = uc.Chrome(options=options)

        print("✓ Chrome launched successfully!")
        print("✓ Navigating to Pocket Option...")

        driver.get('https://pocket2.click/cabinet/demo-quick-high-low')

        print("✓ Page loaded!")
        print("\n" + "=" * 60)
        print("SUCCESS! Chrome automation is working!")
        print("=" * 60)
        print("\nYou should see a Chrome window opened.")
        print("The bot will work the same way - it opens Chrome automatically.")
        print("\nClosing browser in 10 seconds...")

        time.sleep(10)
        driver.quit()

        print("✓ Browser closed successfully")
        return True

    except Exception as e:
        print(f"❌ Error launching browser: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome is installed")
        print("2. Try: pip install --upgrade undetected-chromedriver")
        print("3. Check your internet connection (downloads driver)")
        return False


def show_connection_guide():
    """Show how to connect to Pocket Option"""
    print("\n" + "=" * 60)
    print("HOW TO CONNECT TO YOUR POCKET OPTION ACCOUNT")
    print("=" * 60)
    print("""
STEP-BY-STEP PROCESS:

1. RUN THE BOT:
   python3 po_bot_free.py

2. CONFIGURE SETTINGS:
   - A GUI window will appear
   - Set your strategy settings (EMAs, RSI, etc.)
   - Click "START TRADING"

3. CHROME OPENS AUTOMATICALLY:
   - The bot will open a Chrome browser
   - It navigates to Pocket Option demo account

4. LOGIN TO YOUR ACCOUNT (FIRST TIME ONLY):
   - In the Chrome window that opened
   - Click "Sign In" or "Register"
   - Enter your credentials
   - Login to your account

   IMPORTANT: Chrome will save this login!
   Next time you run the bot, you'll already be logged in.

5. SWITCH TO DEMO OR REAL:
   - Top right corner shows balance
   - Click to switch between Demo/Real account
   - ⚠️ ALWAYS start with DEMO!

6. ADD FAVORITE ASSETS:
   - Click the asset dropdown (e.g., EUR/USD)
   - Add to favorites (star icon)
   - Bot trades assets in your favorites list

7. BOT STARTS TRADING:
   - The bot watches the charts
   - When signals align, it clicks Call/Put
   - You'll see trades appear in the terminal
   - Stats update in real-time

8. MONITORING:
   - Watch the terminal for logs
   - See win rate, trades, profits
   - Bot respects Take Profit / Stop Loss

9. STOPPING THE BOT:
   - Press Ctrl+C in terminal
   - Or close the Chrome window
   - Settings are saved for next time

BROWSER PROFILE:
- Chrome saves your session in a profile folder
- Location: ~/.config/google-chrome/PO Bot Free (Linux)
- This means you only login once!
- To reset: delete this folder

IMPORTANT NOTES:
✓ Start with DEMO account (switch in top-right)
✓ Add 2-5 favorite assets before starting
✓ Let bot run for at least 1 hour to see results
✓ Monitor first few trades manually
✓ Use Take Profit / Stop Loss limits
    """)


def main():
    """Run all tests"""
    print("\n")
    print("█" * 60)
    print("  POCKET OPTION BOT - CONNECTION TEST")
    print("█" * 60)
    print()

    # Step 1: System check
    if not check_system():
        print("\n❌ System check failed. Install Chrome first.")
        return

    # Step 2: Dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Install missing packages.")
        return

    # Step 3: Browser test
    print("\n⚠️  About to launch Chrome browser for testing...")
    response = input("Continue? (y/n): ")

    if response.lower() == 'y':
        if test_browser_launch():
            print("\n✅ ALL TESTS PASSED!")
            print("\nYour system is ready to run the bot!")
            print("\nNext step:")
            print("  python3 po_bot_free.py")
        else:
            print("\n❌ Browser test failed. Check the errors above.")
    else:
        print("\nBrowser test skipped.")

    # Show connection guide
    show_connection_guide()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
