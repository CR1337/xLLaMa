import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'

export const codeSnippetObjects = {};

export function handleCodeSnippetObjectClick(codeSnippetId, name) {
    codeSnippetObjects[codeSnippetId].handleClick(name);
}

window.codeSnippetObjects = codeSnippetObjects;
window.handleCodeSnippetObjectClick = handleCodeSnippetObjectClick;

const app = createApp(App)
app.use(router)
app.use(PrimeVue)
app.mount('#app')
