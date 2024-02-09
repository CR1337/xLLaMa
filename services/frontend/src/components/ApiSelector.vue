<template>
<div>
    <a>API / Framework: </a>
    <template v-for="framework in frameworks" :key="framework.id">
        <input type="radio" :id="framework.id" :value="framework" v-on:click="selectionChanged(framework)" name="framework_selection">
        <label :for="framework.id">{{ framework.name }}</label>
    </template>
</div>
</template>

<script>
import { db } from "@/util/dbInterface.js";

export default {
    name: "ApiSelector",
    data() {
        return {
            frameworks: [],
            selected_framework: null
        }
    },
    methods: {
        selectionChanged(framework) {
            this.selected_framework = framework;
            this.$emit('frameworkChanged', framework);
        }
    },
    mounted() {
        db.getAll("framework_items")
        .then(responseJson => {
            this.frameworkItems = responseJson;
        });
    }
}
</script>