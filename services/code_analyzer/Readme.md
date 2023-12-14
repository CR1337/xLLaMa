# Code Analyzer

This extracts code snippets from predictions stored in the database and analyzes them. The results are stored in the database.

## Endpoints

### `GET /`
This endpoint only exists for debugging purposes. It doesn't take any further parameters and always returns
```json
{"message": "Hello, world!\n This is 'code_analyzer'."}
```

### `GET /analyze-prediction`
This endpoint takes a `prediction` parameter (see below), which is the id of a prediction stored in the database.
```
/analyze-prediction?prediction=PREDICTION_ID
```
It then extracts the code snippets from the prediction and analyzes them. The results are stored in the database. The endpoint returns
```json
{"code_snippets": [...]}
```
The list contains the ids of the code snippets now stored in the database. How to retrieve the results and a description of them can be found in the [db_interface Readme](../db_interface/Readme.md).
