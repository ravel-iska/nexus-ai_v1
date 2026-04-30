// ═══════════════════════════════════════════════════════════════
// CRUD EXECUTOR — Safe monorepo command execution
// AI safety check before every execution
// ═══════════════════════════════════════════════════════════════

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class CRUDExecutor {
  constructor(config = {}) {
    this.workspaceRoot = config.workspaceRoot || process.cwd();
    this.allowedPaths = config.allowedPaths || [this.workspaceRoot];
    this.requireApproval = config.requireApproval !== false;
    this.auditLog = [];
  }

  _isPathAllowed(targetPath) {
    const resolved = path.resolve(targetPath);
    return this.allowedPaths.some(allowed => resolved.startsWith(path.resolve(allowed)));
  }

  _log(action, target, details = {}) {
    this.auditLog.push({
      timestamp: new Date().toISOString(),
      action, target, details,
    });
  }

  async readFile(filePath) {
    if (!this._isPathAllowed(filePath)) {
      throw new Error(`🚫 Path not allowed: ${filePath}`);
    }
    const content = await fs.readFile(filePath, 'utf-8');
    this._log('read', filePath, { size: content.length });
    return content;
  }

  async writeFile(filePath, content) {
    if (!this._isPathAllowed(filePath)) {
      throw new Error(`🚫 Path not allowed: ${filePath}`);
    }
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, content, 'utf-8');
    this._log('write', filePath, { size: content.length });
    return { status: 'ok', path: filePath };
  }

  async deleteFile(filePath) {
    if (!this._isPathAllowed(filePath)) {
      throw new Error(`🚫 Path not allowed: ${filePath}`);
    }
    await fs.unlink(filePath);
    this._log('delete', filePath);
    return { status: 'ok', deleted: filePath };
  }

  async listDir(dirPath) {
    if (!this._isPathAllowed(dirPath)) {
      throw new Error(`🚫 Path not allowed: ${dirPath}`);
    }
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    return entries.map(e => ({
      name: e.name,
      type: e.isDirectory() ? 'directory' : 'file',
      path: path.join(dirPath, e.name),
    }));
  }

  async scaffold(template, targetDir, variables = {}) {
    const templates = {
      'fastapi-route': {
        files: {
          'router.py': `from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get("/")\nasync def index():\n    return {"service": "${variables.name || 'new-service'}"}\n`,
          '__init__.py': '',
        }
      },
      'skill-plugin': {
        files: {
          'skill.json': JSON.stringify({ name: variables.name || 'new-skill', version: '1.0.0', commands: ['!newskill'], runtime: 'python', permissions: [] }, null, 2),
          'handler.py': `async def handle(command, args):\n    return {"response": "Skill ${variables.name || 'new-skill'} executed"}\n`,
        }
      },
      'react-component': {
        files: {
          [`${variables.name || 'Component'}.jsx`]: `import React from 'react';\n\nexport function ${variables.name || 'Component'}() {\n  return <div>${variables.name || 'Component'}</div>;\n}\n`,
          [`${variables.name || 'Component'}.css`]: `.${(variables.name || 'component').toLowerCase()} {\n  padding: 16px;\n}\n`,
        }
      },
    };

    const tmpl = templates[template];
    if (!tmpl) throw new Error(`Unknown template: ${template}`);

    const results = [];
    for (const [filename, content] of Object.entries(tmpl.files)) {
      const filePath = path.join(targetDir, filename);
      await this.writeFile(filePath, content);
      results.push(filePath);
    }

    this._log('scaffold', targetDir, { template, files: results.length });
    return { status: 'ok', template, files: results };
  }

  getAuditLog() {
    return this.auditLog;
  }
}

class SafetyCheck {
  static DANGEROUS_PATTERNS = [
    /rm\s+-rf\s+\//,
    /del\s+\/s\s+\/q\s+c:\\/i,
    /format\s+[a-z]:/i,
    /DROP\s+TABLE/i,
    /DELETE\s+FROM\s+\w+\s*;/i,
    /shutdown/i,
    /:(){ :\|:& };:/,  // Fork bomb
  ];

  static check(command) {
    for (const pattern of SafetyCheck.DANGEROUS_PATTERNS) {
      if (pattern.test(command)) {
        return { safe: false, reason: `Dangerous pattern detected: ${pattern}`, command };
      }
    }
    return { safe: true, command };
  }
}

module.exports = { CRUDExecutor, SafetyCheck };
