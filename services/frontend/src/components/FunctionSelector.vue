<style>
</style>

<template>
<div>
    <a>Function: </a>
    <AutoComplete
        v-model="selectedFrameworkItem"
        :suggestions="suggestions"
        @complete="updateSuggestions"
        @change="selectionChanged"
        optionLabel="name"
        forceSelection
        dropdown
        :disabled="!enabled"
    />
    <button v-on:click="updateSuggestions()" :disabled="!enabled">🔎</button>
    <button
        v-for="frameworkItem in displayedFrameworkItems"
        :key="frameworkItem.id"
        v-on:click="buttonClicked(frameworkItem)"
    >{{ frameworkItem.name }}</button>
    <br>
    <a>Selected Function: </a><a>{{ (selectedFrameworkItem == null) ? "No Item selected!" : selectedFrameworkItem.name }}</a>
</div>
</template>

<script>


import AutoComplete from 'primevue/autocomplete';

export default {
    name: "FunctionSelector",
    components: {
        AutoComplete
    },
    data() {
        return {
            frameworkItems: [],
            suggestions: [],
            // typedFunction: "",
            selectedFrameworkItem: null,
            enabled: false,
            maxDisplayedFrameworkItems: 4
        }
    },
    methods: {
        frameworkChanged(framework) {
            this.frameworkItems = [];
            this.selectedFrameworkItem = null;
            this.selectionChanged();
            for (const frameworkItemId of framework.framework_items) {
                fetch("http://" + this.host + ":5003/framework_items/" + frameworkItemId)
                .then((response) => response.json())
                .then((responseJson) => {
                    this.frameworkItems.push(responseJson);
                    this.enabled = true;
                })
                .catch((error) => {
                    console.log(error);
                });
            }
        },
        buttonClicked(frameworkItem) {
            this.selectedFrameworkItem = frameworkItem;
            this.selectionChanged();
        },
        updateSuggestions(event) {
            this.suggestions = this.frameworkItems.map((e) => e);
        },
        selectionChanged() {
            this.$emit("frameworkItemSelected", this.selectedFrameworkItem);
        }
    },
    computed: {
        displayedFrameworkItems() {
            return this.frameworkItems.slice(
                0, Math.min(this.maxDisplayedFrameworkItems, this.frameworkItems.length + 1)
            );
        },
        host() { return window.location.origin.split("/")[2].split(":")[0]; }
    }
}
</script>
