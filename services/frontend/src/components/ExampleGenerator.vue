<style scoped>
    .container {
    max-width: 500px;
    margin: 30px 0 30px;
    overflow: auto;
    min-height: 300px;
    border: 1px solid steelblue;
    padding: 30px;
    border-radius: 5px;
    background-color: black;
    color:white;
    font-family:'Courier New', Courier, monospace;
    }
</style>

<template>
<div>
    <div class="radio-container">
        <template v-for="model in models" :key="model">
        <input type="radio" :id="model" :value="model" v-on:click="selectionChanged(model)" name="model_selection" v-model="selectedModel">
        <label :for="model">{{ model.split(":")[0] }}</label>
    </template>
    <template v-for="model in disabled_models" :key="model">
        <input type="radio" :id="model" :value="model" v-on:click="selectionChanged(model)" name="model_selection" disabled>
        <label :for="model">{{ model.split(":")[0] }}</label>
    </template>
    </div>
    <div class="container">
        <p>{{ generatedText }}</p>
    </div>
    <button v-on:click="generateExample()">Generate Example!</button>
</div>
</template>

<script>
export default {
    name: "ExampleGenerator",
    data() {
        return {
            models: ["codellama:7b-instruct", "wizardcoder:13b-python"],
            disabled_models: ["GPT-3.5", "GPT-4"],
            selectedModel: "codellama:7b-instruct",
            generatedText: "Generated example will appear here.",

            frameworkItem: null,

            generatedPredictions: []
        }
    },
    methods: {
        selectionChanged(model) {
            const index = this.models.indexOf(model);
            this.generatedText = this.generatedPredictions[index].text;
        },
        frameworkItemChanged(frameworkItem) {
            this.frameworkItem = frameworkItem;
        },
        generateExample() {
            fetch("http://localhost:5003/system_prompts/by-name/example_generation")
            .then((response) => response.json())
            .then((responseJson) => {
                this.setPromptParts(responseJson.id);
            })
            .catch((error) => {
                console.log(error);
            })
        },
        setPromptParts(systemPromptId) {
            Promise.all([
                fetch("http://localhost:5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "# Documentation:\n" + this.frameworkItem.description
                    })
                }),
                fetch("http://localhost:5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "# Implementation:\n" + this.frameworkItem.source
                    })
                }),
                fetch("http://localhost:5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "# Task:\nWrite a helpful code example for this function. Please provide only code."
                    })
                })
            ])
            .then((responses) => Promise.all(responses.map(response => response.json())))
            .then((responseJson) => {
                const promptPartIds = responseJson.map(data => data.id);
                this.getLlmIds(systemPromptId, promptPartIds)
            })
        },
        getLlmIds(systemPromptId, promptPartIds) {
            let promises = [];
            for (const model of this.models) {
                promises.push(fetch("http://localhost:5003/llms/by-name/" + model));
            }
            Promise.all(promises)
            .then((responses) => Promise.all(responses.map(response => response.json())))
            .then((responseJson) => {
                const llmIds = responseJson.map(data => data.id);
                this.generatePredictions(systemPromptId, promptPartIds, llmIds);
            });
        },
        generatePredictions(systemPromptId, promptPartIds, llmIds) {
            let promises = [];
            for (const llmId of llmIds) {
                promises.push(fetch(
                    "http://localhost:5001/generate"
                    + "?model=" + llmId
                    + "&prompt_parts=" + promptPartIds.toString()
                    + "&system_prompt=" + systemPromptId
                    + "&framework_item=" + this.frameworkItem.id
                    + "&stream=false"
                ));
            }
            Promise.all(promises)
            .then((responses) => Promise.all(responses.map(response => response.json())))
            .then((responseJson) => {
                console.log(responseJson);
                const predictionIds = responseJson.map(data => data.prediction);
                this.displayPredictions(predictionIds);
            });
        },
        displayPredictions(predictionIds) {
            let promises = [];
            for (const predictionId of predictionIds) {
                promises.push(fetch("http://localhost:5003/predictions/" + predictionId));
            }
            Promise.all(promises)
            .then((responses) => Promise.all(responses.map(response => response.json())))
            .then((responseJson) => {
                this.generatedPredictions = responseJson;
            });
        }

    }
}
</script>
