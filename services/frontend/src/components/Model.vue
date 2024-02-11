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
import { prompts } from "@/util/prompts.js";

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

            showLoading: false,

            llm: null
        }
    },
    mounted() {
        db.getAll("stop_sequences")
        .then((responseJson) => {
            this.stopSequences = responseJson.map((stopSequence) => stopSequence.id);
        })
        db.getByName("llms", this.model)
        .then((responseJson) => {
            this.llm = responseJson;
        })
    },
    methods: {
        tooLong() {
            this.generateAfterUserFeedback(true, false, "too_long");
        },

        tooShort() {
            this.generateAfterUserFeedback(false, true, "too_short");
        },

        generateAfterUserFeedback(tooLong, tooShort, generationReason) {
            const promises = [
                this.prepareGeneration(tooLong, tooShort),
                this.createFollowUp(generationReason)
            ]
            Promise.all(promises)
            .then((resolvedPromises) => {
                const generationPreparationData = resolvedPromises[0];
                const followUpId = resolvedPromises[1];
                this.generate(
                    generationPreparationData.systemPromptId,
                    generationPreparationData.promptPartIds,
                    followUpId
                )
            })
        },

        generateExample() {
            this.prepareGeneration(false, false)
            .then((data) => {
                this.generate(
                    data.systemPromptId,
                    data.promptPartIds,
                    null
                );
            });
        },

        reset() {
            this.generatedText = "";
            this.generated = false;
            this.highlighted = false;
            this.resultChunks = [];
            this.codeFrameworkItems = [];
            this.selectedCodeFrameworkItem = null;
            this.explanationText = "";
            this.explainClicked = false;
        },

        prepareGeneration(tooLong, tooShort) {
            this.reset()
            this.showLoading = true;

            const generationReason = (tooLong)
                ? "too_long"
                : (tooShort)
                    ? "too_short"
                    : "example_generation";

            return db.getByName("system_prompts", generationReason)
            .then((responseJson) => { return responseJson.id; })
            .then((systemPromptId) => {
                let promises = [
                    db.create("prompt_parts", {
                        text: "\n# Documentation:\n" + this.frameworkItem.description
                    }),
                    db.create("prompt_parts", {
                        text: "\n# Implementation:\n" + this.frameworkItem.source
                    })
                ];
                if (generationReason == "too_short") {
                    promises.push(db.create("prompt_parts", {
                        text: prompts.tooShortOrLongPrefix + this.generatedText
                    }));
                    promises.push(db.create("prompt_parts", {
                        text: prompts.tooShortTask
                    }));
                } else if (generationReason == "too_long") {
                    promises.push(db.create("prompt_parts", {
                        text: prompts.tooShortOrLongPrefix + this.generatedText
                    }));
                    promises.push(db.create("prompt_parts", {
                        text: prompts.tooLongTask
                    }));
                } else {
                    promises.push(db.create("prompt_parts", {
                        text: prompts.exampleGenerationTask
                    }));
                }
                return Promise.all(promises)
                .then((resolvedPromises) => {
                    const promptPartIds = resolvedPromises.map(x => x.id);
                    return {
                        systemPromptId: systemPromptId,
                        promptPartIds: promptPartIds
                    };
                })
            });
        },

        createFollowUp(generationReason) {
            db.getByName("user_rating_type", generationReason)
            .then((responseJson) => {
                return db.create("user_ratings", {
                    value: 0.0,
                    prediction: this.generatedPrediction.id,
                    user_rating_type: responseJson.id
                });
            })
            .then((responseJson) => {
                return db.getByName("follow_up_types", generationReason);
            })
            .then((responseJson) => {
                return db.create("follow_ups", {
                    parent_prediction: this.generatedPrediction.id,
                    follow_up_type: responseJson.id
                });
            })
        },

        generate(systemPromptId, promptPartIds, followUpId) {
            this.generatedPrediction = null;
            llm.generate(
                this.llm.id,
                promptPartIds,
                this.frameworkItem.id,
                {
                    maxTokens: this.max_tokens,
                    temperature: this.temperature,
                    parentFollowUpId: followUpId,
                    systemPromptId: systemPromptId
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

        explain() {
            this.explainClicked = true;
            db.create("prompt_parts", {
                text:prompts.explanationTask + this.generatedText + prompts.explanationTaskSuffix
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
