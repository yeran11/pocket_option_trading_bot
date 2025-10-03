"""
GUI Preview Test - See the bot interface without connecting
Run this to preview the settings interface
"""
from tkinter import *
from tkinter import messagebox

def preview_gui():
    """Show the bot GUI interface"""
    window = Tk()
    window.geometry('700x400')
    window.title('🚀 FREE Pocket Option Bot - Settings Preview')
    window.configure(bg='#f0f0f0')

    # Header
    header = Label(window, text='POCKET OPTION FREE BOT - SETTINGS INTERFACE',
                   font=('Arial', 14, 'bold'), bg='#4CAF50', fg='white', pady=10)
    header.grid(column=0, row=0, columnspan=6, sticky='ew')

    # Column 0: Strategy Settings
    Label(window, text='STRATEGY SETTINGS', font=('Arial', 10, 'bold'), bg='#f0f0f0').grid(column=0, row=1, sticky=W, padx=10, pady=5)

    Label(window, text='Fast EMA:', bg='#f0f0f0').grid(column=0, row=2, sticky=W, padx=10)
    ent_fast_ma = Entry(window, width=5)
    ent_fast_ma.insert(0, '9')
    ent_fast_ma.grid(column=0, row=2, sticky=E, padx=10)

    Label(window, text='Slow EMA:', bg='#f0f0f0').grid(column=0, row=3, sticky=W, padx=10)
    ent_slow_ma = Entry(window, width=5)
    ent_slow_ma.insert(0, '21')
    ent_slow_ma.grid(column=0, row=3, sticky=E, padx=10)

    chk_rsi_var = IntVar(value=1)
    chk_rsi = Checkbutton(window, text='Use RSI', variable=chk_rsi_var, bg='#f0f0f0')
    chk_rsi.grid(column=0, row=4, sticky=W, padx=10)

    Label(window, text='RSI Period:', bg='#f0f0f0').grid(column=0, row=5, sticky=W, padx=10)
    ent_rsi_period = Entry(window, width=5)
    ent_rsi_period.insert(0, '14')
    ent_rsi_period.grid(column=0, row=5, sticky=E, padx=10)

    Label(window, text='RSI Upper:', bg='#f0f0f0').grid(column=0, row=6, sticky=W, padx=10)
    ent_rsi_upper = Entry(window, width=5)
    ent_rsi_upper.insert(0, '70')
    ent_rsi_upper.grid(column=0, row=6, sticky=E, padx=10)

    Label(window, text='Min Confidence:', bg='#f0f0f0').grid(column=0, row=7, sticky=W, padx=10)
    ent_confidence = Entry(window, width=5)
    ent_confidence.insert(0, '4')
    ent_confidence.grid(column=0, row=7, sticky=E, padx=10)

    # Column 1: Divider
    Label(window, text='  ', bg='#f0f0f0').grid(column=1, row=0)

    # Column 2: Risk Management
    Label(window, text='RISK MANAGEMENT', font=('Arial', 10, 'bold'), bg='#f0f0f0').grid(column=2, row=1, sticky=W, padx=10, pady=5)

    Label(window, text='Min Payout %:', bg='#f0f0f0').grid(column=2, row=2, sticky=W, padx=10)
    ent_min_payout = Entry(window, width=5)
    ent_min_payout.insert(0, '85')
    ent_min_payout.grid(column=2, row=2, sticky=E, padx=10)

    chk_take_prof = IntVar(value=1)
    chk_take_profit = Checkbutton(window, text='Take Profit $', variable=chk_take_prof, bg='#f0f0f0')
    chk_take_profit.grid(column=2, row=3, sticky=W, padx=10)
    ent_take_profit = Entry(window, width=5)
    ent_take_profit.insert(0, '100')
    ent_take_profit.grid(column=2, row=3, sticky=E, padx=10)

    chk_stop_lo = IntVar(value=1)
    chk_stop_loss = Checkbutton(window, text='Stop Loss $', variable=chk_stop_lo, bg='#f0f0f0')
    chk_stop_loss.grid(column=2, row=4, sticky=W, padx=10)
    ent_stop_loss = Entry(window, width=5)
    ent_stop_loss.insert(0, '50')
    ent_stop_loss.grid(column=2, row=4, sticky=E, padx=10)

    chk_var = IntVar()
    chk_vice_versa = Checkbutton(window, text='Vice Versa (Invert)', variable=chk_var, bg='#f0f0f0')
    chk_vice_versa.grid(column=2, row=5, sticky=W, padx=10)

    # Column 3: Divider
    Label(window, text='  ', bg='#f0f0f0').grid(column=3, row=0)

    # Column 4: Martingale
    Label(window, text='MARTINGALE', font=('Arial', 10, 'bold'), bg='#f0f0f0').grid(column=4, row=1, sticky=W, padx=10, pady=5)

    chk_mar = IntVar()
    chk_martingale = Checkbutton(window, text='Enable Martingale', variable=chk_mar, bg='#f0f0f0')
    chk_martingale.grid(column=4, row=2, sticky=W, padx=10)

    Label(window, text='Bet Sequence:', bg='#f0f0f0').grid(column=4, row=3, sticky=W, padx=10)
    ent_mar = Entry(window, width=15)
    ent_mar.insert(0, '1, 2, 4, 8')
    ent_mar.grid(column=4, row=4, padx=10)

    Label(window, text='(comma-separated)', font=('Arial', 8), bg='#f0f0f0').grid(column=4, row=5, sticky=W, padx=10)

    # Info box
    info_frame = Frame(window, bg='#e3f2fd', relief='solid', borderwidth=1)
    info_frame.grid(column=0, row=10, columnspan=6, sticky='ew', padx=10, pady=10)

    info_text = """
    ℹ️  THIS IS A PREVIEW - Settings shown above will appear when you run the actual bot

    • Fast/Slow EMA: Moving averages for trend detection (lower = more sensitive)
    • RSI: Detects overbought (>70) and oversold (<30) conditions
    • Min Confidence: Higher = fewer but stronger signal trades (4-6 recommended)
    • Take Profit/Stop Loss: Auto-stops trading when target reached
    • Martingale: Increases bet after losses (RISKY - use with caution!)
    """

    Label(info_frame, text=info_text, justify=LEFT, bg='#e3f2fd',
          font=('Arial', 9)).pack(padx=10, pady=10)

    # Buttons
    def show_info():
        messagebox.showinfo(
            "How It Works",
            "WHEN YOU RUN THE ACTUAL BOT:\n\n"
            "1. This GUI will appear\n"
            "2. Configure your settings\n"
            "3. Click 'START TRADING'\n"
            "4. Chrome browser will open automatically\n"
            "5. Navigate to Pocket Option and login\n"
            "6. Bot will start analyzing and trading\n\n"
            "⚠️ ALWAYS start with DEMO account first!"
        )

    def close_preview():
        messagebox.showinfo("Next Steps",
                           "To run the REAL bot:\n\n"
                           "python3 po_bot_free.py\n\n"
                           "First, make sure:\n"
                           "✓ Chrome is installed\n"
                           "✓ You have a Pocket Option account\n"
                           "✓ You understand the risks")
        window.destroy()

    btn_frame = Frame(window, bg='#f0f0f0')
    btn_frame.grid(column=0, row=11, columnspan=6, pady=10)

    Button(btn_frame, text="ℹ️ How It Works", command=show_info,
           bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side=LEFT, padx=5)

    Button(btn_frame, text="▶️ START TRADING (Preview Only)", command=close_preview,
           bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side=LEFT, padx=5)

    Button(btn_frame, text="❌ Close Preview", command=window.destroy,
           bg='#f44336', fg='white', font=('Arial', 10), padx=20).pack(side=LEFT, padx=5)

    window.mainloop()

if __name__ == '__main__':
    print("=" * 60)
    print("GUI PREVIEW - This shows what the bot interface looks like")
    print("=" * 60)
    print("\nOpening preview window...")
    preview_gui()
    print("\nPreview closed.")
