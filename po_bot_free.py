"""
Pocket Option Trading Bot - FREE Enhanced Version
No licensing, no payments, improved strategies
"""
import asyncio
import base64
import json
import operator
import os
import platform
import random
import sys
from datetime import datetime, timedelta
from tkinter import *

from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

ops = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
}

# CONFIGURATION
URL = 'https://pocket2.click/cabinet/demo-quick-high-low?utm_campaign=806509&utm_source=affiliate&utm_medium=sr&a=ovlztqbPkiBiOt&ac=github'
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
SETTINGS_PATH = 'settings_free.txt'
TRADING_ALLOWED = True

# Statistics
TOTAL_TRADES = 0
WINNING_TRADES = 0
LOSING_TRADES = 0
WIN_STREAK = 0
LOSE_STREAK = 0
MAX_WIN_STREAK = 0
MAX_LOSE_STREAK = 0


def log(*args):
    """Enhanced logging with timestamp"""
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *args)


async def get_driver():
    """Initialize Chrome driver with undetected settings"""
    options = uc.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--headless=new')  # Uncomment for headless mode

    username = os.environ.get('USER', os.environ.get('USERNAME'))
    os_platform = platform.platform().lower()

    if 'macos' in os_platform:
        path_default = fr'/Users/{username}/Library/Application Support/Google/Chrome/PO Bot Free'
    elif 'windows' in os_platform:
        path_default = fr'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\PO Bot Free'
    elif 'linux' in os_platform:
        path_default = '~/.config/google-chrome/PO Bot Free'
    else:
        path_default = ''

    options.add_argument(fr'--user-data-dir={path_default}')
    driver = uc.Chrome(options=options)
    return driver


async def websocket_log(driver):
    """Process WebSocket data and update candles"""
    global CANDLES, PERIOD, CURRENT_ASSET, FAVORITES_REANIMATED

    for wsData in driver.get_log('performance'):
        message = json.loads(wsData['message'])['message']
        response = message.get('params', {}).get('response', {})
        if response.get('opcode', 0) == 2:
            payload_str = base64.b64decode(response['payloadData']).decode('utf-8')
            data = json.loads(payload_str)

            if 'history' in data:
                if not CURRENT_ASSET:
                    CURRENT_ASSET = data['asset']
                if PERIOD != data['period']:
                    PERIOD = data['period']
                    CANDLES = {}
                    FAVORITES_REANIMATED = False

                candles = list(reversed(data['candles']))
                for tstamp, value in data['history']:
                    tstamp = int(float(tstamp))
                    candle = [tstamp, value, value, value, value]
                    candle[2] = value  # close
                    if value > candle[3]:  # high
                        candle[3] = value
                    if value < candle[4]:  # low
                        candle[4] = value
                    if tstamp % PERIOD == 0:
                        if tstamp not in [c[0] for c in candles]:
                            candles.append([tstamp, value, value, value, value])
                CANDLES[data['asset']] = candles

            try:
                asset = data[0][0]
                candles = CANDLES[asset]
                current_value = data[0][2]
                candles[-1][2] = current_value  # close
                if current_value > candles[-1][3]:  # high
                    candles[-1][3] = current_value
                if current_value < candles[-1][4]:  # low
                    candles[-1][4] = current_value
                tstamp = int(float(data[0][1]))
                if tstamp % PERIOD == 0:
                    if tstamp not in [c[0] for c in candles]:
                        candles.append([tstamp, current_value, current_value, current_value, current_value])
            except:
                pass

    if not FAVORITES_REANIMATED:
        try:
            await reanimate_favorites(driver)
        except:
            pass


async def reanimate_favorites(driver):
    """Activate all favorite assets"""
    global CURRENT_ASSET, FAVORITES_REANIMATED

    asset_favorites_items = driver.find_elements(By.CLASS_NAME, 'assets-favorites-item')
    for item in asset_favorites_items:
        while True:
            if 'assets-favorites-item--active' in item.get_attribute('class'):
                CURRENT_ASSET = item.get_attribute('data-id')
                break
            if 'assets-favorites-item--not-active' in item.get_attribute('class'):
                break
            try:
                item.click()
                FAVORITES_REANIMATED = True
            except ElementNotInteractableException:
                log(f"Asset {item.get_attribute('data-id')} out of reach")
                break


async def switch_to_asset(driver, asset):
    """Switch to specific asset"""
    global CURRENT_ASSET

    asset_favorites_items = driver.find_elements(By.CLASS_NAME, 'assets-favorites-item')
    for item in asset_favorites_items:
        if item.get_attribute('data-id') != asset:
            continue
        while True:
            await asyncio.sleep(0.1)
            if 'assets-favorites-item--active' in item.get_attribute('class'):
                CURRENT_ASSET = asset
                return True
            try:
                item.click()
            except:
                log(f'Asset {asset} out of reach')
                return False

    if asset == CURRENT_ASSET:
        return True


async def check_payout(driver, asset):
    """Check if payout meets minimum requirement"""
    global ACTIONS

    payout = driver.find_element(By.CLASS_NAME, 'value__val-start').text
    if int(payout[1:-1]) >= SETTINGS['MIN_PAYOUT']:
        return True
    log(f'Payout {payout[1:]} too low for {asset}')
    ACTIONS[asset] = datetime.now() + timedelta(minutes=1)
    return False


async def create_order(driver, action, asset, reason=""):
    """Create trading order"""
    global ACTIONS, TOTAL_TRADES

    if ACTIONS.get(asset) and ACTIONS[asset] + timedelta(seconds=PERIOD * 2) > datetime.now():
        return False

    try:
        switch = await switch_to_asset(driver, asset)
        if not switch:
            return False

        ok_payout = await check_payout(driver, asset)
        if not ok_payout:
            return False

        if SETTINGS.get('VICE_VERSA'):
            action = 'call' if action == 'put' else 'put'

        driver.find_element(by=By.CLASS_NAME, value=f'btn-{action}').click()
        ACTIONS[asset] = datetime.now()
        TOTAL_TRADES += 1
        log(f'{action.upper()} on {asset} - {reason} | Total trades: {TOTAL_TRADES}')
    except:
        log("Can't create order")
        return False
    return True


# ==================== ENHANCED TECHNICAL INDICATORS ====================

async def calculate_sma(candles, period):
    """Simple Moving Average"""
    if len(candles) < period:
        return None
    closes = [c[2] for c in candles[-period:]]
    return sum(closes) / period


async def calculate_ema(candles, period):
    """Exponential Moving Average"""
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
    """Relative Strength Index"""
    if len(candles) < period + 1:
        return None

    closes = [c[2] for c in candles]
    gains = []
    losses = []

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
    rsi = 100 - (100 / (1 + rs))

    return rsi


async def calculate_bollinger_bands(candles, period=20, std_dev=2):
    """Bollinger Bands (Upper, Middle, Lower)"""
    if len(candles) < period:
        return None, None, None

    closes = [c[2] for c in candles[-period:]]
    sma = sum(closes) / period

    variance = sum((x - sma) ** 2 for x in closes) / period
    std = variance ** 0.5

    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)

    return upper, sma, lower


async def calculate_macd(candles, fast=12, slow=26, signal=9):
    """MACD (Moving Average Convergence Divergence)"""
    if len(candles) < slow:
        return None, None, None

    ema_fast = await calculate_ema(candles, fast)
    ema_slow = await calculate_ema(candles, slow)

    if ema_fast is None or ema_slow is None:
        return None, None, None

    macd_line = ema_fast - ema_slow

    # Simple signal line calculation
    signal_line = macd_line  # Simplified
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


async def calculate_atr(candles, period=14):
    """Average True Range (Volatility)"""
    if len(candles) < period + 1:
        return None

    true_ranges = []
    for i in range(-period, 0):
        high = candles[i][3]
        low = candles[i][4]
        prev_close = candles[i-1][2]

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)

    return sum(true_ranges) / period


async def detect_support_resistance(candles, lookback=20):
    """Detect support and resistance levels"""
    if len(candles) < lookback:
        return None, None

    recent = candles[-lookback:]
    highs = [c[3] for c in recent]
    lows = [c[4] for c in recent]

    resistance = max(highs)
    support = min(lows)

    return support, resistance


# ==================== ADVANCED STRATEGY ENGINE ====================

async def enhanced_strategy(candles):
    """
    Multi-indicator strategy combining:
    - Moving Average Crossover
    - RSI Overbought/Oversold
    - Bollinger Bands
    - MACD
    - Support/Resistance
    - Volatility Filter
    """
    if len(candles) < 50:
        return None

    current_price = candles[-1][2]

    # Calculate all indicators
    ema_fast = await calculate_ema(candles, SETTINGS.get('FAST_MA', 9))
    ema_slow = await calculate_ema(candles, SETTINGS.get('SLOW_MA', 21))
    ema_fast_prev = await calculate_ema(candles[:-1], SETTINGS.get('FAST_MA', 9))
    ema_slow_prev = await calculate_ema(candles[:-1], SETTINGS.get('SLOW_MA', 21))

    rsi = await calculate_rsi(candles, SETTINGS.get('RSI_PERIOD', 14))
    upper_bb, middle_bb, lower_bb = await calculate_bollinger_bands(candles, 20, 2)
    macd_line, signal_line, histogram = await calculate_macd(candles)
    atr = await calculate_atr(candles)
    support, resistance = await detect_support_resistance(candles)

    if None in [ema_fast, ema_slow, rsi, upper_bb, lower_bb]:
        return None

    # Signal counters
    call_signals = 0
    put_signals = 0

    # 1. Moving Average Crossover
    if ema_fast_prev < ema_slow_prev and ema_fast > ema_slow:
        call_signals += 3  # Strong signal
    elif ema_fast_prev > ema_slow_prev and ema_fast < ema_slow:
        put_signals += 3

    # 2. RSI Analysis
    if SETTINGS.get('RSI_ENABLED', True):
        rsi_upper = SETTINGS.get('RSI_UPPER', 70)
        rsi_lower = 100 - rsi_upper

        if rsi < rsi_lower:  # Oversold -> potential call
            call_signals += 2
        elif rsi > rsi_upper:  # Overbought -> potential put
            put_signals += 2

        # Extreme levels
        if rsi < 30:
            call_signals += 1
        elif rsi > 70:
            put_signals += 1

    # 3. Bollinger Bands
    if current_price <= lower_bb:  # Price at lower band -> potential bounce up
        call_signals += 2
    elif current_price >= upper_bb:  # Price at upper band -> potential bounce down
        put_signals += 2

    # 4. Price vs Middle BB
    if current_price < middle_bb and ema_fast > ema_slow:
        call_signals += 1
    elif current_price > middle_bb and ema_fast < ema_slow:
        put_signals += 1

    # 5. Support/Resistance
    if support and resistance:
        price_range = resistance - support
        if current_price < support + (price_range * 0.2):  # Near support
            call_signals += 1
        elif current_price > resistance - (price_range * 0.2):  # Near resistance
            put_signals += 1

    # 6. Volatility Filter (ATR)
    if atr:
        avg_price = sum([c[2] for c in candles[-20:]]) / 20
        volatility_percent = (atr / avg_price) * 100

        # Skip trading in extremely volatile conditions
        if volatility_percent > 5:  # Too volatile
            log(f"Skipping trade - High volatility: {volatility_percent:.2f}%")
            return None

    # 7. Trend Strength
    if ema_fast > ema_slow:
        trend_strength = ((ema_fast - ema_slow) / ema_slow) * 100
        if trend_strength > 0.5:
            call_signals += 1
    else:
        trend_strength = ((ema_slow - ema_fast) / ema_fast) * 100
        if trend_strength > 0.5:
            put_signals += 1

    # Decision Logic
    signal_diff = abs(call_signals - put_signals)
    min_confidence = SETTINGS.get('MIN_CONFIDENCE', 4)  # Minimum signal strength

    if call_signals > put_signals and signal_diff >= min_confidence:
        confidence = (call_signals / (call_signals + put_signals)) * 100
        return 'call', f'Confidence: {confidence:.1f}% ({call_signals} signals)'
    elif put_signals > call_signals and signal_diff >= min_confidence:
        confidence = (put_signals / (call_signals + put_signals)) * 100
        return 'put', f'Confidence: {confidence:.1f}% ({put_signals} signals)'

    return None


async def trend_following_strategy(candles):
    """Pure trend following with multiple timeframe confirmation"""
    if len(candles) < 50:
        return None

    # Short term trend
    ema_9 = await calculate_ema(candles, 9)
    ema_21 = await calculate_ema(candles, 21)

    # Medium term trend
    ema_50 = await calculate_ema(candles[-50:], 50) if len(candles) >= 50 else None

    current_price = candles[-1][2]

    # All EMAs must align
    if ema_9 and ema_21 and ema_50:
        if ema_9 > ema_21 > ema_50 and current_price > ema_9:
            return 'call', 'Strong uptrend - all EMAs aligned'
        elif ema_9 < ema_21 < ema_50 and current_price < ema_9:
            return 'put', 'Strong downtrend - all EMAs aligned'

    return None


async def mean_reversion_strategy(candles):
    """Mean reversion strategy using Bollinger Bands"""
    if len(candles) < 30:
        return None

    upper_bb, middle_bb, lower_bb = await calculate_bollinger_bands(candles, 20, 2.5)

    if not upper_bb:
        return None

    current_price = candles[-1][2]
    prev_price = candles[-2][2]

    # Price touched lower band and starting to reverse
    if prev_price <= lower_bb and current_price > lower_bb:
        return 'call', 'Mean reversion - bouncing from lower BB'

    # Price touched upper band and starting to reverse
    if prev_price >= upper_bb and current_price < upper_bb:
        return 'put', 'Mean reversion - bouncing from upper BB'

    return None


async def check_strategies(candles):
    """Run all strategies and combine signals"""

    # Primary strategy
    result = await enhanced_strategy(candles)
    if result:
        return result

    # Backup strategies
    if SETTINGS.get('USE_TREND_FOLLOWING', False):
        result = await trend_following_strategy(candles)
        if result:
            return result

    if SETTINGS.get('USE_MEAN_REVERSION', False):
        result = await mean_reversion_strategy(candles)
        if result:
            return result

    return None


# ==================== MARTINGALE & RISK MANAGEMENT ====================

async def hand_delay():
    """Random human-like delay"""
    await asyncio.sleep(random.uniform(0.2, 0.6))


async def set_amount_icon(driver):
    """Ensure amount is in USD not percentage"""
    try:
        amount_style = driver.find_element(By.CSS_SELECTOR, value='#put-call-buttons-chart-1 > div > div.blocks-wrap > div.block.block--bet-amount > div.block__control.control > div.control-buttons__wrapper > div > a')
        try:
            amount_style.find_element(By.CLASS_NAME, value='currency-icon--usd')
        except NoSuchElementException:
            amount_style.click()
    except:
        pass


async def set_estimation_icon(driver):
    """Set estimation to time mode"""
    try:
        time_style = driver.find_element(By.CSS_SELECTOR, value='#put-call-buttons-chart-1 > div > div.blocks-wrap > div.block.block--expiration-inputs > div.block__control.control > div.control-buttons__wrapper > div > a > div > div > svg')
        if 'exp-mode-2.svg' in time_style.get_attribute('data-src'):
            time_style.click()
    except:
        pass


async def get_estimation(driver):
    """Get current estimation time in seconds"""
    try:
        estimation = driver.find_element(By.CSS_SELECTOR, value='#put-call-buttons-chart-1 > div > div.blocks-wrap > div.block.block--expiration-inputs > div.block__control.control > div.control__value.value.value--several-items')
        est = datetime.strptime(estimation.text, '%H:%M:%S')
        return (est.hour * 3600) + (est.minute * 60) + est.second
    except:
        return 60


async def manage_martingale(driver):
    """Smart Martingale management with safety limits"""
    global MARTINGALE_AMOUNT_SET, MARTINGALE_INITIAL, MARTINGALE_LIST, WINNING_TRADES, LOSING_TRADES, WIN_STREAK, LOSE_STREAK

    if not SETTINGS.get('MARTINGALE_ENABLED'):
        return

    MARTINGALE_LIST = SETTINGS.get('MARTINGALE_LIST', [1, 2, 4, 8, 16])
    base = '#modal-root > div > div > div > div > div.trading-panel-modal__in > div.virtual-keyboard > div > div:nth-child(%s) > div'

    # Set initial amount
    if MARTINGALE_INITIAL:
        try:
            await set_amount_icon(driver)
            amount = driver.find_element(By.CSS_SELECTOR, value='#put-call-buttons-chart-1 > div > div.blocks-wrap > div.block.block--bet-amount > div.block__control.control > div.control__value.value.value--several-items > div > input[type=text]')
            amount_value = int(float((amount.get_attribute('value').replace(',', ''))))
            if amount_value != MARTINGALE_LIST[0]:
                amount.click()
                for number in str(MARTINGALE_LIST[0]):
                    driver.find_element(By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                    await hand_delay()
            MARTINGALE_INITIAL = False
            MARTINGALE_AMOUNT_SET = True
        except:
            return

    # Check recent trades and adjust
    if not MARTINGALE_AMOUNT_SET:
        try:
            deposit = driver.find_element(By.CSS_SELECTOR, value='body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open > div > div.balance-info-block__data > div.balance-info-block__balance > span')
            deposit_value = float(deposit.text.replace(',', ''))
        except:
            return

        try:
            closed_tab = driver.find_element(By.CSS_SELECTOR, value='#bar-chart > div > div > div.right-widget-container > div > div.widget-slot__header > div.divider > ul > li:nth-child(2) > a')
            closed_tab_parent = closed_tab.find_element(By.XPATH, value='..')
            if closed_tab_parent.get_attribute('class') == '':
                closed_tab_parent.click()
        except:
            pass

        await set_amount_icon(driver)

        closed_trades = driver.find_elements(By.CLASS_NAME, value='deals-list__item')
        if closed_trades:
            last_split = closed_trades[0].text.split('\n')
            try:
                amount = driver.find_element(By.CSS_SELECTOR, value='#put-call-buttons-chart-1 > div > div.blocks-wrap > div.block.block--bet-amount > div.block__control.control > div.control__value.value.value--several-items > div > input[type=text]')
                amount_value = int(float((amount.get_attribute('value').replace(',', ''))))

                # Check if win, draw, or loss
                if '$0' != last_split[4] and '$\u202f0' != last_split[4]:  # WIN
                    WINNING_TRADES += 1
                    WIN_STREAK += 1
                    LOSE_STREAK = 0
                    if WIN_STREAK > MAX_WIN_STREAK:
                        globals()['MAX_WIN_STREAK'] = WIN_STREAK

                    # Reset to base amount
                    if amount_value > MARTINGALE_LIST[0]:
                        amount.click()
                        await hand_delay()
                        for number in str(MARTINGALE_LIST[0]):
                            driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                            await hand_delay()

                    win_rate = (WINNING_TRADES / (WINNING_TRADES + LOSING_TRADES)) * 100 if (WINNING_TRADES + LOSING_TRADES) > 0 else 0
                    log(f"WIN! Win rate: {win_rate:.1f}% | Streak: {WIN_STREAK}")

                elif '$0' != last_split[3] and '$\u202f0' != last_split[3]:  # DRAW
                    log("DRAW - maintaining position")

                else:  # LOSS
                    LOSING_TRADES += 1
                    LOSE_STREAK += 1
                    WIN_STREAK = 0
                    if LOSE_STREAK > MAX_LOSE_STREAK:
                        globals()['MAX_LOSE_STREAK'] = LOSE_STREAK

                    amount.click()
                    await asyncio.sleep(random.uniform(0.6, 1.1))

                    # Increase bet according to Martingale
                    if amount_value in MARTINGALE_LIST and MARTINGALE_LIST.index(amount_value) + 1 < len(MARTINGALE_LIST):
                        next_amount = MARTINGALE_LIST[MARTINGALE_LIST.index(amount_value) + 1]

                        # Safety check - don't bet more than 10% of deposit
                        if next_amount > deposit_value * 0.1:
                            log(f'Martingale safety limit - next bet {next_amount} > 10% of deposit')
                            # Reset to base
                            for number in str(MARTINGALE_LIST[0]):
                                driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                                await hand_delay()
                        elif next_amount > deposit_value:
                            log(f'Insufficient funds for Martingale - resetting')
                            for number in str(MARTINGALE_LIST[0]):
                                driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                                await hand_delay()
                        else:
                            for number in str(next_amount):
                                driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                                await hand_delay()
                    else:
                        # Reset to base amount
                        for number in str(MARTINGALE_LIST[0]):
                            driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                            await hand_delay()

                    win_rate = (WINNING_TRADES / (WINNING_TRADES + LOSING_TRADES)) * 100 if (WINNING_TRADES + LOSING_TRADES) > 0 else 0
                    log(f"LOSS! Win rate: {win_rate:.1f}% | Streak: -{LOSE_STREAK}")

                try:
                    closed_tab_parent.click()
                except:
                    pass
            except Exception as e:
                log(f"Error managing Martingale: {e}")

        MARTINGALE_AMOUNT_SET = True


async def check_indicators(driver):
    """Main trading logic loop"""
    global MARTINGALE_LAST_ACTION_ENDS_AT, MARTINGALE_AMOUNT_SET

    # Manage Martingale
    await manage_martingale(driver)

    # Wait if previous action still running
    if SETTINGS.get('MARTINGALE_ENABLED') and MARTINGALE_LAST_ACTION_ENDS_AT + timedelta(seconds=4) > datetime.now():
        return

    # Check each asset
    for asset, candles in CANDLES.items():
        if len(candles) < 50:
            continue

        result = await check_strategies(candles)

        if not result:
            continue

        action, reason = result
        order_created = await create_order(driver, action, asset, reason)

        if order_created:
            if SETTINGS.get('MARTINGALE_ENABLED'):
                await set_estimation_icon(driver)
                seconds = await get_estimation(driver)
                MARTINGALE_LAST_ACTION_ENDS_AT = datetime.now() + timedelta(seconds=seconds)
                MARTINGALE_AMOUNT_SET = False
            await asyncio.sleep(1)
            return


async def check_deposit(driver):
    """Monitor deposit and apply take profit / stop loss"""
    global INITIAL_DEPOSIT, TRADING_ALLOWED

    try:
        deposit = driver.find_element(By.CSS_SELECTOR, value='body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open > div > div.balance-info-block__data > div.balance-info-block__balance > span')
        deposit = float(deposit.text.replace(',', ''))
    except Exception as e:
        return

    if INITIAL_DEPOSIT is None:
        INITIAL_DEPOSIT = deposit
        log(f'Initial deposit: ${INITIAL_DEPOSIT}')
        await asyncio.sleep(1)
        return

    # Take Profit
    if SETTINGS.get('TAKE_PROFIT_ENABLED'):
        profit = deposit - INITIAL_DEPOSIT
        target = SETTINGS.get('TAKE_PROFIT', 100)
        if profit >= target:
            log(f'TAKE PROFIT HIT! Initial: ${INITIAL_DEPOSIT} | Current: ${deposit} | Profit: ${profit}')
            TRADING_ALLOWED = False

    # Stop Loss
    if SETTINGS.get('STOP_LOSS_ENABLED'):
        loss = INITIAL_DEPOSIT - deposit
        max_loss = SETTINGS.get('STOP_LOSS', 50)
        if loss >= max_loss:
            log(f'STOP LOSS HIT! Initial: ${INITIAL_DEPOSIT} | Current: ${deposit} | Loss: ${loss}')
            TRADING_ALLOWED = False


async def wait_for_login(driver):
    """Wait for user to login manually"""
    log("=" * 60)
    log("WAITING FOR YOU TO LOGIN")
    log("=" * 60)
    log("")
    log("👉 A Chrome window has opened")
    log("👉 Please LOGIN to your Pocket Option account")
    log("👉 Choose DEMO or REAL account (top-right)")
    log("👉 Add 2-5 FAVORITE assets (click asset → star icon)")
    log("")
    log("⏳ Bot will detect when you're logged in and start automatically...")
    log("")

    max_wait = 300  # 5 minutes max
    waited = 0

    while waited < max_wait:
        try:
            # Check if logged in by looking for balance element
            balance = driver.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open')

            # Found balance = logged in!
            log("=" * 60)
            log("✓ LOGIN DETECTED!")
            log("=" * 60)
            await asyncio.sleep(2)
            return True

        except:
            # Not logged in yet
            await asyncio.sleep(2)
            waited += 2

            # Show progress every 10 seconds
            if waited % 10 == 0:
                log(f"⏳ Still waiting for login... ({waited}s elapsed)")

    log("❌ Timeout waiting for login (5 minutes)")
    return False


async def check_account_setup(driver):
    """Check if user has set up favorites"""
    log("")
    log("Checking account setup...")

    try:
        # Get current account type
        balance_elem = driver.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div.wrapper__top > header > div.right-block.js-right-block > div.right-block__item.js-drop-down-modal-open')
        balance_text = balance_elem.text

        if 'DEMO' in balance_text or 'Demo' in balance_text:
            log("✓ Using DEMO account")
        elif 'REAL' in balance_text or 'Real' in balance_text:
            log("⚠️  WARNING: Using REAL MONEY account!")
        else:
            log("✓ Account detected")

    except:
        log("Could not detect account type")

    # Check for favorite assets
    try:
        favorites = driver.find_elements(By.CLASS_NAME, 'assets-favorites-item')
        if favorites:
            log(f"✓ Found {len(favorites)} favorite assets")
            log("")
            log("🚀 Ready to trade!")
            log("")
            return True
        else:
            log("⚠️  No favorite assets found")
            log("👉 Please add favorites: Click asset dropdown → star icon")
            await asyncio.sleep(5)
            return await check_account_setup(driver)

    except:
        log("⚠️  Could not check favorites - continuing anyway")
        return True


async def main():
    """Main bot loop with manual login"""
    driver = await get_driver()

    # Navigate to Pocket Option
    log("Opening Pocket Option...")
    driver.get(URL)
    await asyncio.sleep(3)

    # Wait for user to login
    login_success = await wait_for_login(driver)

    if not login_success:
        log("❌ Login timeout - please restart bot and login faster")
        return

    # Check account setup
    await check_account_setup(driver)

    log("=" * 60)
    log("BOT STARTED - LIVE TRADING")
    log("=" * 60)
    log("Analyzing markets...")
    log("")

    while True:
        if not TRADING_ALLOWED:
            log("Trading halted (Take Profit or Stop Loss hit)")
            await asyncio.sleep(5)
            continue

        await websocket_log(driver)
        await check_indicators(driver)
        await check_deposit(driver)
        await asyncio.sleep(0.5)


# ==================== SETTINGS MANAGEMENT ====================

def read_settings():
    """Read settings from file"""
    global SETTINGS

    try:
        with open(SETTINGS_PATH, 'r') as settings_file:
            for line in settings_file.readlines():
                parts = line.replace('\n', '').split(':')
                setting = parts[0]
                setting_type = parts[1]
                split = setting.split('=')
                value = split[1]

                if setting_type == 'bool':
                    value = True if value == 'True' else False
                elif setting_type == 'int':
                    value = int(value)
                elif setting_type == 'str':
                    if split[0] == 'MARTINGALE_LIST':
                        value = cleanup_martingale_list(value)
                    else:
                        value = value
                SETTINGS[split[0]] = value
    except FileNotFoundError:
        log('Settings file not found, using defaults')
        # Set defaults
        SETTINGS = {
            'FAST_MA': 9,
            'SLOW_MA': 21,
            'MIN_PAYOUT': 85,
            'RSI_ENABLED': True,
            'RSI_PERIOD': 14,
            'RSI_UPPER': 70,
            'VICE_VERSA': False,
            'MARTINGALE_ENABLED': False,
            'MARTINGALE_LIST': [1, 2, 4, 8],
            'TAKE_PROFIT_ENABLED': False,
            'TAKE_PROFIT': 100,
            'STOP_LOSS_ENABLED': False,
            'STOP_LOSS': 50,
            'MIN_CONFIDENCE': 4,
            'USE_TREND_FOLLOWING': False,
            'USE_MEAN_REVERSION': False,
        }


def cleanup_martingale_list(value):
    """Validate and clean Martingale list"""
    value = value.replace(' ', '')
    value_list = value.split(',')
    value_list = [int(v) for v in value_list]
    if len(value_list) < 2 or value_list[0] < 1 or value_list[-1] > 20000:
        raise ValueError("Invalid Martingale list")

    martingale_list = []
    for i, v in enumerate(value_list):
        if i == 0:
            martingale_list.append(v)
        elif value_list[i-1] < value_list[i]:
            martingale_list.append(v)
        else:
            raise ValueError("Martingale values must be increasing")

    return martingale_list


def save_settings(**kwargs):
    """Save settings to file"""
    global SETTINGS

    with open(SETTINGS_PATH, 'w') as settings_file:
        for setting, value in kwargs.items():
            if setting == 'MARTINGALE_LIST':
                SETTINGS[setting] = cleanup_martingale_list(value)
            else:
                SETTINGS[setting] = value
            settings_file.write(f"{setting}={value}:{type(value).__name__}\n")


# ==================== GUI INTERFACE ====================

def tkinter_run():
    """Enhanced GUI interface"""
    window = Tk()
    window.geometry('700x350')
    window.title('Pocket Option FREE Enhanced Bot - No Limits!')
    read_settings()

    def enable_rsi():
        for el in [ent_rsi_period, lbl_rsi_period, lbl_rsi_upper, ent_rsi_upper]:
            el.config(state='normal' if chk_rsi_var.get() else 'disabled')

    def enable_take_profit():
        ent_take_profit.config(state='normal' if chk_take_prof.get() else 'disabled')

    def enable_stop_loss():
        ent_stop_loss.config(state='normal' if chk_stop_lo.get() else 'disabled')

    def enable_martingale():
        ent_mar.config(state='normal' if chk_mar.get() else 'disabled')

    # Column 0: Strategy Settings
    Label(window, text='STRATEGY SETTINGS', font='bold').grid(column=0, row=0, sticky=W)

    Label(window, text='Fast EMA:').grid(column=0, row=1, sticky=W)
    ent_fast_ma = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('FAST_MA', 9)))
    ent_fast_ma.grid(column=0, row=1, sticky=E)

    Label(window, text='Slow EMA:').grid(column=0, row=2, sticky=W)
    ent_slow_ma = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('SLOW_MA', 21)))
    ent_slow_ma.grid(column=0, row=2, sticky=E)

    chk_rsi_var = IntVar()
    chk_rsi = Checkbutton(window, text='Use RSI', variable=chk_rsi_var, command=enable_rsi)
    if SETTINGS.get('RSI_ENABLED', True):
        chk_rsi.select()
    chk_rsi.grid(column=0, row=3, sticky=W)

    lbl_rsi_period = Label(window, text='RSI Period:')
    lbl_rsi_period.grid(column=0, row=4, sticky=W)
    ent_rsi_period = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('RSI_PERIOD', 14)))
    ent_rsi_period.grid(column=0, row=4, sticky=E)

    lbl_rsi_upper = Label(window, text='RSI Upper:')
    lbl_rsi_upper.grid(column=0, row=5, sticky=W)
    ent_rsi_upper = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('RSI_UPPER', 70)))
    ent_rsi_upper.grid(column=0, row=5, sticky=E)

    enable_rsi()

    Label(window, text='Min Confidence:').grid(column=0, row=6, sticky=W)
    ent_confidence = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('MIN_CONFIDENCE', 4)))
    ent_confidence.grid(column=0, row=6, sticky=E)

    # Column 1: Divider
    Label(window, text='  ').grid(column=1, row=0)

    # Column 2: Risk Management
    Label(window, text='RISK MANAGEMENT', font='bold').grid(column=2, row=0, sticky=W)

    Label(window, text='Min Payout %:').grid(column=2, row=1, sticky=W)
    ent_min_payout = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('MIN_PAYOUT', 85)))
    ent_min_payout.grid(column=2, row=1, sticky=E)

    chk_take_prof = IntVar()
    chk_take_profit = Checkbutton(window, text='Take Profit $', variable=chk_take_prof, command=enable_take_profit)
    if SETTINGS.get('TAKE_PROFIT_ENABLED', False):
        chk_take_profit.select()
    chk_take_profit.grid(column=2, row=2, sticky=W)
    ent_take_profit = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('TAKE_PROFIT', 100)))
    ent_take_profit.config(state='normal' if chk_take_prof.get() else 'disabled')
    ent_take_profit.grid(column=2, row=2, sticky=E)

    chk_stop_lo = IntVar()
    chk_stop_loss = Checkbutton(window, text='Stop Loss $', variable=chk_stop_lo, command=enable_stop_loss)
    if SETTINGS.get('STOP_LOSS_ENABLED', False):
        chk_stop_loss.select()
    chk_stop_loss.grid(column=2, row=3, sticky=W)
    ent_stop_loss = Entry(window, width=5, textvariable=IntVar(value=SETTINGS.get('STOP_LOSS', 50)))
    ent_stop_loss.config(state='normal' if chk_stop_lo.get() else 'disabled')
    ent_stop_loss.grid(column=2, row=3, sticky=E)

    chk_var = IntVar()
    chk_vice_versa = Checkbutton(window, text='Vice Versa (Invert)', variable=chk_var)
    if SETTINGS.get('VICE_VERSA', False):
        chk_vice_versa.select()
    chk_vice_versa.grid(column=2, row=4, sticky=W)

    # Column 3: Divider
    Label(window, text='  ').grid(column=3, row=0)

    # Column 4: Martingale
    Label(window, text='MARTINGALE (Optional)', font='bold').grid(column=4, row=0, sticky=W)

    chk_mar = IntVar()
    chk_martingale = Checkbutton(window, text='Enable Martingale', variable=chk_mar, command=enable_martingale)
    if SETTINGS.get('MARTINGALE_ENABLED', False):
        chk_martingale.select()
    chk_martingale.grid(column=4, row=1, sticky=W)

    Label(window, text='Bet Sequence:').grid(column=4, row=2, sticky=W)
    mar_value = ', '.join([str(v) for v in SETTINGS.get('MARTINGALE_LIST', [1, 2, 4, 8])])
    ent_mar = Entry(window, width=20, textvariable=StringVar(value=mar_value))
    ent_mar.config(state='normal' if SETTINGS.get('MARTINGALE_ENABLED') else 'disabled')
    ent_mar.grid(column=4, row=3, columnspan=2)

    Label(window, text='(comma-separated, increasing)', font=('Arial', 8)).grid(column=4, row=4, sticky=W)

    # Advanced Options
    Label(window, text='').grid(column=0, row=10)  # Spacer
    Label(window, text='ADVANCED OPTIONS', font='bold').grid(column=0, row=11, sticky=W)

    chk_trend = IntVar()
    chk_trend_following = Checkbutton(window, text='Trend Following', variable=chk_trend)
    if SETTINGS.get('USE_TREND_FOLLOWING', False):
        chk_trend_following.select()
    chk_trend_following.grid(column=0, row=12, sticky=W)

    chk_mean = IntVar()
    chk_mean_reversion = Checkbutton(window, text='Mean Reversion', variable=chk_mean)
    if SETTINGS.get('USE_MEAN_REVERSION', False):
        chk_mean_reversion.select()
    chk_mean_reversion.grid(column=0, row=13, sticky=W)

    error_variable = StringVar()
    lbl_error = Label(window, textvariable=error_variable, fg='#f00')
    lbl_error.grid(column=0, columnspan=5, row=20, sticky=W)

    def run():
        error_variable.set('')

        # Validation
        try:
            fast = int(ent_fast_ma.get())
            slow = int(ent_slow_ma.get())
            if fast < 1 or fast > 99 or slow < 1 or slow > 99:
                error_variable.set('MA values must be 1-99')
                return
            if fast >= slow:
                error_variable.set('Fast MA must be < Slow MA')
                return

            if chk_mar.get():
                cleanup_martingale_list(ent_mar.get())

        except Exception as e:
            error_variable.set(f'Invalid input: {e}')
            return

        save_settings(
            FAST_MA=int(ent_fast_ma.get()),
            SLOW_MA=int(ent_slow_ma.get()),
            MIN_PAYOUT=int(ent_min_payout.get()),
            RSI_ENABLED=bool(chk_rsi_var.get()),
            RSI_PERIOD=int(ent_rsi_period.get()),
            RSI_UPPER=int(ent_rsi_upper.get()),
            VICE_VERSA=bool(chk_var.get()),
            MARTINGALE_ENABLED=bool(chk_mar.get()),
            MARTINGALE_LIST=ent_mar.get() if chk_mar.get() else mar_value,
            TAKE_PROFIT_ENABLED=bool(chk_take_prof.get()),
            TAKE_PROFIT=int(ent_take_profit.get()) if chk_take_prof.get() else 100,
            STOP_LOSS_ENABLED=bool(chk_stop_lo.get()),
            STOP_LOSS=int(ent_stop_loss.get()) if chk_stop_lo.get() else 50,
            MIN_CONFIDENCE=int(ent_confidence.get()),
            USE_TREND_FOLLOWING=bool(chk_trend.get()),
            USE_MEAN_REVERSION=bool(chk_mean.get()),
        )
        window.destroy()

    def on_close():
        window.destroy()
        sys.exit()

    Button(window, text="START TRADING (FREE - NO LIMITS!)", command=run, bg='#00ff00', font='bold').grid(column=0, columnspan=5, row=21, pady=10)

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()


if __name__ == '__main__':
    try:
        tkinter_run()
        read_settings()
        log("=" * 60)
        log("FREE ENHANCED POCKET OPTION BOT - STARTED")
        log("NO LICENSE REQUIRED - NO PAYMENT REQUIRED")
        log("=" * 60)
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Bot stopped by user")
    except Exception as e:
        log(f"Error: {e}")
