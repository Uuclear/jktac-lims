<script setup>
/**
 * 主布局组件
 * 
 * 包含侧边栏、头部、内容区域
 */
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'

const appStore = useAppStore()

const sidebarWidth = computed(() => {
  return appStore.sidebarCollapsed ? '64px' : '220px'
})
</script>

<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <aside class="sidebar" :style="{ width: sidebarWidth }">
      <Sidebar />
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-container" :style="{ marginLeft: sidebarWidth }">
      <!-- 头部 -->
      <header class="header">
        <Header />
      </header>
      
      <!-- 内容区 -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.layout-container {
  width: 100%;
  height: 100%;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  background-color: var(--sidebar-bg);
  transition: width 0.3s;
  z-index: 1001;
  overflow: hidden;
}

.main-container {
  min-height: 100%;
  transition: margin-left 0.3s;
  background-color: var(--bg-color);
}

.header {
  position: sticky;
  top: 0;
  height: var(--header-height);
  background-color: var(--header-bg);
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1000;
}

.content {
  padding: 20px;
  min-height: calc(100vh - var(--header-height));
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
