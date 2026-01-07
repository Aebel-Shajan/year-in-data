# Error log

Template:
```
## {date}:  {summary of error}
Error:

Fix:

```

## 2026-01-07 Type error encountered when trying to create polars df

Error:
Tried to put extract/flattened data into a df but i get the error below. This is likely caused by undefined.
```shell
Error: called `Result::unwrap()` on an `Err` value: Error { status: "GenericFailure", reason: "Unsupported Data type" }
    at arrayToJsSeries (file:///Users/aebel/personal-projects/websites/year-in-data/node_modules/nodejs-polars/bin/internals/construction.js:150:46)
    at SeriesConstructor (file:///Users/aebel/personal-projects/websites/year-in-data/node_modules/nodejs-polars/bin/series/index.js:673:55)
    at file:///Users/aebel/personal-projects/websites/year-in-data/node_modules/nodejs-polars/bin/internals/construction.js:217:63
    at Array.map (<anonymous>)
    at arrayToJsDataFrame (file:///Users/aebel/personal-projects/websites/year-in-data/node_modules/nodejs-polars/bin/internals/construction.js:217:27)
    at Object.DataFrameConstructor [as DataFrame] (file:///Users/aebel/personal-projects/websites/year-in-data/node_modules/nodejs-polars/bin/dataframe.js:734:78)
    at <anonymous>:35:4
    at eventLoopTick (ext:core/01_core.js:187:7)
```

Fix:
The error was caused by the column `content_part`
Turns out the `content_parts` column was not a list of strings as expected. Its actually a 
tree structure which can contain strings or objects based on `content_type`. 

I decided on process only `content_parts` which had `content_type="text"`.