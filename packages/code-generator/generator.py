# ═══════════════════════════════════════════════════════════════
# CODE GENERATOR — Multi-language code gen + testing
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import logging, asyncio, tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger("nexus.codegen")


class CodeGenerator:
    """AI-powered multi-language code generation."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        logger.info("⚡ Code Generator initialized")

    async def generate(self, prompt: str, language: str = "python", framework: str = "") -> dict:
        """Generate code from natural language prompt using LLM."""
        from packages.agents.orchestrator import NexusOrchestrator

        system_prompt = (
            f"Kamu adalah code generator expert. Generate {language} code"
            f"{' menggunakan ' + framework if framework else ''}. "
            "Output HANYA kode, tanpa penjelasan. Format rapi dengan proper indentation."
        )

        config = self.config
        orchestrator = NexusOrchestrator(config)
        result = await orchestrator.process(
            user_id="codegen", session_id="codegen",
            text=f"Generate {language} code: {prompt}",
        )

        code = self._extract_code(result.get("response", ""))
        return {
            "code": code, "language": language, "framework": framework,
            "prompt": prompt, "model": result.get("agent_used", ""),
        }

    def _extract_code(self, response: str) -> str:
        """Extract code block from LLM response."""
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                code = parts[1]
                if code.startswith(("python", "javascript", "typescript", "java", "go", "rust")):
                    code = "\n".join(code.split("\n")[1:])
                return code.strip()
        return response.strip()

    async def validate_code(self, code: str, language: str) -> dict:
        """Validate generated code by syntax check."""
        if language == "python":
            return await self._validate_python(code)
        elif language in ("javascript", "js"):
            return await self._validate_js(code)
        return {"valid": True, "message": "Validation not available for this language"}

    async def _validate_python(self, code: str) -> dict:
        try:
            compile(code, "<codegen>", "exec")
            return {"valid": True, "message": "✅ Syntax valid"}
        except SyntaxError as e:
            return {"valid": False, "message": f"❌ Syntax error line {e.lineno}: {e.msg}"}

    async def _validate_js(self, code: str) -> dict:
        proc = await asyncio.create_subprocess_exec(
            "node", "-e", f"try {{ new Function({repr(code)}); console.log('OK') }} catch(e) {{ console.error(e.message) }}",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode().strip()
        if output == "OK":
            return {"valid": True, "message": "✅ Syntax valid"}
        return {"valid": False, "message": f"❌ {stderr.decode().strip() or output}"}

    async def generate_test(self, code: str, language: str) -> str:
        """Generate unit test for given code."""
        if language == "python":
            return self._generate_pytest(code)
        elif language in ("javascript", "js"):
            return self._generate_jest(code)
        return "# Test generation not available for this language"

    def _generate_pytest(self, code: str) -> str:
        lines = code.split("\n")
        funcs = [l.split("def ")[1].split("(")[0] for l in lines if l.strip().startswith("def ") and not l.strip().startswith("def _")]
        tests = ["import pytest", "", "# Auto-generated tests", ""]
        for func in funcs:
            tests.append(f"def test_{func}():")
            tests.append(f"    result = {func}()")
            tests.append(f"    assert result is not None")
            tests.append("")
        return "\n".join(tests)

    def _generate_jest(self, code: str) -> str:
        import re
        funcs = re.findall(r'(?:function|const|let)\s+(\w+)', code)
        tests = ["// Auto-generated tests", ""]
        for func in funcs[:5]:
            tests.append(f"test('{func} should work', () => {{")
            tests.append(f"  expect({func}).toBeDefined();")
            tests.append("});")
            tests.append("")
        return "\n".join(tests)
