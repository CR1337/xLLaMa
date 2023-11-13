import { createRouter, createWebHistory } from 'vue-router'
import SimpleUi from '../components/SimpleUi.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'simpleUi',
      component: SimpleUi
    }
  ]
})

export default router
