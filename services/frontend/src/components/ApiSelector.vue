<style>
</style>

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
        fetch("http://localhost:5003/frameworks", )
        .then((response) => response.json())
        .then((responseJson) => {
            this.frameworks = responseJson;
        })
        .catch((error) => {
            console.log(error);
        });
    }
}
</script>
