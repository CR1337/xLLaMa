<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: 'Poppins', sans-serif;
}

h1 {
    padding: 5px;
}

div {
    margin: 5px;
    padding: 5px;
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
  font-family: inherit;
}

label {
    margin-right: 10px;
}

input {
    margin-right: 3px;
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