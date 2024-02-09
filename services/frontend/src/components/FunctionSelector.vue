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
    <a class="suggested-functions">   Suggested Functions: </a>
    <button
        v-for="frameworkItem in displayedFrameworkItems"
        :key="frameworkItem.id"
        v-on:click="buttonClicked(frameworkItem)"
    >{{ frameworkItem.name }}</button>
</div>
</template>

<script>
import AutoComplete from 'primevue/autocomplete';
import { host } from "@/util/util.js";

export default {
    name: "FunctionSelector",
    components: {
        AutoComplete
    },
    data() {
        return {
            frameworkItems: [],
            suggestions: [],
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
                fetch("http://" + host() + ":5003/framework_items/" + frameworkItemId)
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
            const query = event.query.toLowerCase();
            this.suggestions = this.frameworkItems.filter((item) => {
                return item.name.toLowerCase().includes(query);
            });
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
        }
    }
}
</script>