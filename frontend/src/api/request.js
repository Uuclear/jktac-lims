/**
 * Axios请求封装
 * 
 * 提供统一的请求配置、拦截器、错误处理
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    
    // 添加token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data
    
    // 直接返回数据
    return res
  },
  (error) => {
    console.error('响应错误:', error)
    
    const response = error.response
    
    if (response) {
      const status = response.status
      const data = response.data
      
      // 处理不同错误状态码
      switch (status) {
        case 401:
          // 未登录或token过期
          ElMessage.error('登录已过期，请重新登录')
          const userStore = useUserStore()
          userStore.resetState()
          router.push('/login')
          break
        case 403:
          ElMessage.error(data?.message || '权限不足')
          break
        case 404:
          ElMessage.error(data?.message || '请求的资源不存在')
          break
        case 500:
          ElMessage.error(data?.message || '服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
      
      return Promise.reject(data || error)
    }
    
    // 网络错误
    ElMessage.error('网络连接失败，请检查网络')
    return Promise.reject(error)
  }
)

// 封装请求方法
export const get = (url, params, config) => {
  return service.get(url, { params, ...config })
}

export const post = (url, data, config) => {
  return service.post(url, data, config)
}

export const put = (url, data, config) => {
  return service.put(url, data, config)
}

export const patch = (url, data, config) => {
  return service.patch(url, data, config)
}

export const del = (url, config) => {
  return service.delete(url, config)
}

// 文件上传
export const upload = (url, file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return service.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percent)
      }
    },
  })
}

export default service
