import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'
import ToastPlugin from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-bootstrap.css';

// This is for handling click event from html injected after
// vue mounted the page.
export const codeSnippetObjects = {};
export function handleCodeSnippetObjectClick(codeSnippetId, name) {
    codeSnippetObjects[codeSnippetId].handleClick(name);
}
window.codeSnippetObjects = codeSnippetObjects;
window.handleCodeSnippetObjectClick = handleCodeSnippetObjectClick;

const app = createApp(App)
app.use(router)
app.use(PrimeVue)
app.use(ToastPlugin);
app.mount('#app')
