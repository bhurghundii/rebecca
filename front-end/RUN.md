# 🚀 Quick Run Guide

## Instant Start (Choose One)

### Option 1: Quick Scripts
```bash
# Mac/Linux
./start.sh

# Windows
start.bat
```

### Option 2: NPM Commands
```bash
# Development server
npm run dev

# Development server (accessible from network)
npm run dev:host

# Just start (alias for dev)
npm start
```

### Option 3: VS Code Tasks
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
2. Type "Tasks: Run Task"
3. Select "🚀 Start Development Server"

### Option 4: VS Code Debug
1. Press `F5` or go to Run & Debug panel
2. Select "🌐 Launch Chrome"
3. It will start the dev server AND open Chrome with debugging

## 📋 Available NPM Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (localhost only) |
| `npm run dev:host` | Start dev server (accessible from network) |
| `npm start` | Alias for `npm run dev` |
| `npm run build` | Build for production |
| `npm run build:prod` | Build with production optimizations |
| `npm run preview` | Preview production build locally |
| `npm run preview:host` | Preview production build (network accessible) |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Run ESLint and fix issues |
| `npm run docker:build` | Build Docker image |
| `npm run docker:run` | Run Docker container |
| `npm run clean` | Clean build artifacts |
| `npm run fresh` | Clean, reinstall, and start dev server |

## 🏃‍♂️ One-Line Starters

```bash
# Start development
npm run dev

# Fresh start (if something's broken)
npm run fresh

# Production build and preview
npm run build && npm run preview

# Docker deployment
npm run docker:build && npm run docker:run
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173

# Or use different port
npm run dev -- --port 3000
```

### Clean Start
```bash
npm run fresh
```

### VS Code Tasks Not Working
1. Make sure you're in the `/front-end` directory
2. Reload VS Code window: `Cmd+R` (Mac) or `Ctrl+R` (Windows)

## 🐳 Docker Quick Commands

```bash
# Build and run in one go
docker build -t rebecca-ui . && docker run -p 3000:80 rebecca-ui

# Or use npm scripts
npm run docker:build && npm run docker:run
```

## 🌐 Accessing the App

- **Development**: http://localhost:5173
- **Production Preview**: http://localhost:4173
- **Docker**: http://localhost:3000

## 🎯 Pro Tips

1. **Use VS Code tasks** - They're configured with nice output and problem matchers
2. **Use the debug config** - Press F5 to start dev server + debugging in Chrome
3. **Keep backend running** - Make sure your Rebecca API is running on port 8000
4. **Network access** - Use `--host` variants to access from other devices on your network

That's it! Pick your favorite method and you're ready to go! 🚀
