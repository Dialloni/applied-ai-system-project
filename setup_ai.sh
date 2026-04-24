#!/bin/bash
# Quick setup script for AI-Enhanced Music Recommender

echo "🎵 Setting up AI-Enhanced Music Recommender System..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set up environment variables (optional)
echo ""
echo "🔑 LLM API Setup (Optional)"
echo "For enhanced AI explanations, set environment variables:"
echo ""
echo "  Option 1: Anthropic Claude"
echo "    export ANTHROPIC_API_KEY='your-key-here'"
echo ""
echo "  Option 2: OpenAI GPT"
echo "    export OPENAI_API_KEY='your-key-here'"
echo ""
echo "⚠️  If not set, system will use rule-based explanations."
echo ""

# Run demo
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the AI demo, use:"
echo "   python -m src.ai_demo"
echo ""
echo "🧪 To run tests:"
echo "   pytest tests/"
echo ""
