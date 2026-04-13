<template>
  <div class="latex-test-container">
    <div class="test-header">
      <h1>LaTeX 公式渲染测试</h1>
      <p class="subtitle">使用 KaTeX 渲染数学公式</p>
    </div>

    <div class="input-section">
      <el-input
        v-model="inputFormula"
        placeholder="输入 LaTeX 公式，例如: E=mc^2"
        class="formula-input"
      />
      <el-button type="primary" @click="renderInput">渲染公式</el-button>
    </div>

    <div class="result-section">
      <h3>渲染结果：</h3>
      <div class="result-box">
        <KatexRenderer :formula="inputFormula" :display-mode="true" />
      </div>
    </div>

    <div class="examples-section">
      <h3>常用公式示例：</h3>
      <div class="examples-grid">
        <div class="example-card" v-for="(example, index) in examples" :key="index">
          <div class="example-label">{{ example.name }}</div>
          <div class="example-formula">{{ example.formula }}</div>
          <div class="example-render">
            <KatexRenderer :formula="example.formula" :display-mode="true" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import KatexRenderer from '../components/KatexRenderer.vue'

const inputFormula = ref('E=mc^2')

const examples = [
  {
    name: '质能方程',
    formula: 'E = mc^2'
  },
  {
    name: '勾股定理',
    formula: 'a^2 + b^2 = c^2'
  },
  {
    name: '微积分基本定理',
    formula: '\\int_a^b f(x) dx = F(b) - F(a)'
  },
  {
    name: '欧拉公式',
    formula: 'e^{i\\pi} + 1 = 0'
  },
  {
    name: '正态分布',
    formula: 'f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}'
  },
  {
    name: '矩阵乘法',
    formula: 'A_{ij} = \\sum_{k=1}^n B_{ik} C_{kj}'
  }
]

function renderInput() {
  console.log('渲染公式:', inputFormula.value)
}
</script>

<style scoped>
.latex-test-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px;
}

.test-header {
  text-align: center;
  margin-bottom: 30px;
}

.test-header h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 10px;
}

.subtitle {
  color: #999;
  margin: 0;
}

.input-section {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.formula-input {
  flex: 1;
}

.result-section {
  background: #f9f9f9;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
}

.result-section h3 {
  margin: 0 0 15px;
  color: #666;
}

.result-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.examples-section h3 {
  margin: 0 0 20px;
  color: #333;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.example-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.example-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.example-formula {
  font-family: monospace;
  font-size: 13px;
  color: #666;
  background: #f5f5f5;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  word-break: break-all;
}

.example-render {
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
