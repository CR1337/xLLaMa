<style>
</style>

<template>
<div :hidden="!visible">
    <div class="container">
        <pre><code class="language-python">{{ generatedText }}</code></pre>
    </div>
    <div>
        <button v-on:click="tooLong()" :disabled="!generated">Too long</button>
        <button v-on:click="tooShort()" :disabled="!generated">Too short</button>
        <button v-on:click="openDocumentation()" :disabled="frameworkItem == null">Documentation</button>
        <button v-on:click="generateNextExample()" :disabled="!generated || selectedCodeObject == null">New example for {{ (selectedCodeObject == null) ? '________' : selectedCodeObject.name }}</button>
    </div>

</div>
</template>

<script>
import Prism from 'prismjs';
import 'prismjs/themes/prism.css';
import 'prismjs/components/prism-python';
export default {
    name: "Model",
    props: {
        model: String,
        frameworkItem: Object,
        visible: Boolean
    },
    data() {
        return {
            generatedText: "Generated code by " + this.model + " will apear here.",
            generatedPrediction: null,
            generated: false,

            selectedCodeObject: null,

            stream: true  // This is a constant to dis/enable streaming
        }
    },
    methods: {
        tooLong() {
            console.log("function: tooLong()");
            this.generateExample("too_long");
        },
        tooShort() {
            console.log("function: tooShort()");
            this.generateExample("too_short");
        },
        generateExample(generationReason="example_generation") {
            console.log("function: generateExample(" + generationReason + ")");
            console.log("Generation started for " + this.model);
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
            console.log("function: setPromptParts(" + systemPromptId + ", " + generationReason + ")");
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
            console.log("function: getLlmId(" + systemPromptId + ", " + promptPartIds + ", " + generationReason + ")");
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
            console.log("function: getUserRatingType(" + systemPromptId + ", " + promptPartIds + ", " + llmId + ", " + generationReason + ")");
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
            console.log("function: generateUserRating(" + systemPromptId + ", " + promptPartIds + ", " + llmId + ", " + userRatingTypeId + ", " + generationReason + ")");
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
            console.log("function: getFollowUpType(" + systemPromptId + ", " + promptPartIds + ", " + llmId + ", " + generationReason + ")");
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
            console.log("function: generateFollowUp(" + systemPromptId + ", " + promptPartIds + ", " + llmId + ", " + followUpTypeId + ")");
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
            console.log("function: generatePrediction(" + systemPromptId + ", " + promptPartIds + ", " + llmId + ", " + followUpId + ")");
            let url = "http://" + this.host + ":5001/generate"
                + "?model=" + llmId
                + "&prompt_parts=" + promptPartIds.toString()
                + "&system_prompt=" + systemPromptId
                + "&framework_item=" + this.frameworkItem.id
            if (followUpId != null) {
                url += "&parent_follow_up=" + followUpId;
            }
            if (!this.stream) {
                console.log("NO STREAM");
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
                console.log("STREAM");
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
            console.log("function: displayPrediction(" + predictionId + ")");
            fetch("http://" + this.host + ":5003/predictions/" + predictionId)
            .then((response) => response.json())
            .then((responseJson) => {
                this.generatedPrediction = responseJson;
                this.generatedText = this.generatedPrediction.text;

                this.$nextTick(() => {
                    Prism.highlightAll();
                });


                this.generated = true;
            })
            .catch((error) => {
                console.log(error);
            })
        },

        openDocumentation() {
            window.open(this.frameworkItem.url, "_blank");
        },

        generateNextExample() {
            alert("Not implemented yet!"); // TODO
        }
    },
    computed: {
        host() { return window.location.origin.split("/")[2].split(":")[0]; }
    }
}
</script>
