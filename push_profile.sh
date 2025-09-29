#!/bin/bash

echo "🚀 Pushing GitHub Profile Repository"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Not in profile repository directory"
    echo "Please run this from /Users/jacksonzhao/Desktop/ZhaoJackson-profile"
    exit 1
fi

echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Success! Your profile is now live!"
    echo "🌐 Check it out at: https://github.com/ZhaoJackson"
    echo ""
    echo "🔧 Don't forget to enable GitHub Actions:"
    echo "   1. Go to: https://github.com/ZhaoJackson/ZhaoJackson/settings/actions"
    echo "   2. Select 'Allow all actions and reusable workflows'"
    echo "   3. Select 'Read and write permissions'"
else
    echo "❌ Push failed!"
    echo "Make sure you created the repository 'ZhaoJackson' on GitHub first:"
    echo "👉 https://github.com/new"
fi
