<style>
.container pre {
    background-color: white;
    margin: 0px 0px 0px
}
</style>

<template>
<div :hidden="!visible">
    <div class="wrapper">
        <div class="coder">
            <div class="helper_buttons" style="float: right;">
                <div><button class="copy" title="Copy to clipboard" v-on:click="copyToClipboard()" :disabled="!generated || isDummy">
                    <img class="copyimg" v-bind:src="'src/assets/copy-icon.png'">
                </button></div>
                <div><button class="documentation" title="Open documentation" v-on:click="openDocumentation()" :disabled="frameworkItem == null || isDummy">
                    <img class="clipboardimg" v-bind:src="'src/assets/read-book-icon.png'">
                </button></div>
            </div>
            <div class="container">
                <pre><code class="language-python">{{ generatedText }}</code></pre>
            </div>
        </div>
        <div class="explainer">
            <div>
                <button @click="explain" :disabled="!generated || isDummy || explainClicked">Explain!</button>
            </div>
            <div class="container_explain">
                <div>{{ explanationText }}</div>
            </div>
        </div>
    </div>

    <div class="codebuttons">
        <button v-on:click="tooLong()" :disabled="!generated || isDummy">Too long</button>
        <button v-on:click="tooShort()" :disabled="!generated || isDummy">Too short</button>
        <!-- TODO: imporove disabled -->
        <AutoComplete
            v-model="selectedCodeFrameworkItem"
            :suggestions="suggestedCodeFrameworkItem"
            @complete="updateSuggestedCodeFrameworkItems"
            optionLabel="name"
            force-selection
            dropdown
            :disabled="isDummy"
        />
        <!-- TODO: check generated for disabled -->
        <button v-on:click="generateNextExample()" :disabled="selectedCodeFrameworkItem == null || isDummy">Generate next</button>
    </div>

</div>
</template>

<script>
import Prism from 'prismjs';
import 'prismjs/themes/prism.css';
import 'prismjs/components/prism-python';
import AutoComplete from 'primevue/autocomplete';

export default {
    name: "Model",
    components: {
        AutoComplete
    },
    props: {
        model: String,
        frameworkItem: Object,
        visible: Boolean,
        allFrameworkItems: Array,
        isDummy: Boolean
    },
    data() {
        return {
            generatedText: "Generated code by " + this.model + " will apear here.",
            generatedPrediction: null,
            generated: false,

            codeFrameworkItems: [],
            selectedCodeFrameworkItem: null,
            suggestedCodeFrameworkItem: [],

            explanationText: "",
            explanationModel: "codellama:7b-instruct",
            explainClicked: false,

            stream: true,  // This is a constant to dis/enable streaming
            max_tokens: 1024,
            temperature: 0.0
        }
    },
    methods: {
        tooLong() {
            this.generateExample("too_long");
        },
        tooShort() {
            this.generateExample("too_short");
        },
        generateExample(generationReason="example_generation") {
            fetch("http://" + this.host + ":5003/system_prompts/by-name/" + generationReason)
            .then((response) => response.json())
            .then((responseJson) => {
                this.setPromptParts(responseJson.id, generationReason);
            })
            .catch((error) => {
                console.log(error);
            });
        },
        setPromptParts(systemPromptId, generationReason) {
            let promises = [
                fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Documentation:\n" + this.frameworkItem.description
                    })
                }),
                fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Implementation:\n" + this.frameworkItem.source
                    })
                })
            ]
            if (generationReason == "too_short") {
                promises.push(fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Your last generation:\n" + this.generatedText
                    })
                }));
                promises.push(fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Task:\nWrite a longer code example for this function. Please provide only code."
                    })
                }));
            } else if (generationReason == "too_long") {
                promises.push(fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Your last generation:\n" + this.generatedText
                    })
                }));
                promises.push(fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Task:\nWrite a shorter code example for this function. Please provide only code."
                    })
                }));
            } else {
                promises.push(fetch("http://" + this.host + ":5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Task:\nWrite a helpful code example for this function. Please provide only code."
                    })
                }));
            }
            Promise.all(promises)
            .then((responses) => Promise.all(responses.map(response => response.json())))
            .then((responseJson) => {
                const promptPartIds = responseJson.map(data => data.id);
                this.getLlmId(systemPromptId, promptPartIds, generationReason)
            })
            .catch((error) => {
                console.log(error);
            });
        },

        getLlmId(systemPromptId, promptPartIds, generationReason) {
            fetch("http://" + this.host + ":5003/llms/by-name/" + this.model)
            .then((response) => response.json())
            .then((responseJson) => {
                if (generationReason == "example_generation") {
                    this.generatePrediction(systemPromptId, promptPartIds, responseJson.id, null);
                } else {
                    this.getUserRatingType(systemPromptId, promptPartIds, responseJson.id, generationReason);
                }
            })
            .catch((error) => {
                console.log(error);
            })
        },

        getUserRatingType(systemPromptId, promptPartIds, llmId, generationReason) {
            fetch("http://" + this.host + ":5003/user_rating_types/by-name/" + generationReason)
            .then((response) => response.json())
            .then((responseJson) => {
                this.getFollowUpType(systemPromptId, promptPartIds, llmId, responseJson.id, generationReason);
            })
            .catch((error) => {
                console.log(error);
            })
        },

        generateUserRating(systemPromptId, promptPartIds, llmId, userRatingTypeId, generationReason) {
            fetch("http://" + this.host + ":5003/user_ratings", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    value: 0.0,
                    prediction: this.generatedPrediction.id,
                    user_rating_type: userRatingTypeId
                })
            })
            .then((response) => response.json())
            .then((responseJson) => {
                this.getFollowUpType(systemPromptId, promptPartIds, llmId, generationReason);
            })
            .catch((error) => {
                console.log(error);
            })
        },

        getFollowUpType(systemPromptId, promptPartIds, llmId, generationReason) {
            fetch("http://" + this.host + ":5003/follow_up_types/by-name/" + generationReason)
            .then((response) => response.json())
            .then((responseJson) => {
                this.generateFollowUp(systemPromptId, promptPartIds, llmId, responseJson.id);
            })
            .catch((error) => {
                console.log(error);
            })
            .catch((error) => {
                console.log(error);
            })
        },

        generateFollowUp(systemPromptId, promptPartIds, llmId, followUpTypeId) {
            fetch("http://" + this.host + ":5003/follow_ups", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    parent_prediction: this.generatedPrediction.id,
                    follow_up_type: followUpTypeId
                })
            })
            .then((response) => response.json())
            .then((responseJson) => {
                this.generatePrediction(systemPromptId, promptPartIds, llmId, responseJson.id);
            })
            .catch((error) => {
                console.log(error);
            })
        },

        generatePrediction(systemPromptId, promptPartIds, llmId, followUpId) {
            let url = "http://" + this.host + ":5001/generate"
                + "?model=" + llmId
                + "&prompt_parts=" + promptPartIds.toString()
                + "&system_prompt=" + systemPromptId
                + "&framework_item=" + this.frameworkItem.id
                + "&max_tokens=" + this.max_tokens
                + "&temperature=" + this.temperature;
            if (followUpId != null) {
                url += "&parent_follow_up=" + followUpId;
            }

            this.codeFrameworkItems = [];
            this.selectedCodeFrameworkItem = null;

            if (!this.stream) {
                url += "&stream=false";
                fetch(url)
                .then((response) => response.json())
                .then((responseJson) => {
                    this.displayPrediction(responseJson.prediction);
                })
                .catch((error) => {
                    console.log(error);
                });
            } else {
                this.generatedText = "";
                const eventSource = new EventSource(url);
                eventSource.addEventListener("generation_progress", (event) => {
                    const token = JSON.parse(event.data).token;
                    this.generatedText += token;
                });
                eventSource.addEventListener("generation_success", (event) => {
                    eventSource.close();
                    const predictionId = JSON.parse(event.data).prediction;
                    this.displayPrediction(predictionId);
                });
            }
        },

        displayPrediction(predictionId) {
            fetch("http://" + this.host + ":5003/predictions/" + predictionId)
            .then((response) => response.json())
            .then((responseJson) => {
                this.generatedPrediction = responseJson;
                this.generatedText = this.generatedPrediction.text;

                this.$nextTick(() => {
                    Prism.highlightAll();
                });

                this.getCodeSymbols();
                this.generated = true;
            })
            .catch((error) => {
                console.log(error);
            })
        },

        getCodeSymbols() {
            fetch("http://" + this.host + ":5002/analyze-prediction?prediction=" + this.generatedPrediction.id)
            .then((response) => response.json())
            .then((responseJson) => {
                const codeSnippetIds = responseJson.code_snippets;
                for (const codeSnippetId of codeSnippetIds) {
                    fetch("http://" + this.host + ":5003/code_snippets/" + codeSnippetId)
                    .then((response) => response.json())
                    .then((codeSnippet) => {
                        const symbolDefinitionIds = codeSnippet.symbol_definitions;
                        const undefinedSymbolReferenceIds = codeSnippet.undefined_symbol_references;
                        for (const symbolDefinitionId of symbolDefinitionIds) {
                            fetch("http://" + this.host + ":5003/symbol_definitions/" + symbolDefinitionId)
                            .then((response) => response.json())
                            .then((symbolDefinition) => {
                                const frameworkItem = this.getFrameworkItemForSymbol(symbolDefinition);
                                if (frameworkItem == null) return;
                                if (frameworkItem.framework != this.frameworkItem.framework) return;
                                this.codeFrameworkItems.push(frameworkItem);
                            })
                            .catch((error) => {
                                console.log(error);
                            })
                        }
                        for (const undefinedSymbolReferenceId of undefinedSymbolReferenceIds) {
                            fetch("http://" + this.host + ":5003/undefined_symbol_references/" + undefinedSymbolReferenceId)
                            .then((response) => response.json())
                            .then((undefinedSymbolReference) => {
                                const frameworkItem = this.getFrameworkItemForSymbol(undefinedSymbolReference);
                                if (frameworkItem == null) return;
                                if (frameworkItem.framework != this.frameworkItem.framework) return;
                                this.codeFrameworkItems.push(frameworkItem);
                            })
                            .catch((error) => {
                                console.log(error);
                            })
                        }
                    })
                    .catch((error) => {
                        console.log(error);
                    })
                }
            })
            .catch((error) => {
                console.log(error);
            })

        },

        getFrameworkItemForSymbol(symbol) {
            const symbolName = symbol.symbol.toLowerCase();
            for (const frameworkItem of this.allFrameworkItems) {
                const frameworkItemName = frameworkItem.name.toLowerCase();
                if (frameworkItemName.includes(symbolName)) {
                    return frameworkItem;
                }
            }
            return null;
        },

        explain() {
            this.explainClicked = true;
            fetch("http://" + this.host + ":5003/prompt_parts", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "text": "Please explain this code:\n\n```python\n" + this.generatedText + "\n```"
                })
            })
            .then((response) => response.json())
            .then((responseJson) => {
                const promptPartIds = [responseJson.id];
                fetch("http://" + this.host + ":5003/llms/by-name/" + this.explanationModel)
                .then((response) => response.json())
                .then((responseJson) => {
                    const llmId = responseJson.id;
                    let url = "http://" + this.host + ":5001/generate"
                        + "?model=" + llmId
                        + "&prompt_parts=" + [promptPartIds].toString()
                        + "&framework_item=" + this.frameworkItem.id
                        + "&max_tokens=" + this.max_tokens
                        + "&temperature=" + this.temperature;
                        if (!this.stream) {
                            url += "&stream=false";
                            fetch(url)
                            .then((response) => response.json())
                            .then((responseJson) => {
                                this.displayExplanation(responseJson.prediction);
                            })
                            .catch((error) => {
                                console.log(error);
                            });
                        } else {
                            this.explanationText = "";
                            const eventSource = new EventSource(url);
                            eventSource.addEventListener("generation_progress", (event) => {
                                const token = JSON.parse(event.data).token;
                                this.explanationText += token;
                            });
                            eventSource.addEventListener("generation_success", (event) => {
                                eventSource.close();
                                const predictionId = JSON.parse(event.data).prediction;
                                this.displayExplanation(predictionId);
                            });
                        }
                })
                .catch((error) => {
                    console.log(error);
                })
            })
            .catch((error) => {
                console.log(error);
            });
        },
        displayExplanation(predictionId) {
            fetch("http://" + this.host + ":5003/predictions/" + predictionId)
            .then((response) => response.json())
            .then((responseJson) => {
                this.explanationText = responseJson.text;
            })
            .catch((error) => {
                console.log(error);
            })
        },

        updateSuggestedCodeFrameworkItems(event) {
            // TODO: implement
            // This should return a list of all framework items that were found in generated code

            // TODO: backend needs to find symbols after dots

            console.log(this.allFrameworkItems);
            this.suggestedCodeFrameworkItem = this.allFrameworkItems.map((item) => {
                return item;
            })
        },

        openDocumentation() {
            window.open(this.frameworkItem.url, "_blank");
        },

        generateNextExample() {
            this.$emit("generateFollowUpExample", this.selectedCodeFrameworkItem);
        },

        copyToClipboard() {
            navigator.clipboard.writeText(this.generatedText);
        }
    },
    computed: {
        host() { return window.location.origin.split("/")[2].split(":")[0]; }
    }
}
</script>
