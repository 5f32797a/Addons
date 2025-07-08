# Addons

A plugin for [Endstone](https://github.com/EndstoneMC) written in Python. It provides a robust system to automatically install and manage Minecraft Bedrock addons by extracting them from a local folder or downloading them from the internet.

## Key Features

- **Automated Installation:** Extracts `.mcpack`, `.mcaddon`, and `.zip` files from a local `addons/` folder.
- **Remote Addons:** Downloads and installs addons from URLs specified in the configuration.
- **Intelligent State Management:**
    - **Modification Detection:** Automatically detects when an addon file is changed, cleans up the old version, and installs the new one.
    - **Automatic Cleanup:** Removes installed packs if their source addon file is deleted from the `addons/` folder.
    - **Self-Healing:** Re-installs packs if it detects they have been manually removed from the world folder.
- **Robust Extraction:** Reliably processes complex addons, including `.mcaddon` files that contain multiple nested `.mcpack` files.
- **Conflict-Free:** Generates unique folder names for each pack to prevent conflicts.
- **World Pack Configuration:** Automatically updates the `world_behavior_packs.json` and `world_resource_packs.json` for the specified world.

## Folder Structure

```
your-server/
│
├── plugins/
│   └── configuration/
│       └── addons/
│           ├── config.json      # Main configuration file
│           └── processed.json   # Stores the state of processed addons (auto-generated)
│
├── addons/                      # Place your local addons here
│   ├── ExampleAddon.zip
│   └── CoolPack.mcaddon
│
└── worlds/
    └── Bedrock level/           # Your world folder (must match "world" in config.json)
        ├── behavior_packs/
        └── resource_packs/
```

## Configuration

Create a file at:
`/plugins/configuration/addons/config.json`

```json
{
    "world": "Bedrock level",
    "addons": [
        {
            "name": "Some-Cool-Addon",
            "url": "https://example.com/some-addon.zip"
        },
        {
            "name": "Another-Addon",
            "url": "https://example.com/another-addon.mcaddon"
        }
    ]
}
```
- **world**: The exact name of your world folder.
- **addons**: A list of remote addons to download. The `name` is used for the downloaded filename.

## How It Works

The plugin is designed to be fully automatic after the initial setup.

1.  **On Server Start:**
    - The plugin scans the `/addons/` folder for any new, modified, or removed addon files.
    - It downloads any remote addons defined in `config.json` and checks if they have been updated.
    - It processes all required addons, extracts their contents into unique folders within the world's `behavior_packs` and `resource_packs` directories.
    - It cleans up any packs associated with deleted or modified addon files.
    - Finally, it updates the world's configuration files to ensure all addons are enabled.

2.  **State Tracking:**
    The plugin keeps track of every addon it processes in the `processed.json` file. It stores a "footprint" (a hash or modification date) for each file. This allows it to intelligently determine what needs to be added, updated, or removed on each server start, making the process highly efficient.

## Notes

- To use a GitHub repository as a source for an addon, ensure the URL points to a raw file download link, not the repository page. For public repositories, the "Code" -> "Download ZIP" link works well.
- The plugin uses file footprints (ETags for remote files, modification times for local files) to detect changes. Some hosts may not provide a stable ETag, which could cause the addon to be re-downloaded. Using direct download links is recommended.
