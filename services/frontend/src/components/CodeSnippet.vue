<style>
@import 'src/assets/syntax-highlighting.css';
</style>

<template>
<div><button class="copy" title="Copy to clipboard" v-on:click="copyToClipboard()">
    <img class="copyimg" v-bind:src="'src/assets/copy-icon.png'">
</button></div>
<span class="code-snipet-span" v-html="code"></span>
</template>

<script>
import { codeSnippetObjects, handleCodeSnippetObjectClick } from "/src/main.js";

export default {
  name: 'CodeSnippet',
  props: {
    codeSnippet: Object,
    clickableNames: Array,
    rawHtml: String
  },
  data() {
    return {
      code: ""
    };
  },
  mounted() {
    if (this.rawHtml !== undefined) {
      this.code = this.rawHtml;
      return;
    }
    codeSnippetObjects[this.codeSnippet.id] = this;
    fetch(
        `http://${this.host}:5002/highlight`
        + `?code_snippet=${this.codeSnippet.id}`
        + `&clickable_class=clickable`
        + `&clickable_names=${this.clickableNamesForUrl}`
        + `&on_click_attribute=onclick`
        + `&click_handler=handleCodeSnippetObjectClick`
    )
        .then(response => response.json())
        .then(data => {
          this.code = data.html;
        })
        .catch(error => console.error(error));
  },
    methods: {
        handleClick(name) {
            this.$emit("click", name);
        },

        copyToClipboard() {
          // source: https://stackoverflow.com/questions/51805395/navigator-clipboard-is-undefined
          if (navigator.clipboard && window.isSecureContext) {
              navigator.clipboard.writeText(this.codeSnippet.code);
          } else {
              // Use the 'out of viewport hidden text area' trick
              const textArea = document.createElement("textarea");
              textArea.value = this.codeSnippet.code;

              // Move textarea out of the viewport so it's not visible
              textArea.style.position = "absolute";
              textArea.style.left = "-999999px";

              document.body.prepend(textArea);
              textArea.select();

              try {
                  document.execCommand('copy');
              } catch (error) {
                  console.error(error);
              } finally {
                  textArea.remove();
              }
          }
        }
    },
  computed: {
    host() { return window.location.origin.split("/")[2].split(":")[0]; },

    clickableNamesForUrl() {
        return this.clickableNames.join(",");
    }
  }
};
</script>