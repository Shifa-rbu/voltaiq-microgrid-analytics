"""Bounded HTML-table scraping helpers for public, permitted sources."""
from __future__ import annotations

import ipaddress
import socket
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit

import pandas as pd
import requests
from bs4 import BeautifulSoup

MAX_PAGE_BYTES = 2_000_000
MAX_TABLES = 20
MAX_ROWS_PER_TABLE = 500
MAX_COLUMNS_PER_TABLE = 40
MAX_REDIRECTS = 5
USER_AGENT = "VoltaIQ-StudentAnalytics/1.0 (educational demonstration)"


def _validate_public_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.casefold() not in {"http", "https"}:
        raise ValueError("Use a public HTTP or HTTPS webpage URL.")
    if not parts.hostname or parts.username or parts.password:
        raise ValueError("Enter a valid public webpage URL without embedded credentials.")
    if parts.port and parts.port not in {80, 443}:
        raise ValueError("Only standard HTTP (80) and HTTPS (443) ports are allowed.")
    host = parts.hostname.rstrip(".").casefold()
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("Local or private-network URLs are not allowed.")
    try:
        addresses = {item[4][0].split("%", 1)[0] for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)}
    except OSError as exc:
        raise ValueError(f"Could not resolve the website host: {exc}") from exc
    if not addresses:
        raise ValueError("The website host did not resolve to a public address.")
    for address in addresses:
        try:
            if not ipaddress.ip_address(address).is_global:
                raise ValueError("The URL resolves to a non-public network address and is blocked.")
        except ValueError as exc:
            if "non-public" in str(exc):
                raise
            raise ValueError("The URL has an invalid network address.") from exc
    return url.strip()


def fetch_public_html(url: str) -> tuple[str, str, str]:
    """Fetch a bounded public HTML page; revalidate each redirect target."""
    current_url = _validate_public_url(url)
    session = requests.Session()
    session.trust_env = False
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    try:
        for _ in range(MAX_REDIRECTS + 1):
            response = session.get(current_url, headers=headers, timeout=(5, 15), allow_redirects=False, stream=True)
            if response.is_redirect or response.is_permanent_redirect:
                location = response.headers.get("Location")
                response.close()
                if not location:
                    raise ValueError("The source returned a redirect without a destination.")
                current_url = _validate_public_url(urljoin(current_url, location))
                continue
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").casefold()
            if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                response.close()
                raise ValueError(f"The source did not return HTML (content type: {content_type or 'unknown'}).")
            body = bytearray()
            for chunk in response.iter_content(chunk_size=16_384):
                body.extend(chunk)
                if len(body) > MAX_PAGE_BYTES:
                    raise ValueError("The webpage is larger than the 2 MB safety limit.")
            encoding = response.encoding or "utf-8"
            response.close()
            return bytes(body).decode(encoding, errors="replace"), current_url, datetime.now(timezone.utc).isoformat(timespec="seconds")
        raise ValueError("The source exceeded the redirect limit.")
    except requests.RequestException as exc:
        raise ValueError(f"Could not fetch the webpage: {exc}") from exc
    finally:
        session.close()


def _unique_headers(values: list[str]) -> list[str]:
    headers: list[str] = []
    used: dict[str, int] = {}
    for index, value in enumerate(values):
        base = " ".join(value.split())[:120] or f"Column {index + 1}"
        used[base] = used.get(base, 0) + 1
        headers.append(base if used[base] == 1 else f"{base} ({used[base]})")
    return headers


def extract_html_tables(html: str) -> list[pd.DataFrame]:
    """Extract non-empty, bounded HTML tables into pandas DataFrames."""
    soup = BeautifulSoup(html, "html.parser")
    tables: list[pd.DataFrame] = []
    for table in soup.find_all("table", limit=MAX_TABLES):
        rows = []
        header_index = None
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"], recursive=True)
            values = [" ".join(cell.stripped_strings)[:500] for cell in cells]
            if not any(values):
                continue
            if header_index is None and any(cell.name == "th" for cell in cells):
                header_index = len(rows)
            rows.append(values[:MAX_COLUMNS_PER_TABLE])
            if len(rows) >= MAX_ROWS_PER_TABLE + 1:
                break
        if not rows:
            continue
        if header_index is None:
            header_index = 0
        headers = _unique_headers(rows[header_index])
        records = []
        for row in rows[header_index + 1:]:
            if len(row) < len(headers):
                row = row + [""] * (len(headers) - len(row))
            records.append(row[:len(headers)])
        if records:
            frame = pd.DataFrame(records, columns=headers)
            frame = frame.replace(r"^\s*$", pd.NA, regex=True).dropna(how="all").reset_index(drop=True)
            if not frame.empty:
                tables.append(frame)
    return tables


def scrape_public_tables(url: str) -> tuple[list[pd.DataFrame], str, str]:
    html, source_url, fetched_at = fetch_public_html(url)
    tables = extract_html_tables(html)
    if not tables:
        raise ValueError("No usable HTML tables were found on that page. Try a public page containing a data table.")
    return tables, source_url, fetched_at
