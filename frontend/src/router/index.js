/**
 * 路由配置
 * 
 * 定义所有页面路由，实现权限控制
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 布局组件
import Layout from '@/layout/index.vue'

// 公共路由（无需登录）
const publicRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
]

// 静态路由（登录后可访问）
const staticRoutes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      }
    ]
  },
  {
    path: '/samples',
    component: Layout,
    redirect: '/samples/commissions',
    meta: { title: '委托收样', icon: 'Document' },
    children: [
      {
        path: 'commissions',
        name: 'Commissions',
        component: () => import('@/views/samples/commissions/index.vue'),
        meta: { title: '委托单管理' }
      },
      {
        path: 'clients',
        name: 'Clients',
        component: () => import('@/views/samples/clients/index.vue'),
        meta: { title: '委托方管理' }
      },
      {
        path: 'receives',
        name: 'Receives',
        component: () => import('@/views/samples/receives/index.vue'),
        meta: { title: '收样记录' }
      }
    ]
  },
  {
    path: '/workflow',
    component: Layout,
    redirect: '/workflow/list',
    meta: { title: '样品流转', icon: 'Operation' },
    children: [
      {
        path: 'list',
        name: 'WorkflowList',
        component: () => import('@/views/workflow/list/index.vue'),
        meta: { title: '流转管理' }
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/workflow/tasks/index.vue'),
        meta: { title: '我的任务' }
      }
    ]
  },
  {
    path: '/records',
    component: Layout,
    redirect: '/records/list',
    meta: { title: '原始记录', icon: 'Tickets' },
    children: [
      {
        path: 'list',
        name: 'RecordList',
        component: () => import('@/views/records/list/index.vue'),
        meta: { title: '记录列表' }
      },
      {
        path: 'templates',
        name: 'RecordTemplates',
        component: () => import('@/views/records/templates/index.vue'),
        meta: { title: '模板管理' }
      }
    ]
  },
  {
    path: '/ocr',
    component: Layout,
    redirect: '/ocr/scans',
    meta: { title: 'OCR识别', icon: 'Camera' },
    children: [
      {
        path: 'scans',
        name: 'Scans',
        component: () => import('@/views/ocr/scans/index.vue'),
        meta: { title: '扫描件管理' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/ocr/reports/index.vue'),
        meta: { title: '检测报告' }
      }
    ]
  },
  {
    path: '/quality',
    component: Layout,
    redirect: '/quality/documents',
    meta: { title: '质量体系', icon: 'Files' },
    children: [
      {
        path: 'documents',
        name: 'QualityDocuments',
        component: () => import('@/views/quality/documents/index.vue'),
        meta: { title: '体系文件' }
      }
    ]
  },
  {
    path: '/capability',
    component: Layout,
    redirect: '/capability/standards',
    meta: { title: '能力管理', icon: 'Medal' },
    children: [
      {
        path: 'standards',
        name: 'Standards',
        component: () => import('@/views/capability/standards/index.vue'),
        meta: { title: '检测标准' }
      },
      {
        path: 'parameters',
        name: 'Parameters',
        component: () => import('@/views/capability/parameters/index.vue'),
        meta: { title: '检测参数' }
      }
    ]
  },
  {
    path: '/equipment',
    component: Layout,
    redirect: '/equipment/list',
    meta: { title: '设备管理', icon: 'Monitor' },
    children: [
      {
        path: 'list',
        name: 'EquipmentList',
        component: () => import('@/views/equipment/list/index.vue'),
        meta: { title: '设备列表' }
      },
      {
        path: 'laboratories',
        name: 'Laboratories',
        component: () => import('@/views/equipment/laboratories/index.vue'),
        meta: { title: '试验室管理' }
      },
      {
        path: 'calibrations',
        name: 'Calibrations',
        component: () => import('@/views/equipment/calibrations/index.vue'),
        meta: { title: '校准记录' }
      }
    ]
  },
  {
    path: '/floorplan',
    component: Layout,
    redirect: '/floorplan/view',
    meta: { title: '平面图', icon: 'MapLocation' },
    children: [
      {
        path: 'view',
        name: 'FloorPlanView',
        component: () => import('@/views/floorplan/view/index.vue'),
        meta: { title: '平面图查看' }
      }
    ]
  },
  {
    path: '/statistics',
    component: Layout,
    redirect: '/statistics/dashboard',
    meta: { title: '数据统计', icon: 'DataAnalysis' },
    children: [
      {
        path: 'dashboard',
        name: 'StatisticsDashboard',
        component: () => import('@/views/statistics/dashboard/index.vue'),
        meta: { title: '统计面板' }
      },
      {
        path: 'reports',
        name: 'StatisticsReports',
        component: () => import('@/views/statistics/reports/index.vue'),
        meta: { title: '报表管理' }
      }
    ]
  },
  {
    path: '/ai-verify',
    component: Layout,
    redirect: '/ai-verify/verify',
    meta: { title: 'AI校验', icon: 'MagicStick' },
    children: [
      {
        path: 'verify',
        name: 'AiVerify',
        component: () => import('@/views/ai-verify/verify/index.vue'),
        meta: { title: '文档校验' }
      },
      {
        path: 'records',
        name: 'VerifyRecords',
        component: () => import('@/views/ai-verify/records/index.vue'),
        meta: { title: '校验记录' }
      }
    ]
  },
  {
    path: '/cloud',
    component: Layout,
    redirect: '/cloud/applications',
    meta: { title: '云查询', icon: 'Cloudy' },
    children: [
      {
        path: 'applications',
        name: 'CloudApplications',
        component: () => import('@/views/cloud/applications/index.vue'),
        meta: { title: '查看申请' }
      }
    ]
  },
  {
    path: '/users',
    component: Layout,
    redirect: '/users/list',
    meta: { title: '用户管理', icon: 'User', roles: ['admin'] },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('@/views/users/list/index.vue'),
        meta: { title: '用户列表' }
      },
      {
        path: 'departments',
        name: 'Departments',
        component: () => import('@/views/users/departments/index.vue'),
        meta: { title: '部门管理' }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', hidden: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { hidden: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: [...publicRoutes, ...staticRoutes]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const userStore = useUserStore()
  const token = userStore.token
  
  if (to.path === '/login') {
    next()
    return
  }
  
  if (!token) {
    next(`/login?redirect=${to.path}`)
    return
  }
  
  // 检查角色权限
  const requiredRoles = to.meta?.roles
  if (requiredRoles && !requiredRoles.includes(userStore.userInfo?.role)) {
    next('/dashboard')
    return
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
