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

## 2026-01-11 React visx dependency error.

Error:
```
npm error code ERESOLVE
npm error ERESOLVE unable to resolve dependency tree
npm error
npm error While resolving: year-in-data@4.0.0
npm error Found: react@19.2.3
npm error node_modules/react
npm error   react@"^19.2.0" from the root project
npm error
npm error Could not resolve dependency:
npm error peer react@"^16.8.0-0 || ^17.0.0-0 || ^18.0.0-0" from @visx/tooltip@3.12.0
npm error node_modules/@visx/tooltip
npm error   @visx/tooltip@"*" from the root project
npm error
npm error Fix the upstream dependency conflict, or retry
npm error this command with --force or --legacy-peer-deps
npm error to accept an incorrect (and potentially broken) dependency resolution.
npm error
npm error
```

Fix:
* Downgraded to react 18.