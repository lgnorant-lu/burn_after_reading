import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/create',
      name: 'create',
      component: () => import('../views/CreatePage.vue')
    },
    {
      path: '/note/:id',
      name: 'note',
      component: () => import('../views/NoteView.vue')
    }
  ]
})

// 路由守卫：设置页面标题
router.beforeEach((to) => {
  document.title = (to.meta.title as string) || 'Burn After Reading'
})

export default router 