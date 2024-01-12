<style>
</style>

<template>
<div>
    <div>
        <button v-on:click="generateExample()" class="generate-example-button" :disabled="frameworkItem == null">Generate Examples!</button>
    </div>
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
            :visible="model == selectedModel"
            :ref="`ref_${model}`"
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
            frameworkItem: null,
        }
    },
    methods: {
        frameworkItemChanged(frameworkItem) {
            this.frameworkItem = frameworkItem;
        },
        generateExample() {
            for (const model of this.models) {
                const component = this.$refs[`ref_${model}`][0];
                component.generateExample();
            }
        },
    }
}
</script>
