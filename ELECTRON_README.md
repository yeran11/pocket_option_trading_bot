# Trading Bot Pro - Desktop Application

## 🚀 Overview
Trading Bot Pro is a professional desktop application for automated trading on Pocket Option. It features a modern UI with embedded terminal, auto-updates via GitHub, and both demo and live trading modes.

## ✨ Features
- **Professional Desktop UI** - Native application with custom title bar and system tray
- **Demo & Live Modes** - Practice with virtual money or trade with real funds
- **Embedded Terminal** - View bot logs in real-time without opening command prompt
- **Auto-Updates** - Automatic updates from GitHub releases
- **Web Interface Integration** - Access full web UI within the desktop app
- **System Tray** - Minimize to tray and control bot from there
- **Cross-Platform** - Works on Windows, Mac, and Linux (Windows primary)

## 📦 Installation for Development

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### Setup Steps

1. **Install Node Dependencies**
```bash
npm install
```

2. **Replace Icon Files**
- Replace `electron-ui/assets/icon.png` with your 256x256 PNG icon
- Replace `electron-ui/assets/icon.ico` with your Windows ICO file
- Replace `electron-ui/assets/tray-icon.png` with your 16x16 or 24x24 tray icon

3. **Test the Application**
```bash
npm start
```

## 🏗️ Building for Distribution

### Build for Windows
```bash
npm run dist
```
This creates an installer in the `dist` folder.

### Configuration
Edit `package.json` to set your GitHub repository for auto-updates:
```json
"publish": {
    "provider": "github",
    "owner": "YOUR_GITHUB_USERNAME",
    "repo": "YOUR_REPO_NAME"
}
```

## 🎯 User Experience

### First Launch
1. User downloads and installs the application
2. On first launch, sees mode selector:
   - **Demo Trading** - Practice with $10,000 virtual money
   - **Live Trading** - Trade with real money
3. If no credentials exist, setup wizard appears
4. User enters Pocket Option credentials
5. Application creates `.env` file automatically
6. Bot is ready to start

### Daily Usage
1. Launch application
2. Select trading mode (Demo/Live)
3. Click "Start Bot" to begin trading
4. View logs in embedded terminal
5. Access web interface for strategy configuration
6. Minimize to system tray when not needed

## 🔄 Auto-Update System

### For Developers (You)
1. Make bug fixes or improvements
2. Update version in `package.json`
3. Commit and push to GitHub
4. Create a new release on GitHub:
```bash
git tag v1.0.1
git push origin v1.0.1
```
5. Build and upload the installer to the release

### For Users
- Application checks for updates on startup
- Shows notification when update available
- One-click update installation
- Preserves user settings and strategies

## 🛡️ Security Features

### Credential Management
- Credentials stored locally in `.env`
- Never transmitted to servers
- Each user has their own credentials
- Encrypted storage (optional enhancement)

### Trading Modes
- **Demo Mode**: Green indicators, virtual money only
- **Live Mode**: Red warnings, requires confirmation
- Clear visual distinction between modes

## 📁 Project Structure
```
trading-bot-pro/
├── electron-main.js         # Main Electron process
├── electron-preload.js      # Preload script for security
├── electron-ui/             # Desktop UI files
│   ├── splash.html         # Mode selector screen
│   ├── main-window.html    # Main application window
│   └── assets/            # Icons and images
├── pocket_option_trading_bot/  # Python backend
│   ├── main.py            # Flask server & bot logic
│   ├── templates/         # Web UI templates
│   └── ...               # Other bot files
├── package.json           # Electron configuration
└── dist/                 # Built installers (after build)
```

## 🔧 Troubleshooting

### Bot Won't Start
- Check Python is installed: `python --version`
- Verify `.env` file exists in `pocket_option_trading_bot/`
- Check terminal output for errors

### Can't See Web Interface
- Ensure Flask is running (check terminal)
- Try opening http://localhost:5000 in browser
- Check firewall isn't blocking port 5000

### Updates Not Working
- Ensure GitHub repository is public
- Check internet connection
- Verify `package.json` has correct GitHub details

## 🎨 Customization

### Modify UI Theme
Edit colors in `electron-ui/main-window.html`:
```css
/* Change gradient colors */
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

### Change Port
If port 5000 is in use, modify in both:
- `pocket_option_trading_bot/main.py`: `app.run(port=YOUR_PORT)`
- `electron-ui/main-window.html`: Update iframe src

### Add Features
- Edit `electron-main.js` for desktop features
- Modify `main.py` for bot functionality
- Update UI in `electron-ui/` files

## 📝 Release Checklist

Before distributing to users:

1. ✅ Test on clean system
2. ✅ Verify auto-updater works
3. ✅ Check demo mode safety
4. ✅ Test credential setup wizard
5. ✅ Ensure Python backend starts
6. ✅ Verify terminal output displays
7. ✅ Test system tray functionality
8. ✅ Check all buttons work
9. ✅ Test on target OS versions
10. ✅ Create GitHub release with installer

## 💡 Tips for Distribution

### For Users
1. Download the installer from releases
2. Run installer (may need to allow in Windows Defender)
3. Launch application from desktop shortcut
4. Follow setup wizard on first launch
5. Updates install automatically

### Version Management
- Use semantic versioning: `major.minor.patch`
- Increment patch for bug fixes (1.0.1)
- Increment minor for features (1.1.0)
- Increment major for breaking changes (2.0.0)

## ⚠️ Important Notes

1. **Do NOT commit `.env` files** to GitHub
2. **Test thoroughly** before releasing updates
3. **Keep backups** of working versions
4. **Document** any manual steps needed
5. **Users' credentials** stay on their machines

## 📞 Support

For users needing help:
1. Check terminal output for errors
2. Try demo mode first
3. Verify credentials are correct
4. Restart the application
5. Check for updates

---

## 🎯 Quick Start Commands

```bash
# Development
npm start              # Run in development

# Building
npm run dist          # Build Windows installer

# Git Release
git add .
git commit -m "Fix: [description]"
git push
git tag v1.0.X
git push origin v1.0.X
# Then create release on GitHub and upload installer
```

## ✅ Current Status

- ✅ Electron wrapper created
- ✅ Professional UI implemented
- ✅ Mode selector (Demo/Live)
- ✅ Auto-updater configured
- ✅ Embedded terminal working
- ✅ Flask integration ready
- ✅ Credential setup wizard
- ✅ System tray support
- ⏳ Icons need replacement
- ⏳ GitHub repository setup needed

---

**Note**: This application maintains full compatibility with your existing Flask backend. All trading strategies and configurations work exactly as before, now with a professional desktop interface!