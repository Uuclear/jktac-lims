<script setup>
/**
 * 侧边栏组件
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const isCollapsed = computed(() => appStore.sidebarCollapsed)

// 获取菜单列表（根据路由配置生成）
const menuList = computed(() => {
  const routes = router.options.routes.filter(r => r.path === '/')[0]?.children || []
  const staticRoutes = router.options.routes.filter(r => 
    r.component?.name === 'Layout' || r.path.startsWith('/')
  )
  
  return staticRoutes
    .filter(r => r.meta && !r.meta.hidden && r.children)
    .map(r => ({
      path: r.path,
      title: r.meta?.title,
      icon: r.meta?.icon,
      children: r.children?.filter(c => !c.meta?.hidden).map(c => ({
        path: c.path.startsWith('/') ? c.path : `${r.path}/${c.path}`,
        title: c.meta?.title,
      }))
    }))
})

const activeMenu = computed(() => route.path)
</script>

<template>
  <div class="sidebar-container">
    <!-- Logo -->
    <div class="logo">
      <img src="@/assets/logo.svg" alt="Logo" class="logo-img" />
      <span v-show="!isCollapsed" class="logo-text">JKTAC LIMS</span>
    </div>
    
    <!-- 菜单 -->
    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <template v-for="menu in menuList" :key="menu.path">
          <!-- 有子菜单 -->
          <el-sub-menu v-if="menu.children?.length > 1" :index="menu.path">
            <template #title>
              <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
              <span>{{ menu.title }}</span>
            </template>
            <el-menu-item
              v-for="child in menu.children"
              :key="child.path"
              :index="child.path"
            >
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 无子菜单或只有一个子菜单 -->
          <el-menu-item
            v-else
            :index="menu.children?.[0]?.path || menu.path"
          >
            <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
            <template #title>{{ menu.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<style lang="scss" scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  background-color: #263445;
  
  .logo-img {
    width: 32px;
    height: 32px;
  }
  
  .logo-text {
    margin-left: 12px;
    font-size: 18px;
    font-weight: 600;
    color: #fff;
    white-space: nowrap;
  }
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-sub-menu__title:hover),
:deep(.el-menu-item:hover) {
  background-color: #263445 !important;
}

:deep(.el-menu-item.is-active) {
  background-color: #409EFF !important;
}
</style>
