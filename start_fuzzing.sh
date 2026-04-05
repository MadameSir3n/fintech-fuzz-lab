#!/bin/bash
# FinTech Fuzz Lab - Startup Script

echo "🚀 Starting FinTech Fuzz Lab..."
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🐳 Building and starting Docker containers..."
docker-compose up --build -d

echo "⏳ Waiting for API to start..."
sleep 10

echo "🧪 Running health check..."
curl -f http://localhost:8000/health || {
    echo "❌ API health check failed"
    docker-compose logs fintech-fuzz-api
    exit 1
}

echo "✅ API is healthy!"
echo ""
echo "🎯 Starting fuzz tests..."
echo "================================"

# Run the fuzzer
python -m src.fuzzer --url http://localhost:8000 --verbose

FUZZ_RESULT=$?

echo ""
echo "================================"
echo "🧪 Fuzz testing completed!"

if [ $FUZZ_RESULT -eq 0 ]; then
    echo "✅ No crashes detected - API handled all test cases"
else
    echo "⚠️  Crashes detected - check artifacts/ directory for details"
    echo "   Saved artifacts: $(ls -1 artifacts/ | wc -l) files"
fi

echo ""
echo "📊 API is running at: http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo "📁 Artifacts directory: ./artifacts/"
echo ""
echo "To stop the application:"
echo "  docker-compose down"
echo ""

exit $FUZZ_RESULT