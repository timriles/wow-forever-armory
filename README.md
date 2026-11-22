# WoW Forever Armory

Automatically sync WoW Forever Armory character data to GitHub for tracking, analysis, and AI-assisted progression.

Everything runs through GitHub Actions. You do not need to keep a PC running or install Python locally.

## Setup

### 1. Fork this repository

Click **Fork** at the top of this repository and create the fork under your GitHub account.

Use your fork for your own character data. Do not edit the original repository.

### 2. Enable GitHub Actions

Open the **Actions** tab in your fork.

GitHub may show a message that workflows are disabled in forked repositories. If it does, click **I understand my workflows, go ahead and enable them**.

### 3. Add your region and characters

Open [armory-config.json](armory-config.json) in your fork and click the **pencil icon** to edit it in GitHub.

Set `region` to your Armory region and replace the `Your Character Name` placeholder in `characters` with your full display name. To track more characters, add their names to the list:

```json
{
  "region": "us",
  "characters": [
    "Firstname Lastname",
    "Anothername Lastname"
  ]
}
```

Enter each name once, using the same capitalization as in-game. The collector preserves the display name and generates the Armory slug automatically. For example, `Firstname Lastname` becomes `firstname-lastname`.

Separate names with commas and click **Commit changes** when you're done. If you configured an earlier version in `sync_armory.py`, copy your region and display names into `armory-config.json`.

### 4. Check the first sync

After you enable Actions, committing changes to `armory-config.json` on `main` starts a sync automatically.

Open **Actions → Sync WoW Forever Armory** and select the latest run. Its **Summary** shows each character’s result, the Armory URL it tried, and any unavailable pages. Successful snapshots appear in the `characters/` directory.

To sync manually, click **Run workflow** and select your default branch.

### 5. Automatic updates

After setup, GitHub Actions checks your configured characters every 30 minutes at **:07** and **:37** past the hour.

The workflow only creates a new commit when character data or sync status actually changes, so unchanged checks do not continuously grow the repository history.

GitHub may occasionally delay scheduled workflows.

## Supported regions

| Setting | Region |
| --- | --- |
| `us` | Americas & Oceania |
| `eu` | Europe |
| `kr` | Korea |
| `tw` | Taiwan |

China (`cn`) is not supported.

All characters in a fork use the same `region` from `armory-config.json`.

## What gets collected

The collector reads structured data embedded in Blizzard's public WoW Forever Armory pages, including:

- Character details and combat stats
- Equipped gear and item data
- Talents
- Profession skill levels
- Faction reputations
- PvP information
- Mounts and companion pets
- Achievement progress
- Blizzard-hosted portrait and full-body character image URLs

## Output files

Each configured character receives two files:

| File | Contents |
| --- | --- |
| `characters/<slug>.json` | Latest successful character snapshot |
| `characters/<slug>-status.json` | Latest recorded sync status |

For example:

```text
characters/
├── firstname-lastname.json
└── firstname-lastname-status.json
```

A failed fetch does not replace the last successful character snapshot.

The snapshot's `fetched_at_utc` value changes only when meaningful character data changes. Repeated identical checks do not rewrite the file.

## Using the data with AI assistants

Because the character data is stored as JSON in GitHub, an AI assistant with access to your fork can use your actual character state instead of relying only on generic level-based information.

For example:

> Read my latest character snapshot from this repository. Review my current gear, stats, professions, and progression, then recommend useful upgrades for my level in WoW Forever.

You can also ask about:

- Gear comparisons
- Dungeon upgrade opportunities
- Profession progression
- Reputation progress
- Current stats and equipment
- Mounts, pets, and achievements

The snapshot describes your current character state. Recommendations such as best-in-slot gear, dungeon strategy, or optimal talents may require additional WoW Forever-specific research.

## Limitations

The public Armory does not expose everything.

This collector does not currently provide:

- Active quests
- Complete quest history
- Bags or bank contents
- Gold
- Complete toy collections
- Complete appearance collections

Blizzard controls the underlying Armory page format, so the collector may need updates if that format changes.

## Running locally

Local use is optional. The GitHub workflow is enough for normal use. The script reads `armory-config.json` from the same directory as `sync_armory.py`.

If you want to run the collector manually:

```sh
python3 sync_armory.py
```

It uses only Python's standard library and requires no additional packages.

## Repository layout

```text
wow-forever-armory/
├── .github/
│   └── workflows/
│       └── sync-armory.yml
├── characters/
├── armory-config.json
├── README.md
└── sync_armory.py
```

This is an independent project and is not affiliated with Blizzard Entertainment.
