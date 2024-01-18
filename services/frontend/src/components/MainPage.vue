<style>
</style>

<template>
<h1>xLLaMa</h1>
<ApiSelector @frameworkChanged="frameworkChanged"></ApiSelector>
<FunctionSelector ref="functionSelector" @frameworkItemSelected="frameworkItemSelected"></FunctionSelector>
<ExampleGenerator ref="exampleGenerator"></ExampleGenerator>
</template>

<script>
import ApiSelector from '@/components/ApiSelector.vue';
import FunctionSelector from '@/components/FunctionSelector.vue'
import ExampleGenerator from '@/components/ExampleGenerator.vue';

export default {
    name: "MainPage",
    components: {
        ApiSelector,
        FunctionSelector,
        ExampleGenerator
    },
    data() {
        return {
            selectedFramework: null,
            selectedFrameworkItem: null
        }
    },
    methods: {
        frameworkChanged(framework) {
            this.selectedFramework = framework;
            this.$refs.functionSelector.frameworkChanged(framework);
        },
        frameworkItemSelected(frameworkItem) {
            this.selectedFrameworkItem = frameworkItem;
            this.$refs.exampleGenerator.frameworkItemChanged(frameworkItem);
        }
    }
}
</script>
