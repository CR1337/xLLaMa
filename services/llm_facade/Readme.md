# LLM Facade

This service provides an abstraction for the Open AI and the Ollama interface. It can
- list installed models
- install new models (will be installed using Ollama)
- uninstall models
- generate predictions

## Endpoints

### `GET /`
This endpoint only exists for debugging purposes. It doesn't take any further parameters and always returns
```json
{"message": "Hello, world! This is 'llm_facade'."}
```

### `GET /models`
The `/models` endpoint returns a list of all models available. It returns a json response like this
```json
{
    "models": [
        "gpt-4",
        "gpt-3.5-turbo",
        "codellama:7b-instruct"
    ]
}
```

### `GET /models/install`
To install models one can call this endpoint. It takes the parameters `model` and `stream` like this:
```
/models/install?model=MODEL_NAME&stream=false
```
where `stream` is optional and defaults to `true`. The specified model `MODEL_NAME` will be installed locally using Ollama.

If `stream` is `false` a json object will be returned after the installation is finished:
```json
{
    "llm": LLM_ID
}
```
where `LLM_ID` is the database id of the installed model.

If `stream` is `true` a event stream will be returned where each event looks like the following:
```
event: model_installation_progress
data: <JSON_DATA>
id: <ID>

```
Here `<ID>` is a continuously increasing integer starting at `0`. `<JSON_OBJECT>` contains information about the progress which is described [here](https://github.com/jmorganca/ollama/blob/main/docs/api.md#response-10).


### `GET /models/uninstall`
To uninstall models one can call this endpoint. It takes the parameter 'model' like this:
```
/models/uninstall?model=MODEL_NAME
```
where `MODEL_NAME` is the name of the model to uninstall. The specified model will be uninstalled locally using Ollama. On success it returns an empty json object. If the model was not installed in the first place it returns a json object like this:
```json
{
    "message": "model not installed"
}
```
with status code `400`.


### `GET /generate`
This endpoint generates a prediction using a prompt and some other parameters using a specified model. One must/can provide the following GET parameters:

|Field|Type|Optional|Default|Description|
|-----|----|--------|-------|-----------|
|`model`|`str`|no||The database id of the model to use for the prediction.|
|`prompt_parts`|`str`|no||A comma separated list of prompt part database ids. The prompt parts will be concatenated and used to prompt the model.|
|`system_prompt`|`str`|yes||The database id of a system prompt to use with the model.|
|`repeat_penalty`|`float`|yes|`1.1`|How strongly to penalize repetitions. A higher value (e.g., 1.5) will penalize repetitions more strongly, while a lower value (e.g., 0.9) will be more lenient.|
|`max_tokens`|`int`|yes|`256`|The maximum amount of tokens to generate.|
|`seed`|`int`|yes|`0`|A random number seed to use for generation. Setting this to a specific number will make the model generate the same text for the same prompt.|
|`temperature`|`float`|yes|`0.8`|Increasing the temperature will make the model answer more creatively.|
|`top_p`|`float`|yes|`0.9`|A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text.|
|`stop_sequences`|`str`|yes||A comma separated list of stop sequence database ids to use as stop sequences for the prediction|
|`framework_item`|`str`|no||The framework item database id for the framework item the predition is for.|
|`parent_follow_up`|`str`|yes||The follow up database id of the parent follow up object in case this prediction is a follow up prediction.|

It also takes the parameter `stream` that is optional and defaults to `true`.

If `stream` is `false`, this endpoint returns a json object like this:
```
{"preditction": PREDICTION_ID}
```
where `PREDICTION_ID` is the database id of the generated prediction.

If `stream` is `true`, an event stream is returned where each event looks like this:
```
event: generation_progress
data: {"token": TOKEN}
id: ID

```
where `TOKEN` is the currently generated token, `ID` is an increasing integer.

The last event of the event stream looks different:
```
event: generation_success
data: {"prediction": PREDICTION_ID}
id: ID

```
where `PREDICTION_ID` is the database id of the generated prediction.
