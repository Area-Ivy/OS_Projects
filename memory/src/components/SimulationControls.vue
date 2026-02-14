<template>
  <div class="simulation-controls">
    <div class="title-section">
      <h2>{{ title }}</h2>
    </div>

    <div class="buttons-container">
      <el-button 
        v-for="(button, index) in buttons" 
        :key="index"
        :plain="true" 
        :type="'primary'"
        size="large" 
        round 
        class="control-button"
        @click="button.action">
        <div class="button-content">
          <component :is="getButtonIcon(button.label)" class="button-icon" />
          <span class="button-text">{{ button.label }}</span>
        </div>
      </el-button>
    </div>

    <div class="description-section">
      <h4>算法说明</h4>
      <div class="algorithm-description">
        <div class="algorithm-card">
          <h5>FIFO (先进先出)</h5>
          <p>最早进入内存的页面最先被置换出去。FIFO算法实现简单，但可能会导致频繁使用的页面被置换出去。</p>
        </div>
        <div class="algorithm-card">
          <h5>LRU (最近最少使用)</h5>
          <p>最长时间未被访问的页面将被置换出去。LRU算法能较好地反映程序局部性原理，但实现较为复杂。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Sort, Timer, RefreshRight } from '@element-plus/icons-vue';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  buttons: {
    type: Array,
    required: true
  }
});

const getButtonIcon = (label) => {
  if (label.includes('FIFO')) {
    return Sort;
  } else if (label.includes('LRU')) {
    return Timer;
  } else if (label.includes('重置')) {
    return RefreshRight;
  }
  return null;
};
</script>

<style scoped>
.simulation-controls {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.title-section {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 12px;
  width: 100%;
}

.title-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 3px;
  background-color: var(--primary-color);
  border-radius: 3px;
}

h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.6rem;
}

.buttons-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: 24px;
  align-items: stretch;
  gap: 12px;
}

.control-button {
  width: 100%;
  justify-content: flex-start;
  padding-left: 20px !important;
  height: 40px !important;
  margin: 0 !important;
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 100%;
}

.button-icon {
  margin-right: 10px;
  font-size: 16px;
}

.button-text {
  white-space: nowrap;
  font-size: 14px;
}

.description-section {
  width: 100%;
  margin-top: 5px;
}

h4 {
  color: var(--text-color);
  font-size: 1.1rem;
  margin: 0 0 12px 0;
  position: relative;
  padding-left: 12px;
}

h4::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background-color: var(--primary-color);
  border-radius: 2px;
}

.algorithm-description {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.algorithm-card {
  background-color: #f9f9f9;
  border-radius: 6px;
  padding: 12px;
  border-left: 4px solid var(--primary-color);
}

.algorithm-card h5 {
  margin: 0 0 8px;
  color: var(--primary-color);
  font-size: 1rem;
}

.algorithm-card p {
  margin: 0;
  color: var(--light-text);
  font-size: 0.9rem;
  line-height: 1.5;
}

:deep(.el-button) {
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@media (max-width: 900px) {
  .buttons-container {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .control-button {
    flex: 1;
    min-width: 180px;
  }
}

@media (max-width: 600px) {
  h2 {
    font-size: 1.4rem;
  }
  
  .buttons-container {
    flex-direction: column;
  }
  
  .algorithm-card h5 {
    font-size: 0.95rem;
  }
  
  .algorithm-card p {
    font-size: 0.85rem;
  }
}
</style> 