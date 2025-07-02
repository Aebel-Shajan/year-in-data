import pandera as pa
from pandera.typing.pandas import Series


class RawGithubRepoContributions(pa.DataFrameModel):
    class Config:
        coerce = True

    commit_count: Series[int] = pa.Field()
    occured_at: Series[pa.DateTime] = pa.Field()
    repository_name: Series[str] = pa.Field()
    repository_url: Series[str] = pa.Field()
    repository_image: Series[str] = pa.Field()


class GithubRepoContributions(pa.DataFrameModel):
    date: Series[pa.Date] = pa.Field(
        metadata={
            "tag": "date_column",
        }
    )
    total_commits: Series[int] = pa.Field(
        metadata={
            "tag": "value_column",
            "units": "commits",
        }
    )
    repository_name: Series[str] = pa.Field(
        metadata={
            "tag": "category_column",
        }
    )
    repository_url: Series[str] = pa.Field(
        metadata={
            "tag": "link_column",
        }
    )
    repository_image: Series[str] = pa.Field(
        metadata={
            "tag": "image_column",
            "category": "repository_name",
        }
    )
