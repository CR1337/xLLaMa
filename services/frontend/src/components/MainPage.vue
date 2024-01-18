<style>
</style>

<template>
<h1>xLLaMa</h1>
<ApiSelector @frameworkChanged="frameworkChanged"></ApiSelector>
<FunctionSelector ref="functionSelector" @frameworkItemSelected="frameworkItemSelected"></FunctionSelector>
<div>
    <button v-on:click="generateExample()" class="generate-example-button" :disabled="selectedFrameworkItem == null">Generate Examples!</button>
</div>
<ModelSelection
    v-for="modelSelectionId in modelSelectionIds"
    :key="modelSelectionId"
    :all-framework-items="allFrameworkItems"
    :ref="`modelSelection_${modelSelectionId}`"
    :id="modelSelectionId"
    :is-dummy="modelSelectionId == dummyModelSelectionId"
    @generateFollowUpExample="generateFollowUpExample"
/>
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
            unused: true
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
            if (this.ununsed) {
                this.unused = false;
                this.modelSelectionIds = [];
            }
            const id = this.uuidv4();
            this.modelSelectionIds.splice(index, 0, id);
            this.$nextTick(() => {
                this.$refs[`modelSelection_${id}`][0].generateExample(frameworkItem);
                const modelSelection = this.$refs[`modelSelection_${id}`][0];
                modelSelection.generateExample(frameworkItem);
            });
        },
        uuidv4() {
          return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
          );
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

        this.modelSelectionIds.push(this.dummyModelSelectionId);
    },
    computed: {
        host() { return window.location.origin.split("/")[2].split(":")[0]; }
    }
}
</script>
