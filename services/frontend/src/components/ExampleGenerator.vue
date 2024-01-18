<!-- <style>
</style>

<template>
<div>
    <div>
        <button v-on:click="generateExample()" class="generate-example-button" :disabled="frameworkItem == null">Generate Examples!</button>
    </div>
    <ModelSelection
        ref="modelSelection"
        :all-framework-items="allFrameworkItems"
    />
</div>
</template>

<script>
import ModelSelection from '@/components/ModelSelection.vue'

export default {
    name: "ExampleGenerator",
    components: {
        ModelSelection
    },
    props: {
        allFrameworkItems: Array
    },
    data() {
        return {
            frameworkItem: null
        }
    },
    methods: {
        frameworkItemChanged(frameworkItem) {
            this.$refs.modelSelection.frameworkItemChanged(frameworkItem);
            this.frameworkItem = frameworkItem;
        },
        generateExample() {
            console.log("generateExample in ExampleGenerator");
            this.$refs.modelSelection.generateExample();
        },
    }
}
</script> -->
