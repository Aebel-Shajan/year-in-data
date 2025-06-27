from datetime import datetime
import dagster as dg
import pandas as pd
from transformations.utils.env import load_env_vars
from transformations.github import repo_contributions

@dg.asset(
    kinds={"bronze"},
)
def github_repo_contribution_jsons() -> str:
    env_vars = load_env_vars()
    if env_vars.GITHUB_TOKEN is None:
        raise dg.Failure(
            description="Expected 'GITHUB_TOKEN' in env vars!"
        )
    
    output_dir = "data/bronze/stage/github/repo_contributions"
    start_year = 2020 # TODO: Make this part of config when I get to making a config.
    current_year = datetime.now().year
    for year in range(start_year, current_year + 1):
        repo_contributions.request_repo_contributions(
            github_token=env_vars.GITHUB_TOKEN,
            year=year,
            output_dir=output_dir,
        )
    
    return output_dir
    

@dg.asset(
    kinds={"silver"},
    deps=[github_repo_contribution_jsons],
)
def github_repo_contributions_raw(github_repo_contribution_jsons: str) -> pd.DataFrame:
    df = repo_contributions.extract_repo_contributions(github_repo_contribution_jsons)
    return df

@dg.asset(
    kinds={"gold"},
    deps=[github_repo_contributions_raw],
)
def github_repo_contributions(github_repo_contributions_raw: pd.DataFrame) -> pd.DataFrame:
    df = repo_contributions.transform_repo_contributions(github_repo_contributions_raw)
    return df