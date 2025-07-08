<template>
  <div class="report-display">
    <div class="report-content" v-html="renderedHtml"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  reportData: Object
})

const renderedHtml = computed(() => {
  let html = `<h3>Question:</h3>` + 
             `<p>${props.reportData.question}</p>`
  props.reportData.sub_qs_w_anss.forEach((task, index) => {
    html += `<h4>Sub Question ${index + 1}: ${task.sub_q}</h4><p>Answer: ${task.sub_ans}</p>`
  })
  html += `<h3>Final Answer: <u>${props.reportData.final_ans}</u> </h3>`
  return html
})
</script>

<style>
.report-display {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgb(0 0 0 / 0.1);
  padding: 24px;
  border: 1px solid #e5e7eb;
}

.report-display h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 16px;
}

.report-content h3 {
  font-size: 1.25rem;
  margin-bottom: 12px;
  color: #1e40af;
}

.report-content h4 {
  font-weight: 600;
  margin-top: 16px;
  margin-bottom: 6px;
  color: #3b82f6;
}

.report-content p {
  margin: 0 0 12px;
  line-height: 1.5;
  color: #4b5563;
}
</style>
