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
        <div class="explainer">
            <div>
                <button @click="explain" :disabled="!generated || isDummy || explainClicked">Explain!</button>
                <button @click="debug_fillExplain()">FILL THIS TOO!</button>
            </div>
            <div class="container_explain">
                <div>{{ explanationText }}</div>
            </div>
        </div>
    </div>

    <div class="codebuttons">
        <button v-on:click="debug_fillWithCode(false)">FILL ME!</button>
        <button v-on:click="debug_fillWithCode(true)">FILL ME 2!</button>
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

        debug_fillExplain() {
            this.explanationText = `Eine Aufzählung:\n
1. Erstens\n
2. Zweitens\n
3. Drittens\n
\n
Und ein Lorem Ipsum:\n
\n
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\n
incididunt ut labore et dolore magna aliqua. Magna fermentum iaculis eu non diam\n
phasellus vestibulum lorem. Varius vel pharetra vel turpis nunc eget.\n
Condimentum vitae sapien pellentesque habitant morbi tristique senectus et.\n
Lobortis elementum nibh tellus molestie nunc non. Lacus vestibulum sed arcu\n
non odio euismod lacinia at. Lacus luctus accumsan tortor posuere. A pellentesque\n
sit amet porttitor eget dolor morbi. Enim lobortis scelerisque fermentum dui\n
faucibus. Iaculis nunc sed augue lacus viverra vitae congue eu consequat. Sed\n
egestas egestas fringilla phasellus faucibus scelerisque. Aliquet sagittis id\n
consectetur purus ut faucibus pulvinar elementum integer. Nec tincidunt praesent\n
semper feugiat nibh sed pulvinar. Porttitor leo a diam sollicitudin. Velit\n
euismod in pellentesque massa placerat. Ut venenatis tellus in metus vulputate\n
eu. Dui id ornare arcu odio ut. Massa sapien faucibus et molestie ac feugiat.\n
\n
Cursus mattis molestie a iaculis. Volutpat sed cras ornare arcu dui vivamus\n
arcu. In massa tempor nec feugiat nisl pretium fusce id velit. Turpis massa\n
tincidunt dui ut ornare lectus. Consectetur purus ut faucibus pulvinar elementum\n
integer enim. Vitae congue eu consequat ac felis donec et odio pellentesque.\n
Sit amet cursus sit amet dictum sit amet justo donec. Magna fermentum iaculis\n
eu non. Elit eget gravida cum sociis natoque penatibus. Lectus urna duis\n
convallis convallis. Lorem dolor sed viverra ipsum nunc aliquet. Sed blandit\n
libero volutpat sed cras.\n
\n
Habitasse platea dictumst quisque sagittis. Aliquam vestibulum morbi blandit\n
cursus. Venenatis a condimentum vitae sapien pellentesque. Pharetra diam sit\n
amet nisl suscipit. Auctor neque vitae tempus quam pellentesque. Sed risus\n
pretium quam vulputate dignissim suspendisse in est. Lectus nulla at volutpat\n
diam ut. Sed augue lacus viverra vitae congue. Adipiscing elit pellentesque\n
habitant morbi tristique senectus et. Id nibh tortor id aliquet lectus proin\n
nibh nisl condimentum. Aenean et tortor at risus viverra adipiscing at in\n
tellus. Ut ornare lectus sit amet est placerat in egestas erat. Massa tincidunt\n
nunc pulvinar sapien et ligula ullamcorper malesuada proin. Cras semper auctor\n
neque vitae tempus quam pellentesque. Ac feugiat sed lectus vestibulum mattis\n
ullamcorper velit sed. Commodo odio aenean sed adipiscing diam donec adipiscing\n
tristique risus.\n
\n
Enim nulla aliquet porttitor lacus. Rhoncus est pellentesque elit ullamcorper\n
dignissim cras tincidunt lobortis. Lacus vestibulum sed arcu non odio euismod\n
lacinia. Eget nulla facilisi etiam dignissim. A cras semper auctor neque vitae\n
tempus quam pellentesque nec. Vitae tortor condimentum lacinia quis vel eros\n
donec ac odio. Diam vulputate ut pharetra sit amet aliquam id. Praesent\n
elementum facilisis leo vel. Aliquam nulla facilisi cras fermentum odio eu\n
feugiat pretium. Posuere urna nec tincidunt praesent semper feugiat. Condimentum\n
lacinia quis vel eros donec ac odio tempor orci. Semper viverra nam libero\n
justo laoreet sit amet. Pellentesque habitant morbi tristique senectus et.\n
\n
Dictum at tempor commodo ullamcorper a lacus vestibulum sed arcu. Sed lectus\n
vestibulum mattis ullamcorper. Id consectetur purus ut faucibus pulvinar\n
elementum integer. At augue eget arcu dictum varius. Tristique risus nec\n
feugiat in fermentum posuere urna nec tincidunt. Quis hendrerit dolor magna\n
eget est. Amet tellus cras adipiscing enim. In nisl nisi scelerisque eu.\n
Porttitor leo a diam sollicitudin tempor id eu nisl nunc. Cras fermentum odio\n
eu feugiat pretium.\n
`;
        },

        debug_fillWithCode(long) {
            const rawHtml = `<div class="highlight"><pre><span></span><span class="kn">from</span> <span class="nn">transformers</span> <span class="kn">import</span> <span class="n">AutoTokenizer</span><span class="p">,</span> <span class="n">BertTokenizerFast</span>
<span class="kn">import</span> <span class="nn">torch</span>

<span class="n">tokenizer</span> <span class="o">=</span> <span class="n">AutoTokenizer</span><span class="o">.</span><span class="n">from_pretrained</span><span class="p">(</span><span class="s2">"bert-base-uncased"</span><span class="p">)</span>
<span class="n">sequences</span> <span class="o">=</span> <span class="p">[</span><span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"This is a test"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">),</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"Another sentence"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">)]</span>
<span class="n">batch_decoded</span> <span class="o">=</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'batch_decode')">batch_decode</a></u></b></span><span class="p">(</span><span class="n">sequences</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="n">batch_decoded</span><span class="p">)</span> <span class="c1"># Output: ['this is a test', 'another sentence']</span>

<span class="c1"># Convert the sequences to tensors and pass them through the model</span>
<span class="n">input_ids</span> <span class="o">=</span> <span class="n">torch</span><span class="o">.</span><span class="n">tensor</span><span class="p">([</span><span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"This is a test"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">),</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"Another sentence"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">)])</span>
<span class="n">outputs</span> <span class="o">=</span> <span class="n">model</span><span class="p">(</span><span class="n">input_ids</span><span class="p">)</span>
<span class="c1"># Use the 'batch_decode' method to decode the output ids</span>
<span class="n">decoded_sequences</span> <span class="o">=</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'batch_decode')">batch_decode</a></u></b></span><span class="p">(</span><span class="n">outputs</span><span class="p">[</span><span class="mi">0</span><span class="p">],</span> <span class="n">skip_special_tokens</span><span class="o">=</span><span class="kc">True</span><span class="p">,</span> <span class="n">clean_up_tokenization_spaces</span><span class="o">=</span><span class="kc">False</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="n">decoded_sequences</span><span class="p">)</span> <span class="c1"># Output: ['this is a test', 'another sentence']</span>
</pre></div>
            `

            this.resultChunks = []
            if (long) {
                this.resultChunks.push({
                    type: "text",
                    content: "This is some text."
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
                    content:
                        "This is some more text that is a bit longer and has more lines.\n"
                        + "Once upon a time there was a very long text with multiple lines that was so long that it was too long.\n"
                        + "This is some more text that is a bit longer and has more lines.\n"

                });
            }

            this.highlighted = true;
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
