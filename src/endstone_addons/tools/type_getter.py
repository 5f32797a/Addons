from endstone_addons.types.pack_type import PackType

def get_pack_type(manifest: dict) -> str:
    """
    Determines the pack type (BP, RP, or Unknown) by inspecting the modules in the manifest.
    """
    # A list of types that are considered part of a Behavior Pack.
    # 'data' is for things like entities, loot tables. 'script' is for JavaScript/TypeScript modules.
    behavior_pack_types = {"data", "script"}

    # 'resources' is the primary type for Resource Packs.
    resource_pack_types = {"resources"}

    # We can determine the type with a higher degree of certainty by checking all modules.
    is_bp = False
    is_rp = False

    for module in manifest.get("modules", []):
        module_type = module.get("type")
        if module_type in behavior_pack_types:
            is_bp = True
        elif module_type in resource_pack_types:
            is_rp = True

    # A pack can technically contain both, but for installation purposes,
    # we prioritize BP if any BP-related modules are found.
    if is_bp:
        return PackType.Bp
    
    if is_rp:
        return PackType.Rp
        
    # If no known module types are found after checking all modules, it's unknown.
    return PackType.Unknown