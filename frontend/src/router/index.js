import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/layout/MainLayout.vue'),
    redirect: '/upload',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('@/views/Upload.vue'),
        meta: { title: '上传论文', requiresAuth: true }
      },
      {
        path: 'papers',
        name: 'PaperList',
        component: () => import('@/views/PaperList.vue'),
        meta: { title: '我的论文', requiresAuth: true }
      },
      {
        path: 'paper/:id',
        name: 'PaperDetail',
        component: () => import('@/views/PaperDetail.vue'),
        meta: { title: '论文详情', requiresAuth: true }
      },
      {
        path: 'generate/:id',
        name: 'ContentGenerate',
        component: () => import('@/views/ContentGenerate.vue'),
        meta: { title: '内容生成', requiresAuth: true }
      },
      {
        path: 'mindmap/:id',
        name: 'MindMap',
        component: () => import('@/views/MindMap.vue'),
        meta: { title: '思维导图', requiresAuth: true }
      },
      {
        path: 'timeline/:id',
        name: 'Timeline',
        component: () => import('@/views/Timeline.vue'),
        meta: { title: '时间线', requiresAuth: true }
      },
      {
        path: 'graph/:id',
        name: 'KnowledgeGraph',
        component: () => import('@/views/KnowledgeGraph.vue'),
        meta: { title: '概念图谱', requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
// router.beforeEach((to, from, next) => {
//   const token = localStorage.getItem('token')

//   if (to.meta.requiresAuth && !token) {
//     next('/login')
//   } else if ((to.path === '/login' || to.path === '/register') && token) {
//     next('/')
//   } else {
//     next()
//   }
// })

export default router
