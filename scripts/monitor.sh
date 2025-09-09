#!/bin/bash
# GC Estimator Monitoring Script

echo "🚀 GC Estimator - Application Status"
echo "=================================="

# Check application status
echo "📊 Frontend Status:"
flyctl status -a frontend-green-flower-3817 | grep -E "(State|REGION|STATE)"
echo ""

echo "🔧 Backend API Status:"
flyctl status -a api-dark-flower-4953 | grep -E "(State|REGION|STATE)"
echo ""

# Test connectivity and response times
echo "🌐 Connectivity Tests:"
echo -n "Frontend: "
curl -w "HTTP %{http_code} - %{time_total}s" -s -o /dev/null https://frontend-green-flower-3817.fly.dev/
echo ""

echo -n "Backend API: "
curl -w "HTTP %{http_code} - %{time_total}s" -s -o /dev/null https://api-dark-flower-4953.fly.dev/health
echo ""

echo -n "API Integration: "
curl -w "HTTP %{http_code} - %{time_total}s" -s -o /dev/null https://frontend-green-flower-3817.fly.dev/api/estimates
echo ""

# Show recent logs if there are any errors
echo "📝 Recent Logs (last 5 lines):"
echo "Frontend:"
flyctl logs -a frontend-green-flower-3817 --lines 5 | tail -5
echo ""
echo "Backend:"
flyctl logs -a api-dark-flower-4953 --lines 5 | tail -5

echo ""
echo "✅ Monitoring complete!"
echo "💡 For detailed logs: flyctl logs -a <app-name>"
echo "💰 For scaling: flyctl scale memory <size> -a <app-name>"
