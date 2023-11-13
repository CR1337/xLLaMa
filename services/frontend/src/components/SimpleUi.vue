<style>
</style>

<template>
<h1>xLLaMa</h1>
<textarea v-model="content" rows="32" cols="64"/><br>
<button @click="buttonClicked()" :disabled="buttonDisabled">Send</button>
</template>

<script>


export default {
    name: "SimpleUi",
    data() {
        return {
            content: "",
            buttonDisabled: false
        }
    },
    methods: {
        buttonClicked() {
            // this.buttonDisabled = true;
            const url = "http://localhost:11434/api/generate?model=codellama:7b-instruct&prompt=" + this.content;

            const eventSource = new EventSource(url);
            eventSource.onmessage = (event) => {
                console.log(event.data);
                // this.content += event.data;
            };



        }
    }
}
</script>
