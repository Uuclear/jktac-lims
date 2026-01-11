/**
 * 应用状态管理
 * 
 * 管理应用全局状态，如侧边栏折叠、主题等
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 侧边栏是否折叠
  const sidebarCollapsed = ref(false)
  
  // 当前激活的菜单
  const activeMenu = ref('')
  
  // 切换侧边栏
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  // 设置激活菜单
  function setActiveMenu(menu) {
    activeMenu.value = menu
  }
  
  return {
    sidebarCollapsed,
    activeMenu,
    toggleSidebar,
    setActiveMenu,
  }
})
