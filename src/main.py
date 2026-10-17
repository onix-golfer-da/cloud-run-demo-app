import os
import socket
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from cryptography import x509
from cryptography.hazmat.backends import default_backend

app = FastAPI(title="Cloud Run Secrets Demo", version="1.0.0")

CERT_PATH = "/etc/ssl/demo/tls.crt"

def read_certificate_info(cert_path: str = CERT_PATH) -> dict:
    if not os.path.exists(cert_path):
        return {
            "status": "not_found",
            "path": cert_path,
            "message": "Certificate file not mounted at path",
            "subject": None,
            "issuer": None,
            "not_valid_before": None,
            "not_valid_after": None,
            "serial_number": None,
            "raw_preview": None
        }

    try:
        with open(cert_path, "rb") as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        raw_text = cert_data.decode("utf-8", errors="replace")
        preview = "\n".join(raw_text.strip().splitlines()[:6]) + "\n... (truncated)"

        return {
            "status": "mounted",
            "path": cert_path,
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "not_valid_before": cert.not_valid_before_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "not_valid_after": cert.not_valid_after_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "serial_number": hex(cert.serial_number),
            "raw_preview": preview
        }
    except Exception as e:
        return {
            "status": "error",
            "path": cert_path,
            "message": str(e),
            "subject": None,
            "issuer": None,
            "not_valid_before": None,
            "not_valid_after": None,
            "serial_number": None,
            "raw_preview": None
        }

@app.get("/healthz")
def healthz():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/", response_class=HTMLResponse)
def home():
    app_env = os.getenv("APP_ENV", "local-development (unset)")
    app_version = os.getenv("APP_VERSION", "v1.0.0")
    cert_info = read_certificate_info()
    hostname = socket.gethostname()
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    cert_status_badge = (
        '<span class="badge badge-success">Mounted & Verified</span>'
        if cert_info["status"] == "mounted"
        else '<span class="badge badge-warning">Unmounted / Local</span>'
    )

    cert_details_html = ""
    if cert_info["status"] == "mounted":
        cert_details_html = f"""
        <div class="meta-row"><strong>Subject:</strong> <code>{cert_info['subject']}</code></div>
        <div class="meta-row"><strong>Issuer:</strong> <code>{cert_info['issuer']}</code></div>
        <div class="meta-row"><strong>Valid From:</strong> {cert_info['not_valid_before']}</div>
        <div class="meta-row"><strong>Valid To:</strong> {cert_info['not_valid_after']}</div>
        <div class="meta-row"><strong>Serial Number:</strong> <code>{cert_info['serial_number']}</code></div>
        <div class="meta-row" style="margin-top: 10px;">
            <strong>PEM Preview:</strong>
            <pre class="code-box">{cert_info['raw_preview']}</pre>
        </div>
        """
    else:
        cert_details_html = f"""
        <p class="muted">Status: {cert_info.get('message', 'File not present')}</p>
        <p class="muted">Expected Path: <code>{cert_info['path']}</code></p>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Run + Secret Manager | DevOps CI/CD Demo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #111827;
            --surface-hover: #1f2937;
            --border: #374151;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --primary: #3b82f6;
            --primary-glow: rgba(59, 130, 246, 0.2);
            --accent-green: #10b981;
            --accent-yellow: #f59e0b;
            --accent-purple: #8b5cf6;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, var(--bg) 70%);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 900px;
            width: 100%;
        }}
        header {{
            text-align: center;
            margin-bottom: 35px;
        }}
        .logo-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.4);
            color: #93c5fd;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 9999px;
            margin-bottom: 16px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        h1 {{
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 40%, #93c5fd 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        p.subtitle {{
            color: var(--text-muted);
            font-size: 1.05rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .card:hover {{
            border-color: #4b5563;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #1f2937;
        }}
        .card-title {{
            font-size: 1.15rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            text-transform: uppercase;
        }}
        .badge-success {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-info {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }}
        .meta-row {{
            margin-bottom: 10px;
            font-size: 0.92rem;
            color: #d1d5db;
        }}
        .meta-row strong {{
            color: #9ca3af;
            display: inline-block;
            min-width: 110px;
        }}
        code {{
            font-family: 'JetBrains Mono', monospace;
            background: #1f2937;
            padding: 2px 6px;
            border-radius: 4px;
            color: #67e8f9;
            font-size: 0.88rem;
        }}
        .code-box {{
            font-family: 'JetBrains Mono', monospace;
            background: #030712;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
            font-size: 0.8rem;
            color: #a7f3d0;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .runtime-bar {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .runtime-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 8px var(--accent-green);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-badge">
                <span class="dot"></span> DevOps Multi-Repo CI/CD Demo
            </div>
            <h1>Cloud Run Application Service</h1>
            <p class="subtitle">Live verification of Google Secret Manager injection patterns</p>
        </header>

        <div class="grid">
            <!-- Pattern 1: Environment Variable -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🔑 Secret #1: Environment Var</span>
                    <span class="badge badge-info">Injected</span>
                </div>
                <div class="meta-row"><strong>Secret Name:</strong> <code>demo-app-config</code></div>
                <div class="meta-row"><strong>Target Variable:</strong> <code>$APP_ENV</code></div>
                <div class="meta-row"><strong>Resolved Value:</strong> <code style="color: #4ade80; font-size: 1rem; font-weight: bold;">{app_env}</code></div>
                <div class="meta-row" style="margin-top: 15px;">
                    <p class="muted" style="font-size: 0.85rem; color: #9ca3af;">
                        Cloud Run reads the latest secret payload directly upon instance startup and injects it into container process environment variables.
                    </p>
                </div>
            </div>

            <!-- Pattern 2: Volume Mount -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📜 Secret #2: Volume Mount</span>
                    {cert_status_badge}
                </div>
                <div class="meta-row"><strong>Secret Name:</strong> <code>demo-tls-cert</code></div>
                <div class="meta-row"><strong>Mount Path:</strong> <code>{cert_info['path']}</code></div>
                {cert_details_html}
            </div>
        </div>

        <div class="runtime-bar">
            <div class="runtime-item">
                <span class="dot"></span>
                <span>Container Host: <code>{hostname}</code></span>
            </div>
            <div class="runtime-item">
                <span>App Version: <code>{app_version}</code></span>
            </div>
            <div class="runtime-item">
                <span>Server Time: {current_time}</span>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html)
