<script setup>
/**
 * 工作台/仪表盘页面
 */
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loading = ref(false)
const stats = ref({
  totalCommissions: 0,
  monthCommissions: 0,
  pendingCommissions: 0,
  inProgressWorkflows: 0,
  totalEquipments: 0,
})

// 获取统计数据
const fetchStats = async () => {
  loading.value = true
  try {
    // TODO: 调用接口获取统计数据
    // const res = await getDashboardStats()
    // stats.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h2>欢迎回来，{{ userStore.userName }}</h2>
        <p>今天是个好日子，祝您工作顺利！</p>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #409EFF;">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">委托单总数</div>
            <div class="stat-value">{{ stats.totalCommissions }}</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #67C23A;">
            <el-icon :size="24"><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">本月委托</div>
            <div class="stat-value">{{ stats.monthCommissions }}</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6A23C;">
            <el-icon :size="24"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">待处理</div>
            <div class="stat-value">{{ stats.pendingCommissions }}</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F56C6C;">
            <el-icon :size="24"><Operation /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">进行中流转</div>
            <div class="stat-value">{{ stats.inProgressWorkflows }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <div class="section">
      <h3 class="section-title">快捷操作</h3>
      <el-row :gutter="20">
        <el-col :span="4">
          <router-link to="/samples/commissions">
            <div class="quick-action">
              <el-icon :size="32"><DocumentAdd /></el-icon>
              <span>新建委托</span>
            </div>
          </router-link>
        </el-col>
        <el-col :span="4">
          <router-link to="/workflow/tasks">
            <div class="quick-action">
              <el-icon :size="32"><List /></el-icon>
              <span>我的任务</span>
            </div>
          </router-link>
        </el-col>
        <el-col :span="4">
          <router-link to="/records/list">
            <div class="quick-action">
              <el-icon :size="32"><Edit /></el-icon>
              <span>录入记录</span>
            </div>
          </router-link>
        </el-col>
        <el-col :span="4">
          <router-link to="/ocr/reports">
            <div class="quick-action">
              <el-icon :size="32"><Files /></el-icon>
              <span>检测报告</span>
            </div>
          </router-link>
        </el-col>
        <el-col :span="4">
          <router-link to="/statistics/dashboard">
            <div class="quick-action">
              <el-icon :size="32"><DataAnalysis /></el-icon>
              <span>数据统计</span>
            </div>
          </router-link>
        </el-col>
      </el-row>
    </div>
    
    <!-- 待办事项（预留插槽） -->
    <div class="section">
      <h3 class="section-title">待办事项</h3>
      <el-empty description="暂无待办事项" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px 32px;
  margin-bottom: 24px;
  color: #fff;
  
  h2 {
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  p {
    opacity: 0.8;
  }
}

.stat-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  
  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }
  
  .stat-content {
    flex: 1;
  }
  
  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 4px;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
  }
}

.section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    background: #e6f7ff;
    color: #409EFF;
  }
  
  span {
    margin-top: 8px;
    font-size: 14px;
  }
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
