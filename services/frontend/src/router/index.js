import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../components/MainPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'mainPage',
      component: MainPage
    }
  ]
})

export default router
