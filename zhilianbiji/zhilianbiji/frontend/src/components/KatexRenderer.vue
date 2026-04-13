<template>
  <div>
    <div 
      v-if="displayMode" 
      class="katex-display" 
      ref="katexRef"
    ></div>
    <span 
      v-else 
      class="katex-inline" 
      ref="katexRef"
    ></span>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const props = defineProps({
  formula: {
    type: String,
    required: true
  },
  displayMode: {
    type: Boolean,
    default: false
  }
})

const katexRef = ref(null)

function renderFormula() {
  if (!katexRef.value || !props.formula) return
  
  try {
    katex.render(props.formula, katexRef.value, {
      displayMode: props.displayMode,
      throwOnError: false,
      strict: false
    })
  } catch (error) {
    console.error('KaTeX rendering error:', error)
    katexRef.value.textContent = props.formula
  }
}

onMounted(() => {
  nextTick(renderFormula)
})

watch(() => props.formula, () => {
  nextTick(renderFormula)
})
</script>

<style scoped>
.katex-display {
  display: block;
  text-align: center;
  margin: 1em 0;
}

.katex-inline {
  display: inline;
}
</style>
