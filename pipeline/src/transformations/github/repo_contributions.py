import logging
from pathlib import Path

import json
import pandas as pd
import pandera as pa
import requests
from pandera.typing.pandas import DataFrame

from transformations.github.schemas import (GithubRepoContributions,
                                         RawGithubRepoContributions)

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

def request_repo_contributions(
    github_token: str, 
    year: int,
    output_dir: str,
) -> str:
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
    output_json_name = f"github-repo-contributions-{year}.json"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)  

    file_path = output_dir + "/" + output_json_name
    with open(file_path, "w") as json_file:
        json.dump(response_json, json_file, indent=4)
    return file_path


@pa.check_types
def extract_repo_contributions(response_folder: str) -> DataFrame[RawGithubRepoContributions]:
    response_folder: Path = Path(response_folder)
    full_data = []
    for file in response_folder.glob("github-repo-contributions*.json"):
        # TODO: Add validation in the future.
        with open(file) as response_json:
            data = json.load(response_json)
            contributions_by_repos = data["data"]["viewer"]["contributionsCollection"][
                "commitContributionsByRepository"
            ]
            full_data.extend(contributions_by_repos)
    
    full_contribution_list = []
    for repo_contributions in full_data:
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