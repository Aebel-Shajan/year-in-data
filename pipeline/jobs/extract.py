from pipeline.common.config import PipelineConfig
from pipeline.common.r2 import R2Client
from pipeline.common.paths import Source
from pipeline.extract import fitbit, github, gymgroup, kindle, macos_commands, macos_screentime, strong

def extract_from_sources(r2: R2Client, config: PipelineConfig):
    sources_to_extract = config.sources_to_extract
    sources = [
        (Source.FITBIT, fitbit.extract_fitbit),
        (Source.GITHUB, github.extract_github),
        (Source.GYMGROUP, gymgroup.extract_gymgroup),
        (Source.KINDLE, kindle.extract_kindle),
        (Source.MACOS_COMMANDS, macos_commands.extract_macos_commands),
        (Source.MACOS_SCREENTIME, macos_screentime.extract_macos_screentime)
    ]

    for source, extraction_function in sources:
        if source in sources_to_extract:
            print(f"extracting {source}.. ")
            try:
                extraction_function(r2, config)
            except Exception as e:
                print("error encounted")
                print(e)
