<script setup>
/**
 * 应用根组件
 */
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<style>
#app {
  width: 100%;
  height: 100%;
}
</style>
