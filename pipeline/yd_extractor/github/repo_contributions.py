import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import pandera as pa
import requests
from pandera.typing.pandas import DataFrame

from yd_extractor.github.schemas import (GithubRepoContributions,
                                         RawGithubRepoContributions)
from yd_extractor.utils.pandas import (convert_columns_to_numeric,
                                       validate_columns)
from yd_extractor.utils.pipeline_stage import PipelineStage

logger = logging.getLogger(__name__)


def unpack_contributions_dict(contributions_for_repo: dict) -> list[dict]:
    """Unpacks contribution dicts obtained from the using a graphql query on github
    contribution activity.

    Parameters
    ----------
    contributions_for_repo : dict
        Has structure like:
        ```
        {
            "contributions": {
                "nodes": [
                    {
                        "commitCount": int,
                        "occurredAt": str,
                        "repository": {
                            "name": str,
                            "url": str,
                            "openGraphImageUrl": str
                        }
                    }
                ]
            }
        }
        ```

    Returns
    -------
    list[dict]
        Has structure like:
        ```
        [
            {
                commit_count: int
                occurred_at: str
                repository_name: str,
                repository_url: str,
                repositroy_image: str
            }
        ]
        ```
    """
    node_list = contributions_for_repo["contributions"]["nodes"]
    node_list = [
        {
            "commit_count": node["commitCount"],
            "occured_at": node["occurredAt"],
            "repository_name": node["repository"][
                "name"
            ],  # these should all be the same :p
            "repository_url": node["repository"]["url"],
            "repository_image": node["repository"]["openGraphImageUrl"],
        }
        for node in node_list
    ]
    return node_list


@pa.check_types
def extract_repo_contributions(
    github_token: str, year: int
) -> DataFrame[RawGithubRepoContributions]:

    if year < 2005:
        raise Exception("Can't load contributions from before 2005!")

    logger.info(
        f"Making request to https://api.github.com/graphql for repo contribution"
        f"data from {year}"
    )

    # Load query from seperate file
    query = None
    path_to_query = (
        Path(__file__).parent / "graphql" / "GetUserRepoContributions.graphql"
    )
    with open(path_to_query, "r") as file:
        query = file.read()
    if query is None:
        raise Exception("Couldn't load query GetUserRepoContributions!")

    # Post request to github graphql api
    variables = {
        "from": f"{year}-01-01T00:00:00Z",
        "to": f"{year}-12-31T23:59:59Z",
    }
    headers = {"Authorization": f"Bearer {github_token}"}
    repos_url = f"https://api.github.com/graphql"
    response = requests.post(
        repos_url,
        json={"query": query, "variables": variables},
        headers=headers,
        verify=False,
    )
    if not response.ok:
        response.raise_for_status()

    # Turn response object into pandas dataframe
    response_json = response.json()
    contributions_by_repos = response_json["data"]["viewer"]["contributionsCollection"][
        "commitContributionsByRepository"
    ]
    full_contribution_list = []
    for repo_contributions in contributions_by_repos:
        full_contribution_list.extend(unpack_contributions_dict(repo_contributions))

    df = pd.DataFrame(full_contribution_list)
    if df.empty:
        df = RawGithubRepoContributions.empty()
    df = RawGithubRepoContributions.validate(df)
    return df


@pa.check_types
def transform_repo_contributions(
    df: DataFrame[RawGithubRepoContributions],
) -> DataFrame[GithubRepoContributions]:
    df["date"] = df["occured_at"].dt.date
    df = df.rename(columns={"commit_count": "total_commits"})
    df = df[
        [
            "date",
            "total_commits",
            "repository_name",
            "repository_url",
            "repository_image",
        ]
    ]
    if df.empty:
        df = GithubRepoContributions.empty()
    df = GithubRepoContributions.validate(df)
    return df


def process_repo_contributions(
    github_token: Optional[str], 
    start_year: int = 2020,
    load_function: Optional[Callable[[pd.DataFrame, str], None]] = None,
) -> pd.DataFrame:
    logger.info("Processing github repo contributions...")
    df = GithubRepoContributions.empty()
    with PipelineStage(logger, "repo_contributions"):
        if github_token is None:
            error_message = (
                "Couldn't process github data due to missing environment variables!"
            )
            raise Exception(error_message)
        
        df = RawGithubRepoContributions.empty()
        current_year = datetime.now().year
        for year in range(start_year, current_year + 1):
            df_raw = extract_repo_contributions(github_token, year)
            df = pd.concat([df, df_raw], ignore_index=True)
        df = transform_repo_contributions(df)
        
        if load_function:
            load_function(df, "github_repo_contributions")
    return df


if __name__ == "__main__":
    import os
    import dotenv
    
    logging.basicConfig(level=logging.INFO)
    dotenv.load_dotenv("config/.env")
    gh_token = os.environ.get("GITHUB_TOKEN")

    df = process_repo_contributions(gh_token)
    df.to_csv("data/output/github_repo_contributions.csv", index=False)
