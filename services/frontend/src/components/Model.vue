<template>
<div :hidden="!visible">
    <div class="code-explanation-wrapper">
        <div class="code-container-wrapper">
            <div class="helper_buttons" style="float: right;">
                <div><button class="documentation-button" title="Open documentation" v-on:click="openDocumentation()" :disabled="frameworkItem == null || isDummy">
                    <img class="documentation-button-image" v-bind:src="'src/assets/read-book-icon.png'">
                </button></div>
            </div>
            <div class="code-container">
                <div v-if="showLoading || debug" class="lds-facebook"><div></div><div></div><div></div></div>
                <template v-if="highlighted">
                    <template v-for="resultChunk in resultChunks" :key="resultChunk.content">
                        <template v-if="resultChunk.type == 'code'">
                            <CodeSnippet
                                :codeSnippet="resultChunk.codeSnippet"
                                :clickableNames="resultChunk.clickableNames"
                                @click="codeSnippetClicked"
                            />
                        </template>
                        <template v-else-if="resultChunk.type == 'text'">
                            <pre>{{ resultChunk.content }}</pre>
                        </template>
                        <template v-else-if="resultChunk.type == 'debug'">
                            <CodeSnippet
                                :rawHtml="resultChunk.rawHtml"
                                @click="codeSnippetClicked"
                            />
                        </template>
                    </template>
                </template>
                <template v-else>
                    <pre>{{ generatedText }}</pre>
                </template>
            </div>
        </div>
        <div class="explanation-container-wrapper">
            <div>
                <button @click="explain" :disabled="!generated || isDummy || explainClicked">Explain!</button>
                <button @click="debug_fillExplain()" :hidden="!debug">FILL THIS TOO!</button>
            </div>
            <div class="explanation-container">
                <vue-markdown :source="explanationText" />
            </div>
        </div>
    </div>

    <div class="code-buttons">
        <button v-on:click="debug_fillWithCode(false)" :hidden="!debug">FILL ME!</button>
        <button v-on:click="debug_fillWithCode(true)" :hidden="!debug">FILL ME 2!</button>
        <button v-on:click="tooLong()" :disabled="!generated || isDummy">Too long</button>
        <button v-on:click="tooShort()" :disabled="!generated || isDummy">Too short</button>
        <button class="generate-next-example" v-on:click="generateNextExample()" :disabled="!generated || isDummy" v-if="selectedCodeFrameworkItem != null">Generate example for {{ selectedCodeFrameworkItem.name }}</button>
    </div>

</div>
</template>

<script>
import CodeSnippet from '@/components/CodeSnippet.vue';
import VueMarkdown from 'vue-markdown-render';
import { db } from "@/util/dbInterface.js";
import { debug } from "@/util/debug.js";
import { llm } from "@/util/llm.js";
import { codeAnalyzer } from "@/util/codeAnalyzer.js";

export default {
    name: "Model",
    components: {
        CodeSnippet,
        VueMarkdown
    },
    props: {
        model: String,
        frameworkItem: Object,
        visible: Boolean,
        allFrameworkItems: Array,
        isDummy: Boolean,
        debug: Boolean,
    },
    data() {
        return {
            generatedText: "",
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

            stopSequences: [],

            showLoading: false
        }
    },
    mounted() {
        db.getAll("stop_sequences")
        .then((responseJson) => {
            this.stopSequences = responseJson.map((stopSequence) => stopSequence.id);
        })
    },
    methods: {
        tooLong() {
            this.generated = false;
            this.highlighted = false;
            this.resultChunks = [];
            this.explanationText = "";
            this.explainClicked = false;
            this.generatedText = "";
            this.generateExample("too_long");
        },
        tooShort() {
            this.generated = false;
            this.highlighted = false;
            this.resultChunks = [];
            this.explanationText = "";
            this.explainClicked = false;
            this.generatedText = "";
            this.generateExample("too_short");
        },
        generateExample(generationReason="example_generation") {
            this.showLoading = true;
            db.getByName("system_prompts", generationReason)
            .then((responseJson) => {
                this.setPromptParts(responseJson.id, generationReason);
            });
        },
        setPromptParts(systemPromptId, generationReason) {
            let promises = [
                db.create("prompt_parts", {
                    text: "\n# Documentation:\n" + this.frameworkItem.description
                }),
                db.create("prompt_parts", {
                    text: "\n# Implementation:\n" + this.frameworkItem.source
                })
            ]
            if (generationReason == "too_short") {
                promises.push(db.create("prompt_parts", {
                    text: "\n# Your last generation:\n" + this.generatedText
                }));
                promises.push(db.create("prompt_parts", {
                    text: "\n# Task:\nWrite a longer code example for this function. Please provide only code."
                }));
            } else if (generationReason == "too_long") {
                promises.push(db.create("prompt_parts", {
                    text: "\n# Your last generation:\n" + this.generatedText
                }));
                promises.push(db.create("prompt_parts", {
                    text: "\n# Task:\nWrite a shorter code example for this function. Please provide only code."
                }));
            } else {
                promises.push(db.create("prompt_parts", {
                    text: "\n# Task:\nWrite a helpful code example for this function. Please provide only code."
                }));
            }
            Promise.all(promises)
            .then((responseJson) => {
                const promptPartIds = responseJson.map(data => data.id);
                this.getLlmId(systemPromptId, promptPartIds, generationReason)
            });
        },

        getLlmId(systemPromptId, promptPartIds, generationReason) {
            db.getByName("llms", this.model)
            .then((responseJson) => {
                if (generationReason == "example_generation") {
                    this.generatePrediction(systemPromptId, promptPartIds, responseJson.id, null);
                } else {
                    this.getUserRatingType(systemPromptId, promptPartIds, responseJson.id, generationReason);
                }
            });
        },

        getUserRatingType(systemPromptId, promptPartIds, llmId, generationReason) {
            db.getByName("user_rating_types", generationReason)
            .then((responseJson) => {
                this.generateUserRating(systemPromptId, promptPartIds, llmId, responseJson.id, generationReason);
            });
        },

        generateUserRating(systemPromptId, promptPartIds, llmId, userRatingTypeId, generationReason) {
            db.create("user_ratings", {
                value: 0.0,
                prediction: this.generatedPrediction.id,
                user_rating_type: userRatingTypeId
            })
            .then((responseJson) => {
                this.getFollowUpType(systemPromptId, promptPartIds, llmId, generationReason);
            });
        },

        getFollowUpType(systemPromptId, promptPartIds, llmId, generationReason) {
            db.getByName("follow_up_types", generationReason)
            .then((responseJson) => {
                this.generateFollowUp(systemPromptId, promptPartIds, llmId, responseJson.id);
            });
        },

        generateFollowUp(systemPromptId, promptPartIds, llmId, followUpTypeId) {
            db.create(
                "follow_ups",
                {
                    parent_prediction: this.generatedPrediction.id,
                    follow_up_type: followUpTypeId
                }
            )
            .then((responseJson) => {
                    this.generatePrediction(systemPromptId, promptPartIds, llmId, responseJson.id);
            });
        },

        generatePrediction(systemPromptId, promptPartIds, llmId, followUpId) {
            this.codeFrameworkItems = [];
            this.selectedCodeFrameworkItem = null;

            llm.generate(
                llmId,
                promptPartIds,
                systemPromptId,
                {
                    frameworkItem: this.frameworkItem.id,
                    maxTokens: this.max_tokens,
                    temperature: this.temperature,
                    parentFollowUpId: followUpId
                },
                this.stream,
                (responseJson) => {
                    this.displayPrediction(responseJson.prediction);
                    this.showLoading = false;
                },
                (event) => {
                    this.showLoading = false;
                    const token = JSON.parse(event.data).token;
                    this.generatedText += token;
                },
                (event) => {
                    const predictionId = JSON.parse(event.data).prediction;
                    this.displayPrediction(predictionId);
                }
            );
        },

        displayPrediction(predictionId) {
            db.getById("predictions", predictionId)
            .then((responseJson) => {
                this.generatedPrediction = responseJson;
                this.generatedText = this.generatedPrediction.text;

                this.highlightCode();
                this.generated = true;
            });
        },

        debug_fillExplain() {
            this.explanationText = debug.explanationText;
        },

        debug_fillWithCode(long) {
            const rawHtml = debug.codeSnippetHtml;

            this.resultChunks = []
            if (long) {
                this.resultChunks.push({
                    type: "text",
                    content: debug.prefixWrapperText
                });
            }
            this.resultChunks.push({
                type: "debug",
                content: "",
                rawHtml: rawHtml
            });
            if (long) {
                this.resultChunks.push({
                    type: "text",
                    content: debug.suffixWrapperText
                });
            }

            this.highlighted = true;
        },

        highlightCode() {
            codeAnalyzer.analyze(this.generatedPrediction.id)
            .then((responseJson) => {
                const codeSnippetIds = responseJson.code_snippets;
                let promises = [];
                for (const codeSnippetId of codeSnippetIds) {
                    promises.push(db.getById("code_snippets", codeSnippetId));
                }
                Promise.all(promises)
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
                    });
            })
            .catch((error) => {
                console.log(error);
            });
        },

        explain() {
            this.explainClicked = true;
            db.create("prompt_parts", {
                text: "Please explain this code step by step formatted as markdown:\n\n```python\n" + this.generatedText + "\n```"
            })
            .then((responseJson) => {
                const promptPartIds = [responseJson.id];
                db.getByName("llms", this.explanationModel)
                .then((responseJson) => {
                    const llmId = responseJson.id;
                    llm.generate(
                        llmId,
                        promptPartIds,
                        this.frameworkItem.id,
                        {
                            maxTokens: this.max_tokens,
                            temperature: this.temperature
                        },
                        this.stream,
                        (responseJson) => {
                            this.displayExplanation(responseJson.prediction);
                        },
                        (event) => {
                            const token = JSON.parse(event.data).token;
                            this.explanationText += token;
                        },
                        (event) => {
                            const predictionId = JSON.parse(event.data).prediction;
                            this.displayExplanation(predictionId);
                        }
                    );
                });
            })
        },

        displayExplanation(predictionId) {
            db.getById("predictions", predictionId)
            .then((responseJson) => {
                const explanationText = responseJson.text;
                explanationText.replace("\n\n", "\n");
                this.explanationText = explanationText;
            });
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
        }
    },
    computed: {
        clickableNames()  {
            let frameworkItems = this.allFrameworkItems.filter(
                (item) => item.framework.id == this.frameworkItem.framework.id && item.name != this.frameworkItem.name
            );
            return frameworkItems.map(
                (item) => item.name.split('.').reverse()[0]
            );
        }
    }
}
</script>
