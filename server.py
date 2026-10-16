"""Serveur MCP qui expose le catalogue github.com/public-apis/public-apis a Claude.

Outils :
  list_categories  -> les 52 categories et leur nombre d'API
  search_apis      -> recherche plein texte (nom, description, categorie), filtre auth
  call_api         -> GET sur une URL dont le domaine appartient au catalogue
"""
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from mcp.server.fastmcp import FastMCP

APIS = json.loads((Path(__file__).parent / "apis.json").read_text(encoding="utf-8"))


def _root(host: str) -> str:
    parts = host.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host.lower()


# Seuls les domaines (et sous-domaines) presents dans le catalogue sont appelables.
ALLOWED_ROOTS = {_root(urlparse(a["url"]).hostname or "") for a in APIS} - {"", "github.com", "github.io"}
MAX_BYTES = 200_000

mcp = FastMCP("public-apis", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


@mcp.tool()
def list_categories() -> dict[str, int]:
    """Liste les categories du catalogue public-apis avec le nombre d'API dans chacune."""
    counts: dict[str, int] = {}
    for a in APIS:
        counts[a["category"]] = counts.get(a["category"], 0) + 1
    return counts


@mcp.tool()
def search_apis(query: str = "", category: str = "", no_auth_only: bool = False, limit: int = 20) -> list[dict]:
    """Cherche des API publiques par mot-cle (nom, description) et/ou categorie.
    no_auth_only=True ne garde que les API utilisables sans cle."""
    q, c = query.lower(), category.lower()
    hits = [
        a for a in APIS
        if (not q or q in a["name"].lower() or q in a["description"].lower())
        and (not c or c in a["category"].lower())
        and (not no_auth_only or not a["auth"])
    ]
    return hits[: max(1, min(limit, 100))]


@mcp.tool()
async def call_api(url: str, params: dict[str, str] | None = None) -> dict:
    """Fait un GET sur une API du catalogue et renvoie le statut et le corps (tronque a 200 Ko).
    L'URL doit etre en https et appartenir a un domaine du catalogue.
    La page de doc de l'API (champ url de search_apis) indique les endpoints reels."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return {"error": "Seules les URL https sont acceptees."}
    if _root(parsed.hostname or "") not in ALLOWED_ROOTS:
        return {"error": f"Domaine {parsed.hostname} absent du catalogue public-apis."}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        r = await client.get(url, params=params, headers={"User-Agent": "public-apis-mcp/1.0"})
    body = r.text[:MAX_BYTES]
    try:
        body = json.loads(body)
    except ValueError:
        pass
    return {"status": r.status_code, "content_type": r.headers.get("content-type", ""), "body": body}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
