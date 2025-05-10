from pathlib import Path
import pandas as pd
import requests
import logging

from yd_extractor.utils.pandas import convert_columns_to_numeric, validate_columns

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
                commitCount: int
                occurredAt: str
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
            "commitCount": node["commitCount"],
            "occurredAt": node["occurredAt"],
            "repository_name": node["repository"][
                "name"
            ],  # these should all be the same :p
            "repository_url": node["repository"]["url"],
            "repository_image": node["repository"]["openGraphImageUrl"],
        }
        for node in node_list
    ]
    return node_list

#TODO make year a parameter!!
def extract_repo_contributions(
    github_token: str,
    year: int
) -> pd.DataFrame:
    
    if year < 2005:
        raise Exception("Can't load contributions from before 2005!")
    
    # Load query from seperate file
    query = None
    path_to_query = (
        Path(__file__).parent / 
        "graphql" /
        "GetUserRepoContributions.graphql"
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
        verify=False
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

    df_raw = pd.DataFrame(full_contribution_list)
    return df_raw

def transform_repo_contributions(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(
        df,
        [
            "commitCount",
            "occurredAt",
            "repository_name",
            "repository_url",
            "repository_image",
        ],
    )
    df = df.rename(
        columns={
            "commitCount": "total_commits", 
            "occurredAt": "date"
        }
    )
    df["date"] = pd.to_datetime(df["date"], format="ISO8601").dt.date
    df = convert_columns_to_numeric(df, columns=["total_commits"])
    
    return df


def process_repo_contributions(
    github_token: str,
    year=2025
) -> pd.DataFrame:
    logger.info("Processing github repo contirbutions...")
    df_raw = extract_repo_contributions(github_token, year)
    df_transformed = transform_repo_contributions(df_raw)
    logger.info("Finished processing github repo contributions.")
    return df_transformed