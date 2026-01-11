<script setup>
/**
 * 404页面
 */
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="not-found-container">
    <div class="content">
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.not-found-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.content {
  text-align: center;
  
  h1 {
    font-size: 120px;
    font-weight: 700;
    color: #409EFF;
    margin-bottom: 16px;
  }
  
  p {
    font-size: 18px;
    color: #606266;
    margin-bottom: 24px;
  }
}
</style>
