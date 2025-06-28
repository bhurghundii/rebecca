#!/bin/bash

# 🚀 Rebecca UI Quick Start Script

echo "🎯 Rebecca API Dashboard - Quick Start"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Not in the front-end directory. Please run this from /front-end/"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🚀 Starting development server..."
echo "   Frontend: http://localhost:5173"
echo "   Backend should be running on: http://localhost:8000"
echo ""
echo "💡 Pro tips:"
echo "   • Press Ctrl+C to stop the server"
echo "   • Use 'npm run build' to create production build"
echo "   • Use 'npm run preview' to test production build"
echo "   • Use VS Code tasks (Cmd+Shift+P → 'Tasks: Run Task')"
echo ""

# Start the dev server
npm run dev
