#!/bin/bash
# Setup script for 99_AI-lab

echo "🚀 Setting up 99_AI-lab"
echo "========================"

echo ""
echo "Step 1: Installing dependencies..."
pip install anthropic python-dotenv
echo "✅ Dependencies installed"

echo ""
echo "Step 2: Replace API Key"
echo "========================"
echo ""
echo "1. Get your API key from: https://console.anthropic.com/account/keys"
echo "2. Run this command with YOUR_API_KEY:"
echo ""
echo "   sed -i '' 's/sk-ant-v4-YOUR-API-KEY-HERE/YOUR_API_KEY/g' *.py"
echo ""
echo "   Example:"
echo "   sed -i '' 's/sk-ant-v4-YOUR-API-KEY-HERE/sk-ant-v4-abc123xyz/g' *.py"
echo ""

echo "Step 3: Test installation"
echo "========================"
echo "Run: python 01_basic_llm.py"
echo ""
echo "✅ Setup complete! Replace API key and run examples."
