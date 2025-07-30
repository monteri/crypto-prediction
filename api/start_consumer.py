#!/usr/bin/env python3
"""
Script to start the Kafka consumer for crypto price messages
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from consumers.crypto_consumer import main

if __name__ == '__main__':
    print("🚀 Starting Crypto Price Consumer...")
    main() 