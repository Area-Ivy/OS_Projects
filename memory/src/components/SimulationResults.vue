<template>
  <div class="simulation-results">
    <div class="results-header">
      <h3 class="results-title">模拟结果</h3>
    </div>

    <div class="stats-container">
      <div class="stats-card">
        <div class="stat-item">
          <div class="stat-icon page-faults">
            <warning-filled />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ pageFaults }}</div>
            <div class="stat-label">缺页数</div>
          </div>
        </div>

        <div class="stat-item">
          <div class="stat-icon page-fault-rate">
            <data-analysis />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ (pageFaultRate * 100).toFixed(2) }}%</div>
            <div class="stat-label">缺页率</div>
          </div>
        </div>

        <div class="stat-item">
          <div class="stat-icon execution-time">
            <timer />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ executionTime }}</div>
            <div class="stat-label">执行时间 (毫秒)</div>
          </div>
        </div>
      </div>
    </div>

    <div class="table-wrapper">
      <el-table 
        :data="memoryState" 
        stripe 
        border
        max-height="500"
        class="results-table"
        :header-cell-style="{ 
          backgroundColor: '#f5f7fa',
          color: '#606266',
          fontWeight: 'bold'
        }"
      >
        <el-table-column prop="id" label="编号" width="60" align="center" />
        <el-table-column prop="instructionId" label="指令代号" width="100" align="center" />
        <el-table-column label="内存块" align="center">
          <el-table-column label="内存块 1" width="80" align="center">
            <template #default="scope">
              <span :class="{ 'highlighted-cell': isNewlyAddedPage(scope.row, 0) }">
                {{ scope.row.pages[0] ? scope.row.pages[0] : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="内存块 2" width="80" align="center">
            <template #default="scope">
              <span :class="{ 'highlighted-cell': isNewlyAddedPage(scope.row, 1) }">
                {{ scope.row.pages[1] ? scope.row.pages[1] : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="内存块 3" width="80" align="center">
            <template #default="scope">
              <span :class="{ 'highlighted-cell': isNewlyAddedPage(scope.row, 2) }">
                {{ scope.row.pages[2] ? scope.row.pages[2] : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="内存块 4" width="80" align="center">
            <template #default="scope">
              <span :class="{ 'highlighted-cell': isNewlyAddedPage(scope.row, 3) }">
                {{ scope.row.pages[3] ? scope.row.pages[3] : '-' }}
              </span>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column prop="isPageFault" label="缺页" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.isPageFault ? 'danger' : 'success'" size="small">
              {{ scope.row.isPageFault ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="insertedBlock" label="放入" width="80" align="center">
          <template #default="scope">
            <span v-if="scope.row.insertedBlock !== '-'" class="inserted-block">
              {{ scope.row.insertedBlock }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="removedPage" label="换出" width="80" align="center">
          <template #default="scope">
            <span v-if="scope.row.removedPage !== '-'" class="removed-page">
              {{ scope.row.removedPage }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="memoryState.length === 0" class="empty-table-message">
        <p>点击左侧按钮开始模拟</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { WarningFilled, DataAnalysis, Timer, Monitor } from '@element-plus/icons-vue';

const props = defineProps({
  memoryState: {
    type: Array,
    default: () => []
  },
  pageFaults: {
    type: Number,
    default: 0
  },
  pageFaultRate: {
    type: Number,
    default: 0
  },
  executionTime: {
    type: Number,
    default: 0
  }
});

// Check if a page was newly added in this row at the specified index
const isNewlyAddedPage = (row, index) => {
  if (!row.isPageFault) return false;
  const insertedBlock = parseInt(row.insertedBlock);
  return !isNaN(insertedBlock) && insertedBlock === index + 1;
};
</script>

<style scoped>
.simulation-results {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.results-header {
  width: 100%;
  margin-bottom: 16px;
  text-align: left;
}

.results-title {
  color: var(--text-color);
  font-size: 1.4rem;
  margin: 0;
  position: relative;
  padding-left: 12px;
  display: inline-block;
}

.results-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 80%;
  background-color: var(--primary-color);
  border-radius: 2px;
}

.stats-container {
  margin: 0 0 16px;
  width: 100%;
}

.stats-card {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  border-radius: 6px;
  background-color: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  flex: 1;
  min-width: 150px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  margin-right: 15px;
  font-size: 20px;
  color: white;
}

.page-faults {
  background-color: #f56c6c;
}

.page-fault-rate {
  background-color: #e6a23c;
}

.execution-time {
  background-color: #409eff;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: bold;
  color: var(--text-color);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--light-text);
  margin-top: 3px;
}

.table-wrapper {
  width: 100%;
  box-sizing: border-box;
  padding: 0;
}

.results-table {
  width: 100% !important;
  box-sizing: border-box;
}

.highlighted-cell {
  background-color: rgba(64, 158, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: var(--primary-color);
}

.inserted-block {
  color: var(--secondary-color);
  font-weight: bold;
}

.removed-page {
  color: var(--accent-color);
  font-weight: bold;
}

.empty-table-message {
  text-align: center;
  padding: 10px 0;
  color: var(--light-text);
  font-size: 14px;
  width: 100%;
  border: 1px solid #ebeef5;
  border-top: none;
  background-color: #fff;
}

@media (max-width: 900px) {
  .stats-card {
    gap: 10px;
  }
  
  .stat-item {
    padding: 8px 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
    margin-right: 10px;
  }
  
  .stat-value {
    font-size: 1.2rem;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
}

@media (max-width: 600px) {
  .stats-card {
    flex-direction: column;
    gap: 8px;
  }
  
  .stat-item {
    width: 100%;
  }
  
  .results-title {
    font-size: 1.3rem;
  }
}
</style> 