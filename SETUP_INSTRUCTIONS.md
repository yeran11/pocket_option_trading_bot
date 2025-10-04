# 🚀 Setup Instructions for Pocket Option Trading Bot

## 📋 Prerequisites

- Python 3.8+
- Chrome browser installed
- OpenAI API key (get from https://platform.openai.com/api-keys)

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yeran11/pocket_option_trading_bot.git
cd pocket_option_trading_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:

```bash
pip install flask selenium undetected-chromedriver openai python-dotenv
```

### 3. Configure API Keys (IMPORTANT!)

**Create a `.env` file** in the project root directory:

```bash
# On Windows (CMD):
copy .env.example .env

# On Mac/Linux:
cp .env.example .env
```

Then edit the `.env` file and add your actual API keys:

```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_PROJECT_ID=proj_your-actual-project-id-here
```

**⚠️ IMPORTANT:**
- The `.env` file is in `.gitignore` and will NOT be pushed to GitHub
- Never commit your API keys to GitHub
- Keep your `.env` file private and secure

### 4. Run the Bot

```bash
python main.py
```

The server will start on `http://localhost:5000`

### 5. Access the Web Interface

Open your browser and go to:
```
http://localhost:5000
```

## 🤖 AI System Configuration

The bot will automatically:
1. ✅ Load API key from `.env` file
2. ✅ Initialize the AI trading system
3. ✅ Enable AI toggle in settings

If you see "❌ Invalid API key", check that:
- Your `.env` file exists in the root directory
- Your API key is valid and active
- You have installed `python-dotenv`: `pip install python-dotenv`

## 📁 Project Structure

```
pocket_option_trading_bot/
├── .env                    # Your API keys (NOT in git)
├── .env.example           # Template for .env
├── ai_config.py           # AI configuration
├── main.py               # Entry point (redirects to subdirectory)
├── pocket_option_trading_bot/
│   ├── main.py           # Main bot logic
│   ├── ai_config.py      # AI configuration (copy)
│   └── templates/        # Web interface
└── SETUP_INSTRUCTIONS.md # This file
```

## 🔑 Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key immediately (you won't see it again)
4. Paste it into your `.env` file

## ❓ Troubleshooting

### "AI initialization failed - Invalid API key"
- Make sure `.env` file exists in root directory
- Check that your API key is correct (starts with `sk-proj-`)
- Verify `python-dotenv` is installed: `pip install python-dotenv`

### "Module not found" errors
- Run: `pip install flask selenium undetected-chromedriver openai python-dotenv`

### Chrome driver issues
- Make sure Chrome browser is installed
- The bot will automatically download the correct ChromeDriver

## 🌐 Using on Replit

If running on Replit:
1. Go to "Secrets" (lock icon in left sidebar)
2. Add these secrets:
   - Key: `OPENAI_API_KEY`, Value: `your-api-key`
   - Key: `OPENAI_PROJECT_ID`, Value: `your-project-id`
3. Run the bot - it will load from Replit Secrets automatically

## 🔒 Security Notes

- ✅ `.env` file is in `.gitignore` - safe from GitHub
- ✅ API keys loaded from environment variables
- ✅ No hardcoded secrets in code
- ⚠️ Never share your `.env` file
- ⚠️ Never commit API keys to git

## 📞 Support

If you encounter issues:
1. Check that `.env` file exists and has correct format
2. Verify all dependencies are installed
3. Make sure Chrome browser is installed
4. Check the console logs for specific error messages
