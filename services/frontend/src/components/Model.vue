<style>
</style>

<template>
<div :hidden="!visible">
    <div class="container">
        <span>{{ generatedText }}</span>
    </div>
    <div>
        <button v-on:click="tooLong()" :disabled="!generated">Too long</button>
        <button v-on:click="tooShort()" :disabled="!generated">Too short</button>
    </div>

</div>
</template>

<script>
export default {
    name: "Model",
    props: {
        model: String,
        frameworkItem: Object,
        visible: Boolean
    },
    data() {
        return {
            generatedText: "Generated code from " + this.model + " will apear here.",
            generatedPrediction: null,
            generated: false,
            stream: true  // This is a constant to dis/enable streaming
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
            console.log("Generation started for " + this.model);
            fetch("http://localhost:5003/system_prompts/by-name/" + generationReason)
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
                fetch("http://localhost:5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Documentation:\n" + this.frameworkItem.description
                    })
                }),
                fetch("http://localhost:5003/prompt_parts", {
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
                promises.push(fetch("http://localhost:5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Your last generation:\n" + this.generatedText
                    })
                }));
                promises.push(fetch("http://localhost:5003/prompt_parts", {
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
                promises.push(fetch("http://localhost:5003/prompt_parts", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "text": "\n# Your last generation:\n" + this.generatedText
                    })
                }));
                promises.push(fetch("http://localhost:5003/prompt_parts", {
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
                promises.push(fetch("http://localhost:5003/prompt_parts", {
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
            fetch("http://localhost:5003/llms/by-name/" + this.model)
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
            fetch("http://localhost:5003/user_rating_types/by-name/" + generationReason)
            .then((response) => response.json())
            .then((responseJson) => {
                this.getFollowUpType(systemPromptId, promptPartIds, llmId, responseJson.id, generationReason);
            })
            .catch((error) => {
                console.log(error);
            })
        },
        generateUserRating(systemPromptId, promptPartIds, llmId, userRatingTypeId, generationReason) {
            fetch("http://localhost:5003/user_ratings", {
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
            fetch("http://localhost:5003/follow_up_types/by-name/" + generationReason)
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
            fetch("http://localhost:5003/follow_ups", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    parent_prediction: this.generatePrediction.id,
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
            let url = "http://localhost:5001/generate"
                + "?model=" + llmId
                + "&prompt_parts=" + promptPartIds.toString()
                + "&system_prompt=" + systemPromptId
                + "&framework_item=" + this.frameworkItem.id
            if (followUpId != null) {
                url += "&parent_follow_up=" + followUpId;
            }
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
                    const predictionId = JSON.parse(event.data).prediction;
                    this.displayPrediction(predictionId);
                });
            }
        },
        displayPrediction(predictionId) {
            fetch("http://localhost:5003/predictions/" + predictionId)
            .then((response) => response.json())
            .then((responseJson) => {
                this.generatedPrediction = responseJson;
                this.generatedText = this.generatedPrediction.text;
                this.generated = true;
            })
            .catch((error) => {
                console.log(error);
            })
        }
    }
}
</script>
