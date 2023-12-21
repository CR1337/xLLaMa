<style scoped>
    .container {
    max-width: 500px;
    margin: 30px 0 30px;
    overflow: auto;
    min-height: 300px;
    border: 1px solid steelblue;
    padding: 30px;
    border-radius: 5px;
    background-color: black;
    color:white;
    font-family:'Courier New', Courier, monospace;
    }
</style>

<template>
<div>
    <div class="radio-container">
        <template v-for="model in models" :key="model">
        <input type="radio" :id="model" :value="model" name="model_selection" v-model="selectedModel">
        <label :for="model">{{ model.split(":")[0] }}</label>
    </template>
    <template v-for="model in disabled_models" :key="model">
        <input type="radio" :id="model" :value="model" name="model_selection" disabled>
        <label :for="model">{{ model.split(":")[0] }}</label>
    </template>
    </div>
    <template v-for="model in models" :key="model">
        <Model
            :model="model"
            :framework-item="frameworkItem"
            v-if="model == selectedModel"
            :id="'id_' + model"
        />
    </template>
</div>
</template>

<script>
import Model from '@/components/Model.vue';

export default {
    name: "ExampleGenerator",
    components: {
        Model
    },
    data() {
        return {
            models: ["codellama:7b-instruct", "wizardcoder:13b-python"],
            disabled_models: ["GPT-3.5", "GPT-4"],
            selectedModel: "codellama:7b-instruct",
            // generatedText: "Generated example will appear here.",

            frameworkItem: null,

            // generatedPredictions: [],
            // generated: false
        }
    },
    methods: {
        frameworkItemChanged(frameworkItem) {
            this.frameworkItem = frameworkItem;
        },
        generateExample() {
            for (const model of this.models) {
                const id = "id_" + model;
                const component = document.getElementById(id);
                component.generateExample();
            }
        },
    }
}
</script>
