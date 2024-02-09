<style>
@import 'src/assets/syntax-highlighting.css';
</style>

<template>
<div><button class="copy-button" title="Copy to clipboard" v-on:click="copyToClipboard()">
    <img class="copy-button-image" v-bind:src="'src/assets/copy-icon.png'">
</button></div>
<span class="code-snipet-span" v-html="code"></span>
</template>

<script>
import { codeSnippetObjects, handleCodeSnippetObjectClick } from "/src/main.js";
import { codeAnalyzer } from "../util/codeAnalyzer";

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
    codeAnalyzer.highlightCode(
      this.codeSnippet.id,
      'clickable',
      this.clickableNamesForUrl,
      'onclick',
      'handleCodeSnippetObjectClick'
    )
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
          this.$toast.open({
              "message": "Copied to clipboard",
              "position": "top-right",
              "type": "default"
          });
        }
    },
  computed: {
    clickableNamesForUrl() {
        return this.clickableNames.join(",");
    }
  }
};
</script>