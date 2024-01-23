<style>
</style>

<template>
<div class="outsidewrapper">
    <h4 class="Function_Title"> {{ (isDummy) ? 'Noting generated yet!' : (frameworkItem == null) ? "Noting generated yet!" : frameworkItem.name }} </h4>
    <button title="close this example" class="closeButton" @click="close" style="float: right;">✖</button>
    <div class="top-row">
        <template v-for="model in models" :key="model">
        <input type="radio" :id="model + '_' + id" :value="model" :name="'model_selection_' + id" v-model="selectedModel">
        <label :for="model + '_' + id">{{ model.split(":")[0] }}</label>
    </template>
    <template v-for="model in disabled_models" :key="model">
        <input type="radio" :id="model + '_' + id" :value="model" :name="'model_selection_' + id" disabled>
        <label :for="model + '_' + id">{{ model.split(":")[0] }}</label>
    </template>
    </div>
    <template v-for="model in models" :key="model">
        <Model
            :model="model"
            :framework-item="frameworkItem"
            :visible="model == selectedModel"
            :ref="`ref_${model}`"
            :all-framework-items="allFrameworkItems"
            :is-dummy="isDummy"
            :debug="debug"
            @generateFollowUpExample="generateFollowUpExample"
        />
    </template>
</div>
</template>

<script>
import Model from '@/components/Model.vue'

export default {
    name: "ModelSelection",
    components: {
        Model
    },
    props: {
        allFrameworkItems: Array,
        id: String,
        isDummy: Boolean,
        debug: Boolean
    },
    data() {
        return {
            models: ["codellama:7b-instruct", "wizardcoder:13b-python"],
            disabled_models: ["GPT-3.5", "GPT-4"],
            selectedModel: "codellama:7b-instruct",
            frameworkItem: null
        }
    },
    methods: {
        generateExample(frameworkItem) {
            this.frameworkItem = frameworkItem;
            for (const model of this.models) {
                const component = this.$refs[`ref_${model}`][0];
                component.generateExample();
            }
        },
        generateFollowUpExample(frameworkItem) {
            this.$emit('generateFollowUpExample', frameworkItem, this.id);
        },
        close() {
            this.$emit('close', this.id);
        }
    }
}
</script>
