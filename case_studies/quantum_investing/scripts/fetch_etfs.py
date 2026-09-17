#!/usr/bin/env python3
"""Fetch quantum computing focused ETFs using the ETF finder toolbox.

This script demonstrates integration with the toolboxes/scrapers module
to discover ETFs that track quantum computing companies.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "toolboxes" / "src"))

from toolboxes.scrapers import ETFFinderToolbox


async def main():
    """Fetch and display quantum computing ETFs."""
    print("🔬 Quantum Computing ETF Finder")
    print("=" * 50)
    print()

    toolbox = ETFFinderToolbox()

    # Search for quantum computing ETFs
    query = {
        "theme": "quantum computing",
        "focus": "quantum_specific",
        "min_aum": 0,
    }

    print(f"📊 Searching for ETFs: {query['theme']}")
    print()

    result = await toolbox.execute(query)

    if result.success:
        print(f"✓ Found {result.metadata.get('count', 0)} ETFs")
        print()

        if result.data:
            for etf in result.data:
                print(f"  {etf['ticker']:<10} | {etf['name']:<40}")
                if etf.get("price_usd"):
                    print(f"             Price: ${etf['price_usd']:.2f}")
                if etf.get("aum_millions"):
                    print(f"             AUM: ${etf['aum_millions']:.1f}M")
                print(f"             Focus: {etf['focus']}")
                print()
    else:
        print(f"✗ Error: {result.error}")
        print(f"  Metadata: {result.metadata}")

    print()
    print(f"Data source: {result.data[0].get('data_source') if result.data else 'N/A'}")
    print(f"yfinance available: {result.metadata.get('yfinance_available')}")


if __name__ == "__main__":
    asyncio.run(main())
