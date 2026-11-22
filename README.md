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

### 3. Add your character

Open **sync_armory.py** in your fork and click the **pencil icon** to edit the file directly in GitHub.

Near the top of the file, set your region and replace the placeholder character:

```python
REGION = "us"

CHARACTERS = [
    {"name": "Firstname Lastname", "slug": "firstname-lastname"},
]
```

Use the character's normal display name for `name`.

Use the final part of the Blizzard Armory URL for `slug`. For example:

```text
https://worldofwarcraft.blizzard.com/en-us/forever/us/armory/character/firstname-lastname
```

The slug is:

```text
firstname-lastname
```

To track multiple characters, add more entries:

```python
CHARACTERS = [
    {"name": "Firstname Lastname", "slug": "firstname-lastname"},
    {"name": "Anothername Lastname", "slug": "anothername-lastname"},
]
```

When finished, click **Commit changes**.

### 4. Run the first sync

Open:

**Actions → Sync WoW Forever Armory**

Click **Run workflow**, then run it from your default branch.

After the workflow finishes, your character data will appear in the `characters/` directory.

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

All characters in one fork currently use the same configured `REGION`.

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

Local use is optional. The GitHub workflow is enough for normal use.

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
├── README.md
└── sync_armory.py
```

This is an independent project and is not affiliated with Blizzard Entertainment.
