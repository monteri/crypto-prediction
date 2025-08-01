#!/usr/bin/env python3
"""
Complete bootstrap script for Kafka topics and ksqlDB views
This script ensures all required infrastructure is set up before the application starts
"""
import os
import sys
import time
from bootstrap_topics import main as bootstrap_topics
from bootstrap_ksql import main as bootstrap_ksql

def main():
    print("🌟 Starting complete Kafka and ksqlDB bootstrap...")
    print("=" * 60)
    
    # Step 1: Bootstrap Kafka topics
    print("\n📋 Step 1: Creating Kafka topics...")
    try:
        bootstrap_topics()
        print("✅ Kafka topics bootstrap completed")
    except Exception as e:
        print(f"❌ Failed to bootstrap Kafka topics: {e}")
        return False
    
    # Wait a moment for topics to be fully created
    print("⏳ Waiting for topics to be fully initialized...")
    time.sleep(5)
    
    # Step 2: Bootstrap ksqlDB views
    print("\n📊 Step 2: Creating ksqlDB views...")
    try:
        if bootstrap_ksql():
            print("✅ ksqlDB views bootstrap completed")
        else:
            print("❌ ksqlDB views bootstrap failed")
            return False
    except Exception as e:
        print(f"❌ Failed to bootstrap ksqlDB views: {e}")
        return False
    
    print("\n🎉 Complete bootstrap finished successfully!")
    print("=" * 60)
    print("🚀 Your Kafka ecosystem is ready with:")
    print("   • Kafka topics")
    print("   • ksqlDB streams and tables")
    print("   • Daily and monthly crypto price aggregations")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)