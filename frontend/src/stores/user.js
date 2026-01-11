/**
 * 用户状态管理
 * 
 * 管理用户登录状态、用户信息、权限等
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserInfo } from '@/api/user'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || '')
  const userName = computed(() => userInfo.value?.username || '')
  
  // 登录
  async function doLogin(loginData) {
    try {
      const res = await login(loginData)
      if (res.code === 200) {
        token.value = res.data.access
        userInfo.value = res.data.user
        localStorage.setItem('token', res.data.access)
        localStorage.setItem('refreshToken', res.data.refresh)
        return { success: true }
      }
      return { success: false, message: res.message }
    } catch (error) {
      return { success: false, message: error.message }
    }
  }
  
  // 登出
  async function doLogout() {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      await logout({ refresh: refreshToken })
    } catch (e) {
      // 忽略登出接口错误
    } finally {
      resetState()
      router.push('/login')
    }
  }
  
  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      if (res.code === 200) {
        userInfo.value = res.data
        return true
      }
      return false
    } catch (error) {
      return false
    }
  }
  
  // 重置状态
  function resetState() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }
  
  // 检查是否有指定角色
  function hasRole(...roles) {
    return roles.includes(userRole.value)
  }
  
  // 检查是否为管理员
  function isAdmin() {
    return userRole.value === 'admin'
  }
  
  return {
    token,
    userInfo,
    isLoggedIn,
    userRole,
    userName,
    doLogin,
    doLogout,
    fetchUserInfo,
    resetState,
    hasRole,
    isAdmin,
  }
})
