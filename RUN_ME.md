# ▶️ HOW TO RUN THE BOT

## 🎯 Super Simple - Just Click RUN!

### **Method 1: Press the RUN Button (Easiest!)**

At the top of this page, you should see a **green RUN button** ▶️

**Just click it!**

That's it! The bot will:
1. ✅ Open a GUI for settings
2. ✅ Launch Chrome browser
3. ✅ Wait for you to login
4. ✅ Start trading automatically!

---

## 🔧 Alternative Methods

### **Method 2: Run Directly**

```bash
python3 main.py
```

### **Method 3: Run the Bot File**

```bash
python3 po_bot_free.py
```

### **Method 4: Test First**

```bash
# Preview the GUI
python3 test_gui_preview.py

# Test Chrome connection
python3 test_browser_connection.py

# Then run the real bot
python3 main.py
```

---

## 📋 What Happens When You Click RUN

```
STEP 1: Run button pressed ▶️
   ↓
STEP 2: GUI window opens
   📊 Configure your settings:
   - Fast EMA: 9 (default)
   - Slow EMA: 21 (default)
   - RSI: Enabled
   - Min Confidence: 4
   - Take Profit: $100
   - Stop Loss: $50
   ↓
STEP 3: Click "START TRADING"
   ↓
STEP 4: Chrome browser opens automatically
   🌐 Navigates to Pocket Option
   ↓
STEP 5: You see login screen
   👤 Enter your email
   🔑 Enter your password
   ✅ Click LOGIN
   ↓
STEP 6: Bot detects login
   Terminal shows: "✓ LOGIN DETECTED!"
   ↓
STEP 7: Bot checks setup
   ✓ Using DEMO account
   ✓ Found 5 favorite assets
   🚀 Ready to trade!
   ↓
STEP 8: Bot starts trading
   📈 CALL on EUR/USD - Confidence: 75%
   📊 Analyzing with 7+ indicators
   🎯 Clicking trades automatically
   📉 Tracking win rate
   💰 Updating balance
```

---

## 🎬 First Time Setup (Do Once)

**When Chrome opens and you login:**

1. **Switch to DEMO** (top-right corner)
   ```
   Click: 💰 Balance → Select DEMO
   ```

2. **Add Favorite Assets** (click asset dropdown)
   ```
   Click: EUR/USD ▼
   Then: Click ⭐ star on 3-5 assets:
   - EUR/USD (92%)
   - GBP/USD (91%)
   - Bitcoin (92%)
   - Gold (89%)
   - USD/JPY (90%)
   ```

3. **Done!** Bot starts automatically

---

## ⚡ Every Time After (Super Fast)

1. Click **RUN** ▶️
2. Click **START TRADING**
3. Bot starts! (Already logged in!)

**Chrome remembers your session - no re-login needed!** 🎉

---

## 📺 What You'll See in Terminal

```
============================================================
🚀 POCKET OPTION FREE TRADING BOT
============================================================

Starting bot...

2025-10-03 12:00:00 Opening Pocket Option...
2025-10-03 12:00:03 ============================================================
2025-10-03 12:00:03 WAITING FOR YOU TO LOGIN
2025-10-03 12:00:03 ============================================================
2025-10-03 12:00:03
2025-10-03 12:00:03 👉 A Chrome window has opened
2025-10-03 12:00:03 👉 Please LOGIN to your Pocket Option account
2025-10-03 12:00:03 👉 Choose DEMO or REAL account (top-right)
2025-10-03 12:00:03 👉 Add 2-5 FAVORITE assets (click asset → star icon)
2025-10-03 12:00:03
2025-10-03 12:00:03 ⏳ Bot will detect when you're logged in and start automatically...

[You login in Chrome...]

2025-10-03 12:00:45 ============================================================
2025-10-03 12:00:45 ✓ LOGIN DETECTED!
2025-10-03 12:00:45 ============================================================
2025-10-03 12:00:47 Checking account setup...
2025-10-03 12:00:47 ✓ Using DEMO account
2025-10-03 12:00:47 ✓ Found 5 favorite assets
2025-10-03 12:00:47
2025-10-03 12:00:47 🚀 Ready to trade!
2025-10-03 12:00:47
2025-10-03 12:00:48 ============================================================
2025-10-03 12:00:48 BOT STARTED - LIVE TRADING
2025-10-03 12:00:48 ============================================================
2025-10-03 12:00:48 Analyzing markets...
2025-10-03 12:01:00 Initial deposit: $10000.0

2025-10-03 12:02:15 CALL on EUR/USD_otc - Confidence: 75.0% (6 signals) | Total trades: 1
2025-10-03 12:03:30 WIN! Win rate: 100.0% | Streak: 1

2025-10-03 12:05:00 PUT on GBP/USD_otc - Confidence: 66.7% (4 signals) | Total trades: 2
2025-10-03 12:06:15 WIN! Win rate: 100.0% | Streak: 2

2025-10-03 12:08:30 Skipping trade - High volatility: 5.23%
                    👆 Safety feature - protecting your money!

2025-10-03 12:10:00 CALL on Bitcoin_otc - Confidence: 80.0% (8 signals) | Total trades: 3
2025-10-03 12:11:15 WIN! Win rate: 100.0% | Streak: 3
```

---

## 🛑 How to Stop

**Option 1: Press Ctrl+C** in terminal

**Option 2: Close Chrome** browser window

**Option 3: Click Stop** button (if available)

Settings are automatically saved! ✅

---

## ⚠️ Important Reminders

✅ **Always start with DEMO account**
✅ **Add 3-5 favorite assets** before bot starts
✅ **Monitor first hour** to see how it trades
✅ **Set Take Profit & Stop Loss** for safety
✅ **Check win rate** - aim for 60%+

---

## 🎯 Quick Troubleshooting

**Nothing happens when I click RUN:**
- Try: `python3 main.py` in terminal

**Chrome doesn't open:**
- Install Chrome: `sudo apt install google-chrome-stable`

**Bot says "No favorites found":**
- Click asset dropdown in Chrome
- Click ⭐ star next to 3-5 assets

**Login timeout:**
- Login within 5 minutes
- Or restart bot

---

## 🚀 YOU'RE READY!

**Just click the RUN button ▶️ at the top!**

The bot will guide you through everything else! 😊

---

*Need detailed help? Check:*
- `QUICK_START.md` - Visual walkthrough
- `SETUP_GUIDE.md` - Complete manual
- `README_FREE_BOT.md` - Features & strategies
