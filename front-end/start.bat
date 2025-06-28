@echo off

echo 🎯 Rebecca API Dashboard - Quick Start
echo ======================================

REM Check if package.json exists
if not exist "package.json" (
    echo ❌ Error: Not in the front-end directory. Please run this from \front-end\
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    call npm install
)

echo.
echo 🚀 Starting development server...
echo    Frontend: http://localhost:5173
echo    Backend should be running on: http://localhost:8000
echo.
echo 💡 Pro tips:
echo    • Press Ctrl+C to stop the server
echo    • Use 'npm run build' to create production build
echo    • Use 'npm run preview' to test production build
echo    • Use VS Code tasks (Ctrl+Shift+P → 'Tasks: Run Task')
echo.

REM Start the dev server
call npm run dev

pause
