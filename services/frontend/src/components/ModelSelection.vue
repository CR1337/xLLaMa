<style>
</style>

<template>
<div>
    <div class="top-row">
        <template v-for="model in models" :key="model">
        <input type="radio" :id="model" :value="model" name="model_selection" v-model="selectedModel">
        <label :for="model">{{ model.split(":")[0] }}</label>
    </template>
    <template v-for="model in disabled_models" :key="model">
        <input type="radio" :id="model" :value="model" name="model_selection" disabled>
        <label :for="model">{{ model.split(":")[0] }}</label>
    </template>
    <button @click="close" style="float: right;">X</button>
    </div>
    <template v-for="model in models" :key="model">
        <Model
            :model="model"
            :framework-item="frameworkItem"
            :visible="model == selectedModel"
            :ref="`ref_${model}`"
            :all-framework-items="allFrameworkItems"
            :is-dummy="isDummy"
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
        id: Number,
        isDummy: Boolean
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
