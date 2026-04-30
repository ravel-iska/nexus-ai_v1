# ═══════════════════════════════════════════════════════════════
# BLOCKCHAIN — Multi-chain tracker, wallet monitor, DeFi, portfolio
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import logging, asyncio
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.blockchain")


@dataclass
class WalletInfo:
    address: str
    chain: str
    balance: float
    token_symbol: str
    usd_value: float
    tokens: list[dict] = field(default_factory=list)
    recent_txs: list[dict] = field(default_factory=list)


class BlockchainTracker:
    """Multi-chain blockchain tracker with realtime monitoring."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.alchemy_key = self.config.get("alchemy_api_key", "")
        self.moralis_key = self.config.get("moralis_api_key", "")
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        logger.info("🔗 Blockchain Tracker initialized (multi-chain)")

    async def get_wallet(self, address: str, chain: str = "ethereum") -> WalletInfo:
        """Get wallet balance and recent transactions."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                if chain == "ethereum":
                    rpc_url = f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_key}"
                    resp = await client.post(rpc_url, json={
                        "jsonrpc": "2.0", "method": "eth_getBalance",
                        "params": [address, "latest"], "id": 1,
                    })
                    balance_wei = int(resp.json().get("result", "0x0"), 16)
                    balance_eth = balance_wei / 1e18

                    eth_price = await self._get_price("ethereum")
                    return WalletInfo(
                        address=address, chain=chain, balance=round(balance_eth, 6),
                        token_symbol="ETH", usd_value=round(balance_eth * eth_price, 2),
                    )
                elif chain in ("bsc", "binance"):
                    return WalletInfo(address=address, chain="bsc", balance=0, token_symbol="BNB", usd_value=0)
                elif chain == "solana":
                    return WalletInfo(address=address, chain="solana", balance=0, token_symbol="SOL", usd_value=0)
        except Exception as e:
            logger.error(f"❌ Wallet fetch error: {e}")
            return WalletInfo(address=address, chain=chain, balance=0, token_symbol="?", usd_value=0)

    async def get_portfolio(self, wallets: list[dict]) -> dict:
        """Calculate total portfolio across multiple wallets/chains."""
        total_usd = 0
        assets = []
        for w in wallets:
            info = await self.get_wallet(w["address"], w.get("chain", "ethereum"))
            total_usd += info.usd_value
            assets.append({
                "chain": info.chain, "symbol": info.token_symbol,
                "balance": info.balance, "usd_value": info.usd_value,
            })
        return {"total_value_usd": round(total_usd, 2), "assets": assets, "wallet_count": len(wallets)}

    async def get_market_data(self, coin_ids: list[str]) -> list[dict]:
        """Get market data from CoinGecko."""
        import httpx
        try:
            ids = ",".join(coin_ids)
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.coingecko_base}/coins/markets", params={
                    "vs_currency": "usd", "ids": ids, "order": "market_cap_desc",
                    "sparkline": False, "price_change_percentage": "24h,7d",
                })
                return resp.json()
        except Exception as e:
            return [{"error": str(e)}]

    async def _get_price(self, coin_id: str) -> float:
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.coingecko_base}/simple/price", params={
                    "ids": coin_id, "vs_currencies": "usd",
                })
                return resp.json().get(coin_id, {}).get("usd", 0)
        except Exception:
            return 0

    async def fundamental_analysis(self, coin_id: str) -> dict:
        """Generate fundamental analysis for a cryptocurrency."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.coingecko_base}/coins/{coin_id}", params={
                    "localization": False, "tickers": False, "community_data": True,
                    "developer_data": True, "sparkline": False,
                })
                data = resp.json()
                market = data.get("market_data", {})
                dev = data.get("developer_data", {})
                community = data.get("community_data", {})

                return {
                    "name": data.get("name"), "symbol": data.get("symbol"),
                    "market_cap_rank": data.get("market_cap_rank"),
                    "price_usd": market.get("current_price", {}).get("usd"),
                    "market_cap": market.get("market_cap", {}).get("usd"),
                    "volume_24h": market.get("total_volume", {}).get("usd"),
                    "price_change_24h": market.get("price_change_percentage_24h"),
                    "price_change_7d": market.get("price_change_percentage_7d"),
                    "ath": market.get("ath", {}).get("usd"),
                    "atl": market.get("atl", {}).get("usd"),
                    "github_stars": dev.get("stars"),
                    "github_forks": dev.get("forks"),
                    "github_commits_4w": dev.get("commit_count_4_weeks"),
                    "twitter_followers": community.get("twitter_followers"),
                    "reddit_subscribers": community.get("reddit_subscribers"),
                    "description": data.get("description", {}).get("en", "")[:500],
                }
        except Exception as e:
            return {"error": str(e)}
