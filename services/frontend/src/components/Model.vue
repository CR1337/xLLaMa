<style>
</style>

<template>
<div>
    <div>
        <p>{{ generatedText }}</p>
    </div>
    <button v-on:click="generateExample()">Generate Example!</button>
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
        frameworkItem: Object
    },
    data() {
        return {
            generatedText: "Generated code from " + this.model + " will apear here.",
            generatedPrediction: null,
            generated: false
        }
    },
    methods: {
        tooLong() {

        },
        tooShort() {

        },
        generateExample(generationReason="example_generation") {
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
            });
        },
        getLlmId(systemPromptId, promptPartIds, generationReason) {
            fetch("http://localhost:5003/llms/by-name/" + this.model)
            .then((response) => response.json())
            .then((responseJson) => {
                if (generationReason == "example_generation") {
                    this.generatePrediction(systemPromptId, promptPartIds, responseJson.id, generationReason);
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
        getFollowUpType(systemPromptId, promptPartIds, llmId, userRatingTypeId, generationReason) {
            fetch("http://localhost:5003/follow_up_types/by-name/" + generationReason)
            .then((response) => response.json())
            .then((responseJson) => {
                this.generateFollowUp(systemPromptId, promptPartIds, llmId, userRatingTypeId, followUpTypeId, generationReason);
            })
            .catch((error) => {
                console.log(error);
            })
        },
        generateFollowUp(systemPromptId, promptPartIds, llmId, userRatingTypeId, followUpTypeId, generationReason) {
            fetch("http://localhost:5003/follow_ups", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        parent_prediction: this.generatePrediction.id,
                        follow_up_type: responseJson.id
                    })
                });
        },




        generatePrediction(systemPromptId, promptPartIds, llmId, generationReason) {

        }

    }
}
</script>
