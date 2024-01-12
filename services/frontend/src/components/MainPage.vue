<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

h1 {
    padding: 5px;
    font-family: 'Poppins', sans-serif;
}

div {
    margin: 5px;
    padding: 5px;
    font-family: 'Poppins', sans-serif;
}

button {
  display: inline-block;
  background: #000;
  color: #fff;
  border: none;
  padding: 10px 20px;
  margin: 5px;
  border-radius: 5px;
  cursor: pointer;
  text-decoration: none;
  font-size: 15px;
  font-family: 'Poppins', sans-serif;
}

label {
    font-family: 'Poppins', sans-serif;
    margin-right: 10px;
}

input {
    font-family: 'Poppins', sans-serif;
    margin-right: 3px;
}

span {
    white-space: pre;
}

.container {
    max-width: 700px;
    margin: 30px 0 30px;
    overflow: auto;
    min-height: 300px;
    border: 1px solid steelblue;
    border-radius: 5px;
    background-color: white;
}

.container pre {
    font-family: 'Courier New', Courier, monospace !important;
    background-color: white;
}

.generate-example-button {
    background-color: salmon;
    color: black;
}
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
