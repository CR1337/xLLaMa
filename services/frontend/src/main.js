import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'
import ToastPlugin from 'vue-toast-notification';
// Import one of the available themes
//import 'vue-toast-notification/dist/theme-default.css';
import 'vue-toast-notification/dist/theme-bootstrap.css';

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
