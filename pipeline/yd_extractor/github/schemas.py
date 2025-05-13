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
    date: Series[pa.Date] = pa.Field()
    total_commits: Series[int] = pa.Field()
    repository_name: Series[str] = pa.Field()
    repository_url: Series[str] = pa.Field()
    repository_image: Series[str] = pa.Field()
