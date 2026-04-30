# ═══════════════════════════════════════════════════════════════
# CRYPTO DASHBOARD — Fundamental analysis, market sentiment, multi-chain
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger("nexus.crypto")


class CryptoDashboard:
    """Crypto analytics dashboard backend."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.defillama_base = "https://api.llama.fi"
        logger.info("📈 Crypto Dashboard initialized")

    async def get_market_overview(self) -> dict:
        """Get global crypto market overview."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.coingecko_base}/global")
                data = resp.json().get("data", {})
                return {
                    "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
                    "total_volume_24h_usd": data.get("total_volume", {}).get("usd"),
                    "market_cap_change_24h": data.get("market_cap_change_percentage_24h_usd"),
                    "btc_dominance": data.get("market_cap_percentage", {}).get("btc"),
                    "eth_dominance": data.get("market_cap_percentage", {}).get("eth"),
                    "active_cryptocurrencies": data.get("active_cryptocurrencies"),
                }
        except Exception as e:
            return {"error": str(e)}

    async def get_trending(self) -> list[dict]:
        """Get trending coins."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.coingecko_base}/search/trending")
                coins = resp.json().get("coins", [])
                return [
                    {
                        "name": c["item"]["name"], "symbol": c["item"]["symbol"],
                        "rank": c["item"].get("market_cap_rank"),
                        "price_btc": c["item"].get("price_btc"),
                        "score": c["item"].get("score"),
                    }
                    for c in coins[:10]
                ]
        except Exception as e:
            return [{"error": str(e)}]

    async def get_defi_tvl(self, protocol: str | None = None) -> dict:
        """Get DeFi Total Value Locked from DeFiLlama."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                if protocol:
                    resp = await client.get(f"{self.defillama_base}/protocol/{protocol}")
                    data = resp.json()
                    return {
                        "name": data.get("name"), "symbol": data.get("symbol"),
                        "tvl": data.get("tvl"), "chain_tvls": data.get("chainTvls", {}),
                        "category": data.get("category"),
                    }
                else:
                    resp = await client.get(f"{self.defillama_base}/protocols")
                    protocols = resp.json()[:20]
                    return {
                        "top_protocols": [
                            {"name": p["name"], "tvl": p.get("tvl"), "symbol": p.get("symbol"), "category": p.get("category")}
                            for p in protocols
                        ]
                    }
        except Exception as e:
            return {"error": str(e)}

    async def get_fear_greed_index(self) -> dict:
        """Get Fear & Greed Index."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://api.alternative.me/fng/?limit=7")
                data = resp.json().get("data", [])
                if data:
                    latest = data[0]
                    return {
                        "value": int(latest["value"]),
                        "classification": latest["value_classification"],
                        "timestamp": latest["timestamp"],
                        "history": [{"value": d["value"], "class": d["value_classification"], "date": d["timestamp"]} for d in data],
                    }
        except Exception as e:
            return {"error": str(e)}
        return {}

    async def generate_report(self, coin_id: str) -> str:
        """Generate a formatted crypto analysis report."""
        from packages.blockchain.tracker import BlockchainTracker
        tracker = BlockchainTracker(self.config)
        fa = await tracker.fundamental_analysis(coin_id)
        fgi = await self.get_fear_greed_index()

        report = f"""
╔══════════════════════════════════════╗
║   📈 CRYPTO ANALYSIS: {fa.get('name', coin_id).upper()}
╚══════════════════════════════════════╝

💰 Price: ${fa.get('price_usd', 'N/A')}
📊 Market Cap Rank: #{fa.get('market_cap_rank', 'N/A')}
📈 24h Change: {fa.get('price_change_24h', 0):.2f}%
📈 7d Change: {fa.get('price_change_7d', 0):.2f}%
🏆 ATH: ${fa.get('ath', 'N/A')}
📉 ATL: ${fa.get('atl', 'N/A')}

🔧 GitHub Stars: {fa.get('github_stars', 'N/A')}
🔧 Commits (4w): {fa.get('github_commits_4w', 'N/A')}
🐦 Twitter: {fa.get('twitter_followers', 'N/A')} followers
🔴 Reddit: {fa.get('reddit_subscribers', 'N/A')} subscribers

😱 Fear & Greed: {fgi.get('value', 'N/A')} ({fgi.get('classification', '')})
"""
        return report.strip()
