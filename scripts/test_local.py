#!/usr/bin/env python3
"""
Local testing script for GitHub profile updater
Run this to test the automation locally before deploying.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from update_stats import GitHubStatsUpdater

def test_local_update():
    """Test the update process locally."""
    print("🧪 Testing GitHub Profile Updater locally...")
    print("=" * 50)
    
    # Set test environment
    os.environ['USERNAME'] = 'ZhaoJackson'
    
    # Initialize updater
    updater = GitHubStatsUpdater()
    
    # Test fetching stats
    print("📊 Fetching GitHub statistics...")
    stats = updater.get_github_stats()
    
    print("✅ Stats fetched successfully!")
    print(f"📈 Found {len(stats)} statistical metrics")
    
    # Display some stats
    for key, value in stats.items():
        if key not in ['languages']:  # Skip complex data for display
            print(f"   {key}: {value}")
    
    # Test README update
    print("\n📝 Testing README update...")
    success = updater.update_readme()
    
    if success:
        print("✅ Local test completed successfully!")
        print("🚀 Ready for deployment!")
    else:
        print("❌ Local test failed!")
        return False
    
    return True

if __name__ == "__main__":
    test_local_update()
