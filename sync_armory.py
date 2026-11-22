#!/usr/bin/env python3
"""Synchronize configured WoW Forever characters from Blizzard's public Armory."""
import datetime
import html
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

# Supported regions:
#   us - Americas & Oceania
#   eu - Europe
#   kr - Korea
#   tw - Taiwan
# China (cn) is not supported.
REGION = "us"

# Add your WoW Forever characters here.
# name: Character display name, e.g. "Firstname Lastname"
# slug: Final part of the Armory URL, e.g. "firstname-lastname"
CHARACTERS = [
    {"name": "Firstname Lastname", "slug": "firstname-lastname"},
]

ROOT = Path(__file__).resolve().parent
USER_AGENT = "Mozilla/5.0 (compatible; wow-forever-armory/1.0)"

TABS = {
    "reputation": "/reputation",
    "collections": "/collections",
    "pvp": "/pvp",
    "achievements": "/achievements",
    "collection_mounts": "/collections/mounts",
}


def fetch_state(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=25) as response:
        page = response.read(4_000_000).decode("utf-8", errors="replace")
    return extract_armory_profile(page)


def extract_armory_profile(page):
    """Extract Blizzard's embedded character profile state."""
    for match in re.finditer(r'characterProfileInitialState\s*[:=]\s*', page):
        remainder = page[match.end():].lstrip()
        if remainder.startswith("&quot;"):
            remainder = html.unescape(remainder)
        if remainder.startswith('"'):
            try:
                value, _ = json.JSONDecoder().raw_decode(remainder)
                if isinstance(value, str):
                    return json.loads(value)
            except (ValueError, TypeError):
                continue
        if remainder.startswith("{"):
            try:
                value, _ = json.JSONDecoder().raw_decode(remainder)
                if isinstance(value, dict):
                    return value
            except ValueError:
                continue
    return None


def sync_character(character):
    name, slug = (character[key] for key in ("name", "slug"))
    region = REGION.lower()

    if region not in ("us", "eu", "kr", "tw"):
        raise ValueError(f"Unsupported region: {region}")
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError(f"Invalid character slug: {slug}")

    locale = {
        "us": "en-us",
        "eu": "en-gb",
        "kr": "ko-kr",
        "tw": "zh-tw",
    }[region]

    armory = (
        f"https://worldofwarcraft.blizzard.com/"
        f"{locale}/forever/{region}/armory/character/{slug}"
    )

    output = ROOT / f"characters/{slug}.json"
    diagnostic = ROOT / f"characters/{slug}-status.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    data, errors = {}, {}

    try:
        profile = fetch_state(armory)
        if not isinstance(profile, dict) or not isinstance(profile.get("character"), dict):
            raise ValueError("Missing embedded character profile")

        data["armory_initial_state"] = profile

        # Expose Blizzard-hosted character image URLs without downloading image files.
        character_media = profile["character"].get("media", {})
        avatar = profile["character"].get("avatar", {})
        images = {}

        if isinstance(avatar, dict) and isinstance(avatar.get("url"), str):
            images["portrait"] = avatar["url"]

        if isinstance(character_media, dict):
            for source, target in (
                ("main-raw", "full_body"),
                ("main-sd-raw", "full_body_sd"),
                ("avatar-sd", "portrait_sd"),
            ):
                value = character_media.get(source)
                if isinstance(value, dict) and isinstance(value.get("url"), str):
                    images[target] = value["url"]

        if images:
            data["character_images"] = images

        print(f"{name}: profile OK")

    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as error:
        errors["armory_profile"] = str(error)
        print(f"{name}: profile unavailable ({type(error).__name__})")

    if "armory_initial_state" in data:
        tabs = {}

        for key, suffix in TABS.items():
            url = armory + suffix
            try:
                state = fetch_state(url)
                if not state:
                    raise ValueError("No embedded state")
                tabs[key] = {"url": url, "state": state}
                print(f"{name}: {key} OK")
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as error:
                errors[key] = str(error)
                print(f"{name}: {key} unavailable")

        categories = (
            tabs.get("achievements", {})
            .get("state", {})
            .get("achievementIndex", {})
            .get("categories", [])
        )

        for category in categories:
            slug_part = category.get("url")
            if not isinstance(slug_part, str) or not re.fullmatch(r"[a-z0-9-]{1,80}", slug_part):
                continue

            url = armory + "/achievements/" + slug_part
            key = "achievements_" + slug_part

            try:
                state = fetch_state(url)
                if not state:
                    raise ValueError("No embedded state")
                tabs[key] = {"url": url, "state": state}
                print(f"{name}: {key} OK")
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as error:
                errors[key] = str(error)

        data["armory_tabs"] = tabs

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    success = "armory_initial_state" in data

    status = {
        "character": name,
        "checked_at_utc": timestamp,
        "source": "official_armory_html" if success else None,
        "armory_url": armory,
        "endpoint_errors": errors,
        "success": success,
    }

    previous_status = None
    if diagnostic.exists():
        try:
            previous_status = json.loads(diagnostic.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass

    status_changed = (
        previous_status is None
        or {k: v for k, v in status.items() if k != "checked_at_utc"}
        != {k: v for k, v in previous_status.items() if k != "checked_at_utc"}
    )

    if status_changed:
        diagnostic.write_text(
            json.dumps(status, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{name}: sync status changed")
    else:
        print(f"{name}: sync status unchanged")

    if not success:
        print(f"{name}: previous successful snapshot retained")
        return

    snapshot = {
        "character": name,
        "fetched_at_utc": timestamp,
        "source": "official_armory_html",
        "data": data,
        "endpoint_errors": errors,
    }

    previous_snapshot = None
    if output.exists():
        try:
            previous_snapshot = json.loads(output.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass

    unchanged = (
        previous_snapshot is not None
        and {k: v for k, v in snapshot.items() if k != "fetched_at_utc"}
        == {k: v for k, v in previous_snapshot.items() if k != "fetched_at_utc"}
    )

    if unchanged:
        print(f"{name}: character data unchanged; previous snapshot retained")
        return

    output.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{name}: saved {output.relative_to(ROOT)}")


def main():
    if not CHARACTERS:
        raise ValueError("CHARACTERS must not be empty")

    for character in CHARACTERS:
        sync_character(character)


if __name__ == "__main__":
    main()
