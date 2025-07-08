<template>
  <div class="chat-input">
    <textarea
      v-model="message"
      rows="4"
      class="input-area"
      placeholder="请输入你的问题..."
    ></textarea>
    <button
      class="send-button"
      @click="sendMessage"
      :disabled="!message || loading"
    >
      <span v-if="loading" class="loader"></span>
      {{ loading ? '生成中...' : '发送问题' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const emit = defineEmits(['send'])
// const props = defineProps({ loading: Boolean })
const message = ref('')

const sendMessage = () => {
  if (message.value.trim()) {
    emit('send', message.value)
    message.value = ''
  }
}
</script>

<style>
.chat-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-area {
  resize: vertical;
  padding: 12px;
  font-size: 1rem;
  border: 1.5px solid #d1d5db; /* 灰色边框 */
  border-radius: 8px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.input-area:focus {
  outline: none;
  border-color: #2563eb; /* 蓝色 */
  box-shadow: 0 0 5px rgba(37, 99, 235, 0.5);
}

.send-button {
  background-color: #2563eb;
  color: white;
  font-weight: 600;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #1e40af;
}

.send-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 简单旋转动画的loader */
.loader {
  width: 16px;
  height: 16px;
  border: 3px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
