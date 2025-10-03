"""
Pocket Option Trading Bot - FREE with AUTO-LOGIN
Login directly through the GUI - no manual browser login needed!
"""
import asyncio
import base64
import json
import operator
import os
import platform
import random
import sys
import time
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox

from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

ops = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
}

# Import all the enhanced trading logic from po_bot_free.py
# (Keep all the indicator functions, strategies, etc.)

URL = 'https://pocket2.click/'
PERIOD = 1
CANDLES = {}
ACTIONS = {}
CURRENT_ASSET = None
FAVORITES_REANIMATED = False
SETTINGS = {}
MARTINGALE_LIST = []
MARTINGALE_LAST_ACTION_ENDS_AT = datetime.now()
MARTINGALE_AMOUNT_SET = False
MARTINGALE_INITIAL = True
NUMBERS = {
    '0': '11',
    '1': '7',
    '2': '8',
    '3': '9',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '1',
    '8': '2',
    '9': '3',
}
INITIAL_DEPOSIT = None
SETTINGS_PATH = 'settings_autologin.txt'
TRADING_ALLOWED = True
LOGGED_IN = False

# Statistics
TOTAL_TRADES = 0
WINNING_TRADES = 0
LOSING_TRADES = 0
WIN_STREAK = 0
LOSE_STREAK = 0


def log(*args):
    """Enhanced logging"""
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *args)


async def get_driver():
    """Initialize Chrome driver"""
    options = uc.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-blink-features=AutomationControlled')

    username = os.environ.get('USER', os.environ.get('USERNAME'))
    os_platform = platform.platform().lower()

    if 'macos' in os_platform:
        path_default = fr'/Users/{username}/Library/Application Support/Google/Chrome/PO Bot AutoLogin'
    elif 'windows' in os_platform:
        path_default = fr'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\PO Bot AutoLogin'
    elif 'linux' in os_platform:
        path_default = '~/.config/google-chrome/PO Bot AutoLogin'
    else:
        path_default = ''

    options.add_argument(fr'--user-data-dir={path_default}')
    driver = uc.Chrome(options=options)
    return driver


async def auto_login(driver, email, password, account_type='demo'):
    """
    Automatically login to Pocket Option
    account_type: 'demo' or 'real'
    """
    global LOGGED_IN

    log(f"Starting auto-login for {email}...")

    try:
        # Navigate to main page
        driver.get(URL)
        await asyncio.sleep(3)

        # Check if already logged in
        try:
            balance = driver.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open')
            log("✓ Already logged in!")
            LOGGED_IN = True
        except:
            log("Not logged in, proceeding with login...")

            # Find and click Sign In button
            try:
                # Try multiple selectors for sign in button
                sign_in_selectors = [
                    "//a[contains(text(), 'Sign in')]",
                    "//button[contains(text(), 'Sign in')]",
                    "//a[contains(@class, 'sign-in')]",
                    ".header__login-btn",
                    "a[href*='login']"
                ]

                sign_in_clicked = False
                for selector in sign_in_selectors:
                    try:
                        if selector.startswith('//'):
                            sign_in_btn = driver.find_element(By.XPATH, selector)
                        else:
                            sign_in_btn = driver.find_element(By.CSS_SELECTOR, selector)

                        sign_in_btn.click()
                        log("✓ Clicked Sign In button")
                        sign_in_clicked = True
                        await asyncio.sleep(2)
                        break
                    except:
                        continue

                if not sign_in_clicked:
                    log("⚠️  Couldn't find Sign In button, trying direct login URL...")
                    driver.get('https://pocket2.click/login/')
                    await asyncio.sleep(2)

            except Exception as e:
                log(f"Error finding sign in button: {e}")

            # Enter email
            try:
                email_selectors = [
                    "input[name='email']",
                    "input[type='email']",
                    "input[placeholder*='mail']",
                    "input[placeholder*='Email']",
                    "#email"
                ]

                email_entered = False
                for selector in email_selectors:
                    try:
                        email_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        email_field.clear()
                        email_field.send_keys(email)
                        log("✓ Entered email")
                        email_entered = True
                        break
                    except:
                        continue

                if not email_entered:
                    raise Exception("Could not find email field")

            except Exception as e:
                log(f"❌ Error entering email: {e}")
                return False

            # Enter password
            try:
                password_selectors = [
                    "input[name='password']",
                    "input[type='password']",
                    "input[placeholder*='assword']",
                    "#password"
                ]

                password_entered = False
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, selector)
                        password_field.clear()
                        password_field.send_keys(password)
                        log("✓ Entered password")
                        password_entered = True
                        break
                    except:
                        continue

                if not password_entered:
                    raise Exception("Could not find password field")

            except Exception as e:
                log(f"❌ Error entering password: {e}")
                return False

            # Click login/submit button
            try:
                login_selectors = [
                    "button[type='submit']",
                    "button[contains(text(), 'Sign in')]",
                    "button[contains(text(), 'Login')]",
                    "button[contains(text(), 'Log in')]",
                    ".login-btn",
                    "input[type='submit']"
                ]

                login_clicked = False
                for selector in login_selectors:
                    try:
                        if 'contains' in selector:
                            login_btn = driver.find_element(By.XPATH, f"//{selector}")
                        else:
                            login_btn = driver.find_element(By.CSS_SELECTOR, selector)

                        login_btn.click()
                        log("✓ Clicked Login button")
                        login_clicked = True
                        break
                    except:
                        continue

                if not login_clicked:
                    # Try pressing Enter on password field
                    password_field.send_keys(Keys.RETURN)
                    log("✓ Pressed Enter to login")

                await asyncio.sleep(5)

            except Exception as e:
                log(f"❌ Error clicking login: {e}")
                return False

            # Verify login successful
            try:
                balance = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open'))
                )
                log("✓ Login successful!")
                LOGGED_IN = True
            except:
                log("❌ Login failed - could not find balance element")
                return False

        # Navigate to trading page
        trading_url = 'https://pocket2.click/cabinet/demo-quick-high-low' if account_type == 'demo' else 'https://pocket2.click/cabinet/quick-high-low'
        driver.get(trading_url)
        log(f"✓ Navigated to {account_type.upper()} account")
        await asyncio.sleep(5)

        # Switch to demo/real if needed
        await switch_account_type(driver, account_type)

        return True

    except Exception as e:
        log(f"❌ Auto-login failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def switch_account_type(driver, account_type='demo'):
    """Switch between demo and real account"""
    try:
        # Click balance dropdown
        balance = driver.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open')
        balance.click()
        await asyncio.sleep(1)

        # Find and click demo or real option
        if account_type == 'demo':
            try:
                demo_option = driver.find_element(By.XPATH, "//div[contains(text(), 'DEMO')]")
                demo_option.click()
                log("✓ Switched to DEMO account")
            except:
                log("Already on DEMO account or couldn't switch")
        else:
            try:
                real_option = driver.find_element(By.XPATH, "//div[contains(text(), 'REAL')]")
                real_option.click()
                log("✓ Switched to REAL account")
                log("⚠️  WARNING: Trading with real money!")
            except:
                log("Already on REAL account or couldn't switch")

        await asyncio.sleep(2)

    except Exception as e:
        log(f"Could not switch account type: {e}")


# ===== IMPORT ALL TRADING LOGIC FROM po_bot_free.py =====
# (Include all indicator calculations, strategies, etc.)
# For brevity, I'll include key functions with comment placeholders

async def websocket_log(driver):
    """Process WebSocket data - SAME AS po_bot_free.py"""
    # [Include full implementation from po_bot_free.py]
    pass

async def calculate_ema(candles, period):
    """EMA calculation - SAME AS po_bot_free.py"""
    if len(candles) < period:
        return None
    closes = [c[2] for c in candles]
    multiplier = 2 / (period + 1)
    sma = sum(closes[:period]) / period
    ema = sma
    for price in closes[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

async def calculate_rsi(candles, period=14):
    """RSI calculation - SAME AS po_bot_free.py"""
    if len(candles) < period + 1:
        return None
    closes = [c[2] for c in candles]
    gains, losses = [], []
    for i in range(1, period + 1):
        delta = closes[i] - closes[i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# [Include ALL other functions from po_bot_free.py]
# For this example, showing structure...

async def main():
    """Main bot loop with auto-login"""
    driver = await get_driver()

    # Auto-login
    email = SETTINGS.get('EMAIL', '')
    password = SETTINGS.get('PASSWORD', '')
    account_type = SETTINGS.get('ACCOUNT_TYPE', 'demo')

    if not email or not password:
        log("❌ Email or password not set!")
        return

    login_success = await auto_login(driver, email, password, account_type)

    if not login_success:
        log("❌ Could not login automatically")
        log("Please check your credentials and try again")
        return

    log("=" * 60)
    log("AUTO-LOGIN SUCCESSFUL - BOT STARTED")
    log("=" * 60)
    log(f"Account: {account_type.upper()}")
    log("Waiting for trading data...")

    # Continue with normal trading loop
    while True:
        if not TRADING_ALLOWED:
            log("Trading halted")
            await asyncio.sleep(5)
            continue

        # [Include all trading logic from po_bot_free.py]
        await asyncio.sleep(0.5)


# ===== ENHANCED GUI WITH LOGIN =====

def tkinter_run():
    """GUI with login fields"""
    window = Tk()
    window.geometry('750x500')
    window.title('🚀 Pocket Option Bot - AUTO-LOGIN VERSION')
    window.configure(bg='#f0f0f0')

    # Read saved settings
    from po_bot_free import read_settings
    read_settings()

    # Header
    header_frame = Frame(window, bg='#4CAF50')
    header_frame.grid(column=0, row=0, columnspan=6, sticky='ew')
    Label(header_frame, text='POCKET OPTION BOT - AUTO-LOGIN',
          font=('Arial', 14, 'bold'), bg='#4CAF50', fg='white').pack(pady=10)

    # ===== LOGIN SECTION =====
    login_frame = LabelFrame(window, text='📧 LOGIN CREDENTIALS', font=('Arial', 10, 'bold'),
                              bg='#e3f2fd', padx=10, pady=10)
    login_frame.grid(column=0, row=1, columnspan=6, sticky='ew', padx=10, pady=10)

    Label(login_frame, text='Email:', bg='#e3f2fd').grid(column=0, row=0, sticky=W, padx=5)
    ent_email = Entry(login_frame, width=30)
    ent_email.insert(0, SETTINGS.get('EMAIL', ''))
    ent_email.grid(column=1, row=0, padx=5, pady=5)

    Label(login_frame, text='Password:', bg='#e3f2fd').grid(column=0, row=1, sticky=W, padx=5)
    ent_password = Entry(login_frame, width=30, show='*')
    ent_password.insert(0, SETTINGS.get('PASSWORD', ''))
    ent_password.grid(column=1, row=1, padx=5, pady=5)

    # Show/hide password
    def toggle_password():
        if chk_show_pass.get():
            ent_password.config(show='')
        else:
            ent_password.config(show='*')

    chk_show_pass = IntVar()
    Checkbutton(login_frame, text='Show password', variable=chk_show_pass,
                command=toggle_password, bg='#e3f2fd').grid(column=1, row=2, sticky=W, padx=5)

    # Account type
    Label(login_frame, text='Account Type:', bg='#e3f2fd', font=('Arial', 9, 'bold')).grid(column=2, row=0, sticky=W, padx=20)
    account_var = StringVar(value=SETTINGS.get('ACCOUNT_TYPE', 'demo'))
    Radiobutton(login_frame, text='💰 DEMO (Practice)', variable=account_var, value='demo',
                bg='#e3f2fd', font=('Arial', 9)).grid(column=2, row=1, sticky=W, padx=20)
    Radiobutton(login_frame, text='💵 REAL (Real Money)', variable=account_var, value='real',
                bg='#e3f2fd', font=('Arial', 9), fg='red').grid(column=2, row=2, sticky=W, padx=20)

    # Save credentials option
    chk_save_creds = IntVar(value=SETTINGS.get('SAVE_CREDENTIALS', 0))
    Checkbutton(login_frame, text='💾 Save credentials (stored in settings file)',
                variable=chk_save_creds, bg='#e3f2fd').grid(column=0, row=3, columnspan=2, sticky=W, padx=5, pady=5)

    Label(login_frame, text='⚠️  Start with DEMO account! Only use REAL after testing.',
          bg='#e3f2fd', fg='red', font=('Arial', 8, 'bold')).grid(column=0, row=4, columnspan=3, pady=5)

    # ===== STRATEGY SETTINGS =====
    strategy_frame = LabelFrame(window, text='📊 STRATEGY', font=('Arial', 9, 'bold'), bg='#f0f0f0')
    strategy_frame.grid(column=0, row=2, padx=10, pady=5, sticky='nsew')

    Label(strategy_frame, text='Fast EMA:', bg='#f0f0f0').grid(column=0, row=0, sticky=W)
    ent_fast_ma = Entry(strategy_frame, width=5)
    ent_fast_ma.insert(0, str(SETTINGS.get('FAST_MA', 9)))
    ent_fast_ma.grid(column=0, row=0, sticky=E)

    Label(strategy_frame, text='Slow EMA:', bg='#f0f0f0').grid(column=0, row=1, sticky=W)
    ent_slow_ma = Entry(strategy_frame, width=5)
    ent_slow_ma.insert(0, str(SETTINGS.get('SLOW_MA', 21)))
    ent_slow_ma.grid(column=0, row=1, sticky=E)

    chk_rsi_var = IntVar(value=1 if SETTINGS.get('RSI_ENABLED', True) else 0)
    Checkbutton(strategy_frame, text='Use RSI', variable=chk_rsi_var, bg='#f0f0f0').grid(column=0, row=2, sticky=W)

    Label(strategy_frame, text='Min Confidence:', bg='#f0f0f0').grid(column=0, row=3, sticky=W)
    ent_confidence = Entry(strategy_frame, width=5)
    ent_confidence.insert(0, str(SETTINGS.get('MIN_CONFIDENCE', 4)))
    ent_confidence.grid(column=0, row=3, sticky=E)

    # ===== RISK MANAGEMENT =====
    risk_frame = LabelFrame(window, text='🛡️ RISK MANAGEMENT', font=('Arial', 9, 'bold'), bg='#f0f0f0')
    risk_frame.grid(column=1, row=2, padx=10, pady=5, sticky='nsew')

    Label(risk_frame, text='Min Payout %:', bg='#f0f0f0').grid(column=0, row=0, sticky=W)
    ent_payout = Entry(risk_frame, width=5)
    ent_payout.insert(0, str(SETTINGS.get('MIN_PAYOUT', 85)))
    ent_payout.grid(column=0, row=0, sticky=E)

    chk_tp = IntVar(value=1 if SETTINGS.get('TAKE_PROFIT_ENABLED', False) else 0)
    Checkbutton(risk_frame, text='Take Profit $', variable=chk_tp, bg='#f0f0f0').grid(column=0, row=1, sticky=W)
    ent_tp = Entry(risk_frame, width=5)
    ent_tp.insert(0, str(SETTINGS.get('TAKE_PROFIT', 100)))
    ent_tp.grid(column=0, row=1, sticky=E)

    chk_sl = IntVar(value=1 if SETTINGS.get('STOP_LOSS_ENABLED', False) else 0)
    Checkbutton(risk_frame, text='Stop Loss $', variable=chk_sl, bg='#f0f0f0').grid(column=0, row=2, sticky=W)
    ent_sl = Entry(risk_frame, width=5)
    ent_sl.insert(0, str(SETTINGS.get('STOP_LOSS', 50)))
    ent_sl.grid(column=0, row=2, sticky=E)

    # ===== MARTINGALE =====
    mart_frame = LabelFrame(window, text='🎲 MARTINGALE (Optional)', font=('Arial', 9, 'bold'), bg='#f0f0f0')
    mart_frame.grid(column=2, row=2, padx=10, pady=5, sticky='nsew')

    chk_mart = IntVar(value=1 if SETTINGS.get('MARTINGALE_ENABLED', False) else 0)
    Checkbutton(mart_frame, text='Enable Martingale', variable=chk_mart, bg='#f0f0f0').grid(column=0, row=0, sticky=W)

    Label(mart_frame, text='Bet Sequence:', bg='#f0f0f0').grid(column=0, row=1, sticky=W)
    ent_mart = Entry(mart_frame, width=15)
    ent_mart.insert(0, ', '.join([str(v) for v in SETTINGS.get('MARTINGALE_LIST', [1, 2, 4, 8])]))
    ent_mart.grid(column=0, row=2)

    # Info section
    info_frame = Frame(window, bg='#fff3cd', relief='solid', borderwidth=1)
    info_frame.grid(column=0, row=3, columnspan=6, sticky='ew', padx=10, pady=10)
    Label(info_frame, text='ℹ️  Enter your Pocket Option email & password → Select DEMO → Click START → Bot logs in and trades automatically!',
          bg='#fff3cd', font=('Arial', 9), wraplength=700, justify=LEFT).pack(padx=10, pady=10)

    # Error label
    error_var = StringVar()
    Label(window, textvariable=error_var, fg='red', bg='#f0f0f0', font=('Arial', 9, 'bold')).grid(column=0, row=4, columnspan=6)

    # Buttons
    def validate_and_run():
        """Validate inputs and start bot"""
        error_var.set('')

        email = ent_email.get().strip()
        password = ent_password.get().strip()

        if not email or '@' not in email:
            error_var.set('❌ Please enter a valid email address')
            return

        if not password or len(password) < 4:
            error_var.set('❌ Please enter your password')
            return

        if account_var.get() == 'real':
            confirmed = messagebox.askyesno(
                "⚠️ WARNING - REAL MONEY",
                "You selected REAL account!\n\n"
                "This will trade with YOUR REAL MONEY.\n\n"
                "Are you sure you want to continue?\n\n"
                "Recommended: Start with DEMO first!"
            )
            if not confirmed:
                return

        # Save settings
        from po_bot_free import save_settings
        save_settings(
            EMAIL=email if chk_save_creds.get() else '',
            PASSWORD=password if chk_save_creds.get() else '',
            ACCOUNT_TYPE=account_var.get(),
            SAVE_CREDENTIALS=chk_save_creds.get(),
            FAST_MA=int(ent_fast_ma.get()),
            SLOW_MA=int(ent_slow_ma.get()),
            MIN_PAYOUT=int(ent_payout.get()),
            RSI_ENABLED=bool(chk_rsi_var.get()),
            MIN_CONFIDENCE=int(ent_confidence.get()),
            TAKE_PROFIT_ENABLED=bool(chk_tp.get()),
            TAKE_PROFIT=int(ent_tp.get()),
            STOP_LOSS_ENABLED=bool(chk_sl.get()),
            STOP_LOSS=int(ent_sl.get()),
            MARTINGALE_ENABLED=bool(chk_mart.get()),
            MARTINGALE_LIST=ent_mart.get(),
            RSI_PERIOD=14,
            RSI_UPPER=70,
            VICE_VERSA=False,
            USE_TREND_FOLLOWING=False,
            USE_MEAN_REVERSION=False,
        )

        # Store credentials for this session even if not saving
        SETTINGS['EMAIL'] = email
        SETTINGS['PASSWORD'] = password
        SETTINGS['ACCOUNT_TYPE'] = account_var.get()

        window.destroy()

    btn_frame = Frame(window, bg='#f0f0f0')
    btn_frame.grid(column=0, row=5, columnspan=6, pady=15)

    Button(btn_frame, text='🚀 START AUTO-LOGIN & TRADING',
           command=validate_and_run, bg='#4CAF50', fg='white',
           font=('Arial', 12, 'bold'), padx=30, pady=10).pack()

    window.mainloop()


if __name__ == '__main__':
    try:
        tkinter_run()
        log("=" * 60)
        log("POCKET OPTION BOT - AUTO-LOGIN VERSION")
        log("=" * 60)

        # Import full trading logic from po_bot_free
        import sys
        sys.path.insert(0, '/home/runner/workspace/pocket_option_trading_bot/')

        # Run main loop
        asyncio.run(main())

    except KeyboardInterrupt:
        log("\nBot stopped by user")
    except Exception as e:
        log(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
