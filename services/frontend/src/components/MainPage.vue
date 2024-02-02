<template>
<div>
<a class="header-small-image" href="https://hpi.de/studium/im-studium/lehrveranstaltungen/it-systems-engineering-ma/lehrveranstaltung/wise-23-24-3872-future-of-programming.html" target="_blank">
<img
    src="https://hpi.de/favicon.ico"
    alt="Future of Programming"
    width="16"
    height="16"
/>
</a>
<a class="header-small-image" href="https://github.com/CR1337/xLLaMa" target="_blank">
    <img
        src="https://github.githubassets.com/favicon.ico"
        alt="GitHub"
        width="16"
        height="16"
    />
</a>
</div>
<div class="header">
    <img class="header-logo" src="@/assets/xLLaMa_logo.png"  alt="xLLaMa" height="48px"/>
    <h1>LLaMa</h1>
</div>

<ApiSelector @frameworkChanged="frameworkChanged"></ApiSelector>
<FunctionSelector ref="functionSelector" @frameworkItemSelected="frameworkItemSelected"></FunctionSelector>
<div>
    <button v-on:click="generateExample()" class="generate-example-button" :disabled="selectedFrameworkItem == null">Generate Examples!</button>
</div>
<div>
    <ModelSelection
        v-for="modelSelectionId in modelSelectionIds"
        :key="modelSelectionId"
        :all-framework-items="allFrameworkItems"
        :ref="`modelSelection_${modelSelectionId}`"
        :id="modelSelectionId"
        :is-dummy="modelSelectionId == dummyModelSelectionId"
        :debug="debug"
        @generateFollowUpExample="generateFollowUpExample"
        @close="close"
    />
    <ModelSelection
        v-if="debug"
        :all-framework-items="allFrameworkItems"
        :ref="`modelSelection_<<<DEBUG_DUMMY_1>>>`"
        :is-dummy="true"
        :debug="true"
        @generateFollowUpExample="generateFollowUpExample"
        @close="close"
    />
    <ModelSelection
        v-if="debug"
        :all-framework-items="allFrameworkItems"
        :ref="`modelSelection_<<<DEBUG_DUMMY_2>>>`"
        :is-dummy="true"
        :debug="true"
        @generateFollowUpExample="generateFollowUpExample"
        @close="close"
    />
</div>

<div class="copyright-info" @click="debugToggleClick()">
    Copyright (c) 2024 Lara Kursawe, Christian Raue
</div>
</template>

<script>
import ApiSelector from '@/components/ApiSelector.vue';
import FunctionSelector from '@/components/FunctionSelector.vue'
import ModelSelection from '@/components/ModelSelection.vue'

export default {
    name: "MainPage",
    components: {
        ApiSelector,
        FunctionSelector,
        ModelSelection
    },
    data() {
        return {
            selectedFramework: null,
            selectedFrameworkItem: null,
            allFrameworkItems: [],

            dummyModelSelectionId: '<<<DUMMY>>>',
            modelSelectionIds: [],
            unused: true,

            debug: false,
            debugToggleClickAmount: 0
        }
    },
    methods: {
        frameworkChanged(framework) {
            this.selectedFramework = framework;
            this.$refs.functionSelector.frameworkChanged(framework);
        },
        frameworkItemSelected(frameworkItem) {
            this.selectedFrameworkItem = frameworkItem;
        },
        generateExample() {
            this._generateExample(this.selectedFrameworkItem, 0);
        },
        generateFollowUpExample(frameworkItem, id) {
            const index = this.modelSelectionIds.indexOf(id);
            this._generateExample(frameworkItem, index + 1);
        },
        _generateExample(frameworkItem, index) {
            if (this.unused) {
                this.unused = false;
                this.modelSelectionIds = [];
            }
            this.$nextTick(() => {
                const id = this.uuidv4();
                this.modelSelectionIds.splice(index, 0, id);
                this.$nextTick(() => {
                    const modelSelection = this.$refs[`modelSelection_${id}`][0];
                    modelSelection.generateExample(frameworkItem);
                });
            });
        },
        uuidv4() {
          return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
          );
        },
        close(id) {
            this.unused = false;
            const index = this.modelSelectionIds.indexOf(id);
            this.modelSelectionIds.splice(index, 1);
        },
        debugToggleClick() {
            this.debugToggleClickAmount++;
            if (this.debugToggleClickAmount == 7) {
                this.debug = !this.debug;
                this.debugToggleClickAmount = 0;
                if (this.debug) {
                    this.$toast.open({
                        "message": "Debug mode activated",
                        "position": "top-right",
                        "type": "default"
                    });
                } else {
                    this.$toast.open({
                        "message": "Debug mode deactivated",
                        "position": "top-right",
                        "type": "default"
                    });
                }
            }
        }
    },
    mounted: function() {
        fetch("http://" + this.host + ":5003/framework_items")
        .then((response) => response.json())
        .then((responseJson) => {
            this.allFrameworkItems = responseJson;
            console.log(this.allFrameworkItems);
        })
        .catch((error) => {
            console.log(error);
        });

        // this.modelSelectionIds.push(this.dummyModelSelectionId);
    },
    computed: {
        host() { return window.location.origin.split("/")[2].split(":")[0]; }
    }
}
</script>