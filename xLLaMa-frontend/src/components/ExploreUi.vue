<style>
</style>

<template>
<h1>xLLaMa</h1><br>
<textarea v-model="content" rows="32" cols="64"/><br>
<button @click="button_clicked()">Send</button>
</template>

<script>
export default {
    name: "ExploreUi",
    data() {
        return {
            content: ""
        };
    },
    methods: {
        button_clicked() {
            // alert("button clicked");
            fetch("http://localhost:11434/api/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    model: "codellama:7b-instruct",
                    prompt: this.content
                })
            }).then(response => {
                const reader = response.body.getReader();
                return new ReadableStream({
                    start(controller) {
                        function push() {
                            reader.read().then(({done, value}) => {
                                if (done) {
                                    controller.close();
                                    return;
                                }
                                controller.enqueue(value);
                                // this.content += value.response;
                                push();
                            })
                        }
                        push();
                    }
                });
            }).then(stream => {
                return new Response(stream, { headers: { "Content-Type": "text/html" } }).text();
            }).then(result => {
                console.log(result);
                let s = "";
                for (const element of result) {
                    s += element;
                }
                console.log(s);
                s = s.split("}\n{").join("},{");
                s = "[" + s + "]";
                console.log(s);
                let json = JSON.parse(s);
                for (const element of json) {
                    this.content += element.response;
                }
                // this.content += result.response;
            }).catch((error) => {
                console.error("Error:", error);
            });
        },
    }
};
</script>
