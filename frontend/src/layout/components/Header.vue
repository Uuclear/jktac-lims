<script setup>
/**
 * 头部组件
 */
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 切换侧边栏
const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// 前往个人中心
const goProfile = () => {
  router.push('/profile')
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.doLogout()
  })
}
</script>

<template>
  <div class="header-container">
    <div class="left">
      <!-- 折叠按钮 -->
      <div class="collapse-btn" @click="toggleSidebar">
        <el-icon :size="20">
          <Fold v-if="!appStore.sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
      </div>
      
      <!-- 面包屑 -->
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="$route.meta?.title">
          {{ $route.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="right">
      <!-- 用户信息 -->
      <el-dropdown trigger="click">
        <div class="user-info">
          <el-avatar :size="32" icon="User" />
          <span class="username">{{ userStore.userName }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="goProfile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.header-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  
  &:hover {
    background-color: #f5f5f5;
  }
}

.right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  
  &:hover {
    background-color: #f5f5f5;
  }
  
  .username {
    font-size: 14px;
    color: #333;
  }
}
</style>
