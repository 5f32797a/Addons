# Addons
A plugin for [Endstone](https://github.com/EndstoneMC) written in Python. It installs Minecraft Bedrock addons automatically by extracting them from a local folder or downloading from the internet.

## Features
- Automatically extracts `.mcaddon` and `.zip` files from a local `addons/` folder.
- Downloads and installs remote addons from configured URLs.
- Supports both behavior packs and resource packs.
- Adds addons to the specified world folder.

## Folder Structure

```
your-server/
│
├── plugins/
│   ├── addons.py                # Your plugin file
│   └── configuration/
│       └── addons/
│           └── config.json      # Configuration file
│
├── addons/                      # Local addons (.zip or .mcaddon) go here
│   ├── ExampleAddon.zip
│   └── CoolPack.mcaddon
│
└── worlds/
    └── Bedrock level/           # World folder (match "world" value from conf.json)
        ├── behavior_packs/
        └── resource_packs/
```

## Configuration

Create a file at:  
`/plugins/configuration/addons/config.json`

```json
{
    "world": "Bedrock level", // Name of the world folder
    "addons": [
        {
            "name": "Some Cool Addon",
            "url": "https://example.com/some-addon.zip"
        },
        {
            "name": "Another Addon",
            "url": "https://example.com/another-addon.mcaddon"
        }
    ]
}
```

## Usage

1. **Local Addons**  
   Place any `.zip` or `.mcaddon` files into the `/addons/` folder.

2. **Remote Addons**  
   Define them in the `config.json` file under the `addons` list.

3. **On Server Start**  
   - The plugin extracts local addons from `/addons/`.
   - Downloads and installs the remote addons listed in the config.
   - Automatically puts behavior packs and resource packs into the corresponding subfolders of the specified world.

## Notes
- `.mcaddon` files are treated as ZIP archives and extracted.
- If the archive includes both `behavior_packs` and `resource_packs`, contents will be copied to both folders.
- Make sure the `"world"` value matches your actual world folder name (case-sensitive).
- If u wanna use github as a source for addons, make sure the URL points to the raw file, e.g. `https://codeload.github.com/Mih4n/portfolio/zip/refs/heads/main`. 
Cause plugin uses etag to identify if the file was changed, and github does not provide etag for `https://github.com/Mih4n/portfolio/archive/refs/heads/main.zip`.
