<template>
  <div class="app">
    <header class="header">
      <div class="header-content">
        <h1>Memory Management | 内存管理</h1>
        <h3>2351883 陈奕名</h3>
      </div>
    </header>

    <main class="container">
      <div class="layout-container">
        <div class="layout-left">
          <div class="card">
            <SimulationControls
              title="请求分页分配方式模拟"
              :buttons="simulationButtons"
            />
          </div>
        </div>
        
        <div class="layout-right">
          <div class="card">
            <SimulationResults
              :memory-state="memoryState"
              :page-faults="pageFaults"
              :page-fault-rate="pageFaultRate"
              :execution-time="executionTime"
            />
          </div>
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>操作系统课程设计 © 2025</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import SimulationControls from './components/SimulationControls.vue'
import SimulationResults from './components/SimulationResults.vue'
import { runSimulation, getSimulationName, simulationAlgorithms } from './services/simulationService.js'

const memoryState = ref([])
const pageFaults = ref(0)
const pageFaultRate = ref(0)
const executionTime = ref(0)

function runAlgorithm(algorithm) {
  const result = runSimulation(algorithm)
  
  memoryState.value = result.logs
  pageFaults.value = result.pageFaults
  pageFaultRate.value = result.pageFaultRate
  executionTime.value = result.executionTime
  
  ElMessage({
    showClose: true,
    message: `模拟 ${getSimulationName(algorithm)} 置换算法已完成`,
    type: 'success',
    duration: 2000
  })
}

function resetSimulation() {
  memoryState.value = []
  pageFaults.value = 0
  pageFaultRate.value = 0
  executionTime.value = 0
  
  ElMessage({
    showClose: true,
    message: '请求分页分配方式模拟已重置',
    type: 'info',
    duration: 2000
  })
}

const simulationButtons = computed(() => [
  {
    label: '模拟先进先出（FIFO）算法',
    action: () => runAlgorithm(simulationAlgorithms.fifo)
  },
  {
    label: '模拟最近最少使用（LRU）算法',
    action: () => runAlgorithm(simulationAlgorithms.lru)
  },
  {
    label: '重置',
    action: resetSimulation
  }
])
</script>

<style>
:root {
  --primary-color: #409eff;
  --secondary-color: #67c23a;
  --accent-color: #f56c6c;
  --text-color: #303133;
  --light-text: #606266;
  --border-color: #dcdfe6;
  --background-color: #f5f7fa;
  --card-background: #ffffff;
  --shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: var(--primary-color);
  color: white;
  padding: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  padding: 0 20px;
}

.header h1 {
  margin: 0;
  font-size: 1.8rem;
}

.header h3 {
  margin: 8px 0 0;
  font-weight: normal;
  opacity: 0.8;
  font-size: 1rem;
}

.container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.layout-container {
  display: flex;
  width: 100%;
  gap: 24px;
  align-items: flex-start;
}

.layout-left {
  flex: 1;
  min-width: 280px;
  max-width: 350px;
}

.layout-right {
  flex: 2;
}

.card {
  background-color: var(--card-background);
  border-radius: 8px;
  box-shadow: var(--shadow);
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.footer {
  background-color: var(--text-color);
  color: white;
  text-align: center;
  padding: 12px 0;
  margin-top: 24px;
  font-size: 0.9rem;
}

.footer p {
  margin: 0;
  opacity: 0.8;
}

@media (max-width: 900px) {
  .layout-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .layout-left, .layout-right {
    width: 100%;
    max-width: none;
  }
  
  .card {
    padding: 16px;
  }
}

@media (max-width: 600px) {
  .container {
    padding: 12px 8px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .header h3 {
    font-size: 0.9rem;
  }
}
</style>
