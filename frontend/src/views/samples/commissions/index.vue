<script setup>
/**
 * 委托单管理页面
 * 
 * 功能：
 * - 委托单列表展示
 * - 新建委托单
 * - 编辑/删除委托单
 * - 提交/取消委托单
 * 
 * 扩展点：
 * - 可添加批量操作
 * - 可添加导出功能
 * - 可添加高级筛选
 */
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const queryParams = reactive({
  page: 1,
  page_size: 20,
  status: '',
  search: '',
})

// 状态选项
const statusOptions = [
  { value: '', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'submitted', label: '已提交' },
  { value: 'received', label: '已收样' },
  { value: 'testing', label: '试验中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
]

// 获取列表数据
const fetchData = async () => {
  loading.value = true
  try {
    // TODO: 调用接口获取数据
    // const res = await getCommissionList(queryParams)
    // tableData.value = res.data.results
    // total.value = res.data.total
    
    // 模拟数据
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryParams.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  queryParams.status = ''
  queryParams.search = ''
  queryParams.page = 1
  fetchData()
}

// 分页变化
const handlePageChange = (page) => {
  queryParams.page = page
  fetchData()
}

// 新建
const handleCreate = () => {
  // TODO: 打开新建对话框
  ElMessage.info('新建委托单功能待实现')
}

// 编辑
const handleEdit = (row) => {
  // TODO: 打开编辑对话框
  ElMessage.info('编辑功能待实现')
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该委托单吗？', '提示', {
    type: 'warning',
  }).then(() => {
    // TODO: 调用删除接口
    ElMessage.success('删除成功')
    fetchData()
  })
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="page-container">
    <!-- 工具栏 -->
    <div class="table-toolbar">
      <div class="left">
        <el-input
          v-model="queryParams.search"
          placeholder="搜索委托单编号/工程名称"
          style="width: 240px"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select
          v-model="queryParams.status"
          placeholder="状态"
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      <div class="right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建委托单
        </el-button>
      </div>
    </div>
    
    <!-- 表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      stripe
    >
      <el-table-column prop="code" label="委托单编号" width="160" />
      <el-table-column prop="client_name" label="委托方" width="180" />
      <el-table-column prop="project_name" label="工程名称" min-width="200" />
      <el-table-column prop="sample_name" label="样品名称" width="150" />
      <el-table-column prop="sample_quantity" label="数量" width="80" align="center" />
      <el-table-column prop="commission_date" label="委托日期" width="120" />
      <el-table-column prop="status_display" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="queryParams.page"
        :page-size="queryParams.page_size"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
// 获取状态类型
function getStatusType(status) {
  const types = {
    draft: 'info',
    submitted: 'primary',
    received: 'warning',
    testing: 'warning',
    completed: 'success',
    cancelled: 'danger',
  }
  return types[status] || 'info'
}
</script>

<style lang="scss" scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
