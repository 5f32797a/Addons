from endstone_addons.types.pack_type import PackType

def get_pack_type(manifest: dict) -> str:
    for module in manifest.get("modules", []):
        if module.get("type") == "data":
            return PackType.Bp
        elif module.get("type") == "resources":
            return PackType.Rp
        
    return PackType.Unknown