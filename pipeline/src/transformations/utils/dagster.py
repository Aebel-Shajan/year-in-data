import dagster as dg

def get_dagster_type(assets_def: dg.AssetsDefinition) -> dg.DagsterType:
    return assets_def.node_def.output_dict["result"].dagster_type


def get_all_gold_assets(defs: dg.Definitions) -> list[dg.AssetsDefinition]:
    gold_assets = []
    for asset_def in defs.assets:
        medallions = asset_def.get_asset_spec().kinds
        if "gold" in medallions and isinstance(asset_def, dg.AssetsDefinition):
           gold_assets.append(asset_def)
    return gold_assets


def get_asset_metadata(assets_def: dg.AssetsDefinition) -> dict:
    return assets_def.get_asset_spec().metadata
