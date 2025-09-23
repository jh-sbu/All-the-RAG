from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_source(url: str) -> str | None:
    """
    Fetch a CurseForge project page and return the GitHub/source URL if present.

    Strategy:
      1) Load the page (HTML) at `url`.
      2) Locate the "Links" section (id="project-links" or .project-links-container).
      3) Find an <a> whose visible text is exactly "Source" (case-insensitive).
      4) Return its absolute href, or None if not found.

    Fallback:
      - If no "Source" label is found, return the first link under the same section
        that points to a common code host (GitHub, GitLab, Bitbucket, Codeberg, SourceForge).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) Find the "Links" section (matches current CF HTML)
    links_section = soup.find("section", id="project-links") or soup.select_one(
        "section.project-links-container"
    )
    if not links_section:
        return None

    # 2) Prefer the <a> explicitly labeled "Source"
    for a in links_section.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "source":
            return urljoin(url, a["href"])

    # 3) Fallback: first link to a recognizable code host
    code_hosts = (
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "codeberg.org",
        "sourceforge.net",
    )
    for a in links_section.find_all("a", href=True):
        href = a["href"]
        if any(host in href for host in code_hosts):
            return urljoin(url, href)

    return None
