# ═══════════════════════════════════════════════════════════════
# TASK CLASSIFIER — Route tasks to the optimal agent/tool
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import re
import logging
from enum import Enum
from typing import Any

logger = logging.getLogger("nexus.classifier")


class TaskType(Enum):
    GENERAL = "general"
    CONVERSATION = "conversation"
    COMPLEX_REASONING = "complex_reasoning"
    CODE_GENERATION = "code_generation"
    BROWSER_SEARCH = "browser_search"
    OSINT_SCAN = "osint_scan"
    BLOCKCHAIN_CHECK = "blockchain_check"
    FILE_DOWNLOAD = "file_download"
    MEDIA_EDIT = "media_edit"
    SOCIAL_SCRAPE = "social_scrape"
    DOC_CONVERT = "doc_convert"
    MALWARE_SCAN = "malware_scan"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SATELLITE_ANALYSIS = "satellite_analysis"
    CODE_EXECUTE = "code_execute"
    VOICE_COMMAND = "voice_command"
    CRYPTO_ANALYSIS = "crypto_analysis"
    FLOWCHART = "flowchart"
    EXCEL_EXPORT = "excel_export"


# Keyword-based classification rules
TASK_PATTERNS: dict[TaskType, list[str]] = {
    TaskType.BROWSER_SEARCH: [
        r"!cari\b", r"!search\b", r"!google\b", r"cari(?:kan|in)?\s",
        r"tolong carikan", r"harga\s\w+",
    ],
    TaskType.OSINT_SCAN: [
        r"!scan\b", r"!osint\b", r"!recon\b", r"!whois\b",
        r"scan domain", r"cek keamanan",
    ],
    TaskType.BLOCKCHAIN_CHECK: [
        r"!wallet\b", r"!tx\b", r"!crypto\b", r"!chain\b",
        r"cek wallet", r"transaksi", r"portfolio",
    ],
    TaskType.CRYPTO_ANALYSIS: [
        r"!analisa\s*crypto", r"!fundamental\b", r"!defi\b",
        r"analisa\s*(coin|token)", r"market\s*sentiment",
    ],
    TaskType.FILE_DOWNLOAD: [
        r"!download\b", r"!dl\b", r"!unduh\b",
        r"download\s*(video|musik|music|lagu|file)",
    ],
    TaskType.MEDIA_EDIT: [
        r"!edit\b", r"!resize\b", r"!watermark\b", r"!ocr\b",
        r"edit\s*(gambar|foto|video|image)",
    ],
    TaskType.SOCIAL_SCRAPE: [
        r"!ig\b", r"!tiktok\b", r"!twitter\b", r"!yt\b",
        r"scrape\s*(instagram|tiktok|twitter|youtube)",
    ],
    TaskType.DOC_CONVERT: [
        r"!convert\b", r"!pdf\b", r"!word\b", r"!excel\b",
        r"convert\s*(pdf|word|excel)", r"buat\s*excel",
    ],
    TaskType.MALWARE_SCAN: [
        r"!malware\b", r"!sandbox\b", r"!yara\b", r"!scan\s*file",
        r"analisa\s*(file|malware|virus)",
    ],
    TaskType.SENTIMENT_ANALYSIS: [
        r"!sentimen\b", r"!sentiment\b", r"analisa\s*sentimen",
    ],
    TaskType.CODE_GENERATION: [
        r"!code\b", r"!coding\b", r"buatkan\s*(kode|code|script|program)",
    ],
    TaskType.CODE_EXECUTE: [
        r"!run\b", r"!exec\b", r"!jalankan\b", r"jalankan\s*(kode|code)",
    ],
    TaskType.COMPLEX_REASONING: [
        r"jelaskan\s*(secara|dengan)\s*detail", r"analisa\s*mendalam",
        r"bandingkan\b", r"evaluasi\b",
    ],
    TaskType.VOICE_COMMAND: [
        r"!voice\b", r"!suara\b",
    ],
    TaskType.FLOWCHART: [
        r"!flowchart\b", r"!diagram\b", r"!usecase\b",
        r"buatkan\s*(flowchart|diagram|use\s*case)",
    ],
    TaskType.EXCEL_EXPORT: [
        r"!export\b", r"export\s*(excel|csv|data)",
    ],
}


class TaskClassifier:
    """Classify incoming messages to determine the right agent/tool."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._compiled_patterns: dict[TaskType, list[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        for task_type, patterns in TASK_PATTERNS.items():
            self._compiled_patterns[task_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    async def classify(
        self,
        text: str,
        media: dict | None = None,
        context: list[dict] | None = None,
    ) -> TaskType:
        """Classify a message into a TaskType."""

        # 1. Check for explicit command prefix matches
        for task_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    logger.debug(f"Pattern match: {task_type.value} via {pattern.pattern}")
                    return task_type

        # 2. Media-based classification
        if media:
            media_type = media.get("type", "")
            if media_type in ("image", "photo"):
                return TaskType.MEDIA_EDIT
            elif media_type in ("audio", "voice", "ptt"):
                return TaskType.VOICE_COMMAND
            elif media_type in ("document",):
                ext = media.get("filename", "").lower().split(".")[-1]
                if ext in ("exe", "dll", "apk", "bat", "ps1"):
                    return TaskType.MALWARE_SCAN
                elif ext in ("pdf", "docx", "xlsx"):
                    return TaskType.DOC_CONVERT

        # 3. Context-based: if long conversation, likely needs conversation mode
        if context and len(context) > 4:
            return TaskType.CONVERSATION

        # 4. Default: general conversation
        return TaskType.GENERAL
