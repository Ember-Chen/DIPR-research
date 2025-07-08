<template>
  <div class="app-container">
    <div class="content-wrapper">
      <h1 class="title">DIPR-research</h1>
      <ChatInput @send="handleSend" :loading="loading" />

      <!-- 加载中提示 -->
      <div v-if="loading" class="loading-tip">
        正在生成报告，请稍候...
      </div>

      <ReportDisplay :reportData="reportData" v-if="reportData" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatInput from './components/ChatInput.vue'
import ReportDisplay from './components/ReportDisplay.vue'

const ws = new WebSocket('ws://localhost:8000/ws')
const reportData = ref(null)
const loading = ref(false)

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  reportData.value = data
  loading.value = false
}

const handleSend = (message) => {
  loading.value = true
  ws.send(message)
}
</script>

<style>
.app-container {
  min-height: 100vh;
  background: #f9fafb; /* 浅灰背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  box-sizing: border-box;
}

.content-wrapper {
  max-width: 640px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.title {
  font-size: 2.25rem; /* 36px */
  font-weight: 800;
  color: #2563eb; /* 蓝色 */
  text-align: center;
  margin: 0;
}

.loading-tip {
  margin-top: 16px;
  padding: 12px;
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
}
</style>
