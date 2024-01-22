<style>
</style>

<template>
<div :hidden="!visible">
    <div class="wrapper">
        <div class="coder">
            <div class="helper_buttons" style="float: right;">
                <div><button class="documentation" title="Open documentation" v-on:click="openDocumentation()" :disabled="frameworkItem == null || isDummy">
                    <img class="clipboardimg" v-bind:src="'src/assets/read-book-icon.png'">
                </button></div>
            </div>
            <div class="container">
                <template v-if="highlighted">
                    <template v-for="resultChunk in resultChunks" :key="resultChunk.content">
                        <template v-if="resultChunk.type == 'code'">
                            <CodeSnippet
                                :codeSnippet="resultChunk.codeSnippet"
                                :clickableNames="resultChunk.clickableNames"
                                @click="codeSnippetClicked"
                            />
                        </template>
                        <template v-else>
                            <pre>{{ resultChunk.content }}</pre>
                        </template>
                    </template>
                </template>
                <template v-else>
                    <pre>{{ generatedText }}</pre>
                </template>
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
        <button class="generateNextExample" v-on:click="generateNextExample()" :disabled="!generated || isDummy" v-if="selectedCodeFrameworkItem != null">Generate example for {{ selectedCodeFrameworkItem.name }}</button>
    </div>

</div>
</template>

<script>
import CodeSnippet from '@/components/CodeSnippet.vue';

export default {
    name: "Model",
    components: {
        CodeSnippet
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
            highlighted: false,
            resultChunks: [],

            codeFrameworkItems: [],
            selectedCodeFrameworkItem: null,

            explanationText: "",
            explanationModel: "codellama:7b-instruct",
            explainClicked: false,

            stream: true,  // This is a constant to dis/enable streaming
            max_tokens: 1024,
            temperature: 0.0,

            stopSequences: []
        }
    },
    mounted() {
        fetch("http://" + this.host + ":5003/stop_sequences")
        .then((response) => response.json())
        .then((responseJson) => {
            this.stopSequences = responseJson.map((stopSequence) => stopSequence.id);
        })
    },
    methods: {
        tooLong() {
            this.generated = false;
            this.highlighted = false;
            this.resultChunks = [];
            this.generateExample("too_long");
        },
        tooShort() {
            this.generated = false;
            this.highlighted = false;
            this.resultChunks = [];
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
                // + "&stop_sequences=" + this.stopSequences.toString()
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

                this.highlightCode();
                this.generated = true;
            })
            .catch((error) => {
                console.log(error);
            })
        },

        highlightCode() {
            fetch("http://" + this.host + ":5002/analyze-prediction?prediction=" + this.generatedPrediction.id)
            .then((response) => response.json())
            .then((responseJson) => {
                const codeSnippetIds = responseJson.code_snippets;
                let promises = [];
                for (const codeSnippetId of codeSnippetIds) {
                    promises.push(fetch("http://" + this.host + ":5003/code_snippets/" + codeSnippetId));
                }
                Promise.all(promises)
                    .then((responses) => Promise.all(responses.map(response => response.json())))
                    .then((codeSnippets) => {
                        const sortedCodeSnippets = codeSnippets.sort((a, b) => a.start_line - b.start_line);
                        const codeSnippetCount = sortedCodeSnippets.length;
                        const lines = this.generatedPrediction.text.split("\n");
                        const lineCount = lines.length;

                        let resultChunks = [];
                        let currentCodeSnippetIndex = 0;

                        for (let line = 0; line < lineCount; ++line) {
                            if (currentCodeSnippetIndex < codeSnippetCount)  {
                                if (line == sortedCodeSnippets[currentCodeSnippetIndex].start_line) {
                                    resultChunks.push({
                                        type: "code",
                                        codeSnippet: sortedCodeSnippets[currentCodeSnippetIndex],
                                        clickableNames: this.clickableNames
                                    });
                                    line = sortedCodeSnippets[currentCodeSnippetIndex].end_line;
                                    ++currentCodeSnippetIndex;
                                    continue;
                                }
                            }
                            if (lines[line].startsWith("```")) continue;
                            resultChunks.push({
                                type: "text",
                                content: lines[line]
                            });
                        }

                        this.resultChunks = resultChunks;
                        this.highlighted = true;
                    })
                    .catch((error) => {
                        console.log(error);
                    });
            })
            .catch((error) => {
                console.log(error);
            });
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
                    "text": "Please explain this code step by step formatted as markdown:\n\n```python\n" + this.generatedText + "\n```"
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

        codeSnippetClicked(name) {
            console.log(name);
            const frameworkItems = this.allFrameworkItems.filter(
                (item) => item.name.split('.').reverse()[0] == name
            );
            if (frameworkItems.length == 0) return;
            this.selectedCodeFrameworkItem = frameworkItems[0];
            console.log(this.selectedCodeFrameworkItem);
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
        host() { return window.location.origin.split("/")[2].split(":")[0]; },

        clickableNames()  {
            let frameworkItems = this.allFrameworkItems.filter(
                (item) => item.framework.id == this.frameworkItem.framework.id
            );
            return frameworkItems.map(
                (item) => item.name.split('.').reverse()[0]
            );
        }
    }
}
</script>
