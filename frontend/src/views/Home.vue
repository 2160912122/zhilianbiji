<template>
<<<<<<< HEAD
  <!-- 全屏加载遮罩 -->
  <div v-if="loading" class="loading-screen">
    <div class="loading-content">
      <h1 class="loading-logo">智联笔记</h1>
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载智能体验...</p>
    </div>
  </div>

  <!-- 主内容（加载完成后显示） -->
  <div v-else class="home-container">
=======
  <div class="home-container">
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
    <!-- 动态粒子背景 -->
    <div class="particle-bg" ref="particleBg"></div>

    <!-- 顶部导航栏 - 玻璃态 + 滚动动画 -->
    <header class="home-header" :class="{ 'header-scrolled': isScrolled }">
      <div class="header-content">
        <div class="logo" @click="navigateToHome">
          <h1>智联笔记</h1>
          <span class="logo-badge">AI+</span>
        </div>
        <div class="header-actions">
<<<<<<< HEAD
=======
          <div class="download-badges">
            <span class="download-label">多端下载：</span>
            <a href="#" class="badge"><i class="el-icon-mobile-phone"></i> iOS</a>
            <a href="#" class="badge"><i class="el-icon-android"></i> Android</a>
            <a href="#" class="badge"><i class="el-icon-monitor"></i> Windows</a>
            <a href="#" class="badge"><i class="el-icon-mac"></i> macOS</a>
          </div>
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
          <button @click="navigateToLogin" class="login-btn">登录</button>
          <button @click="navigateToRegister" class="register-btn">注册</button>
        </div>
      </div>
    </header>

    <!-- 英雄区域 - 视差 + 渐变浮动 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1>
            记录，成为<br />
            <span class="gradient-text">更好的自己</span>
          </h1>
          <p>AI工具赋能 | 智能问答 | All-in-One编辑器</p>
<<<<<<< HEAD
          <div class="hero-stats">
            <div class="stat"><span>持续</span> 创新迭代</div>
            <div class="stat-dot">·</div>
            <div class="stat"><span>众多</span> 用户信赖</div>
            <div class="stat-dot">·</div>
            <div class="stat"><span>智能</span> 知识管理</div>
          </div>
=======
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
          <div class="hero-actions">
            <button @click="navigateToRegister" class="primary-btn">
              开始创作 <i class="el-icon-arrow-right"></i>
            </button>
            <button @click="navigateToLogin" class="secondary-btn">已有账号？ 登录</button>
          </div>
<<<<<<< HEAD
=======
          <div class="hero-stats">
            <div class="stat"><span>10年</span> 产品沉淀</div>
            <div class="stat"><span>亿万</span> 用户选择</div>
            <div class="stat"><span>99.9%</span> 数据安全</div>
          </div>
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
        </div>
        <div class="hero-image">
          <div class="floating-card">
            <img src="https://picsum.photos/id/20/600/400" alt="智能笔记界面" />
          </div>
          <div class="floating-element elem-1"><i class="el-icon-magic-stick"></i></div>
          <div class="floating-element elem-2"><i class="el-icon-upload"></i></div>
        </div>
      </div>
      <div class="scroll-indicator" @click="scrollToFeatures">
        <span>探索更多</span>
        <i class="el-icon-caret-bottom"></i>
      </div>
    </section>

<<<<<<< HEAD
    <!-- AI 功能专区 -->
=======
    <!-- AI 功能专区 - 具体化、场景化 -->
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
    <section class="ai-features-section">
      <div class="section-header">
        <h2>AI 赋能，智能创作新体验</h2>
        <p class="section-sub">不只是记录，更是你的智慧副脑</p>
      </div>
      <div class="ai-features-grid">
        <div class="ai-card" v-for="(ai, idx) in aiFeatures" :key="idx">
          <div class="ai-icon">
            <el-icon size="24">
              <component :is="ai.icon" />
            </el-icon>
          </div>
          <h3>{{ ai.title }}</h3>
          <p>{{ ai.desc }}</p>
        </div>
      </div>
    </section>

<<<<<<< HEAD
    <!-- 特性展示 -->
=======
    <!-- 特性展示 - 卡片交错动画 -->
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
    <section class="features-section" ref="featuresSection">
      <div class="section-header">
        <h2>专业强大的编辑器</h2>
        <p class="section-sub">支持5种文稿类型，让记录得心应手</p>
      </div>
      <div class="features-grid">
<<<<<<< HEAD
        <div class="feature-card" v-for="(feature, idx) in features" :key="idx">
=======
        <div class="feature-card" v-for="(feature, idx) in features" :key="idx" :style="{ animationDelay: `${idx * 0.1}s` }">
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
          <div class="feature-icon">
            <el-icon size="24">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.desc }}</p>
          <div class="card-glow"></div>
        </div>
      </div>
    </section>

<<<<<<< HEAD
    <!-- 核心功能 -->
    <section class="tools-section">
      <div class="section-header">
        <h2>核心功能模块</h2>
        <p class="section-sub">集成多种实用工具，满足知识管理全场景需求</p>
      </div>
      <div class="tools-grid">
        <div class="tool-card" v-for="(tool, idx) in tools" :key="tool.name" @mouseenter="handleToolHover(idx)" @mouseleave="handleToolLeave(idx)">
          <div class="tool-icon-wrapper">
            <i :class="tool.icon"></i>
          </div>
          <h3>{{ tool.name }}</h3>
          <p class="tool-desc">{{ tool.desc }}</p>
          <div class="tool-glow"></div>
=======
    <!-- 9大效率工具 -->
    <section class="tools-section">
      <div class="section-header">
        <h2>9大效率工具，让高效成为习惯</h2>
        <p class="section-sub">内嵌多种先进工具，多渠道内容一键收藏</p>
      </div>
      <div class="tools-grid">
        <div class="tool-item" v-for="tool in tools" :key="tool.name">
          <i :class="tool.icon"></i>
          <span>{{ tool.name }}</span>
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
        </div>
      </div>
    </section>

    <!-- 使用场景 -->
    <section class="use-cases-section">
      <div class="section-header">
        <h2>多场景解决方案</h2>
        <p class="section-sub">让灵感信手拈来，满足工作、生活、学习中的各个场景</p>
      </div>
      <div class="use-cases-grid">
        <div class="use-case-card" v-for="(useCase, idx) in useCases" :key="idx">
          <div class="use-case-icon">
            <el-icon size="24">
              <component :is="useCase.icon" />
            </el-icon>
          </div>
          <h3>{{ useCase.title }}</h3>
          <p>{{ useCase.desc }}</p>
        </div>
      </div>
    </section>

<<<<<<< HEAD
    <!-- 用户评价 -->
=======
    <!-- 统计亮点 - 数字滚动 -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-item" v-for="(stat, idx) in stats" :key="idx">
          <h4><span :ref="el => statRefs[idx] = el" class="stat-number" :data-target="stat.value">0</span>{{ stat.unit }}</h4>
          <p>{{ stat.label }}</p>
        </div>
      </div>
    </div>

    <!-- 用户评价 - 3D倾斜卡片 + 时长概念 -->
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
    <section class="testimonials-section">
      <h2>亿万用户的共同选择</h2>
      <div class="testimonials-grid">
        <div class="testimonial-card" v-for="(testimonial, idx) in testimonials" :key="idx" @mousemove="handleTilt($event, idx)" @mouseleave="resetTilt(idx)">
          <div class="testimonial-avatar">
<<<<<<< HEAD
            <el-icon>
              <component :is="testimonial.avatar" />
            </el-icon>
=======
           <el-icon>
            <component :is="testimonial.avatar" />
          </el-icon>
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
          </div>
          <p>“{{ testimonial.text }}”</p>
          <div class="testimonial-meta">
            <div class="testimonial-name">
              <i class="el-icon-check" style="color: #2c5f8a;"></i> {{ testimonial.name }}
            </div>
            <div class="testimonial-days"><i class="el-icon-time"></i> {{ testimonial.days }}天 · 忠实用户</div>
          </div>
          <div class="card-tilt-effect" :ref="el => tiltRefs[idx] = el"></div>
        </div>
      </div>
    </section>

    <!-- 常见问题 -->
    <section class="faq-section">
      <div class="section-header">
        <h2>常见问题</h2>
        <p class="section-sub">解答你关心的问题</p>
      </div>
      <div class="faq-grid">
        <div class="faq-item" v-for="(faq, idx) in faqs" :key="idx">
          <h3>{{ faq.question }}</h3>
          <p>{{ faq.answer }}</p>
        </div>
      </div>
    </section>

<<<<<<< HEAD
    <!-- CTA 区域 -->
=======
    <!-- CTA 区域 - 渐变粒子按钮 -->
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
    <div class="cta-section">
      <div class="cta-inner">
        <h3>开启你的智能笔记之旅</h3>
        <p>加入亿万知识工作者的选择，让每个想法都产生价值</p>
        <button @click="navigateToRegister" class="cta-btn">
          免费注册体验 <i class="el-icon-arrow-right"></i>
          <span class="btn-particles"></span>
        </button>
      </div>
    </div>

    <!-- 底部 -->
    <footer class="home-footer">
      <div class="footer-content">
        <div class="footer-logo">
          <h2>智联笔记</h2>
          <p>连接 · 洞见 · 创造</p>
<<<<<<< HEAD
=======
          <div class="security-badge">
            <i class="el-icon-lock"></i> 银行级加密 · 10年数据不丢失
          </div>
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
        </div>
        <div class="footer-links">
          <div class="link-group">
            <h3>产品</h3>
            <a href="#">智能笔记</a>
            <a href="#">AI Copilot</a>
            <a href="#">模板中心</a>
            <a href="#">下载客户端</a>
          </div>
          <div class="link-group">
            <h3>支持</h3>
            <a href="#">帮助文档</a>
            <a href="#">社区论坛</a>
            <a href="#">反馈建议</a>
            <a href="#">常见问题</a>
          </div>
          <div class="link-group">
            <h3>公司</h3>
            <a href="#">关于我们</a>
            <a href="#">隐私条款</a>
            <a href="#">服务协议</a>
            <a href="#">加入我们</a>
          </div>
          <div class="link-group">
            <h3>关注我们</h3>
            <a href="#">微信公众号</a>
            <a href="#">微博</a>
            <a href="#">GitHub</a>
            <a href="#">知乎</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
<<<<<<< HEAD
        <p>© 2026 智联笔记 · 让知识驱动未来 · 网页持续创新迭代，亿万用户的共同选择</p>
=======
        <p>© 2026 智联笔记 · 让知识驱动未来 · 网易10年产品沉淀，亿万用户的共同选择</p>
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
      </div>
    </footer>
  </div>
</template>

<script setup>
<<<<<<< HEAD
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  HelpFilled, Edit, Reading, Document,
  Grid, Picture, Share, FolderOpened, Camera,
  Suitcase, Notebook, User, Flag, Message, Briefcase
} from '@element-plus/icons-vue'

// ========== SEO ==========
document.title = '智联笔记 - AI 智能笔记工具 | 亿万用户的知识管理平台'

// 设置meta标签
const setMetaTag = (name, content) => {
  let tag = document.querySelector(`meta[name="${name}"]`)
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute('name', name)
    document.head.appendChild(tag)
  }
  tag.setAttribute('content', content)
}

setMetaTag('description', '智联笔记是一款集文档笔记、智能表格、Markdown、白板、思维导图、流程图于一体的知识管理平台。支持知识图谱、回收站、管理员功能，为知识工作者打造高效创作体验。')
setMetaTag('keywords', '智能笔记,知识管理,文档笔记,智能表格,Markdown,白板,思维导图,流程图,知识图谱')
setMetaTag('author', '智联笔记团队')

// 设置Open Graph标签
const setOgTag = (property, content) => {
  let tag = document.querySelector(`meta[property="${property}"]`)
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute('property', property)
    document.head.appendChild(tag)
  }
  tag.setAttribute('content', content)
}

setOgTag('og:title', '智联笔记 - 让每个想法都产生价值')
setOgTag('og:description', 'AI 赋能的智能笔记平台，支持文档、表格、思维导图、网页剪藏等 9 大效率工具。')
setOgTag('og:type', 'website')
setOgTag('og:url', 'https://yourdomain.com')
setOgTag('og:image', 'https://yourdomain.com/og-image.jpg')

// 设置Twitter标签
setMetaTag('twitter:card', 'summary_large_image')

// 设置canonical链接
const setCanonicalLink = (href) => {
  let link = document.querySelector('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', href)
}

setCanonicalLink('https://yourdomain.com')

// ========== 加载状态 ==========
const loading = ref(true)
const finishLoading = () => {
  loading.value = false
}

// ========== 原有逻辑 ==========
const router = useRouter()
const isScrolled = ref(false)
const featuresSection = ref(null)
const tiltRefs = ref([])

=======
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  HelpFilled, Edit, Reading, Document,
  Grid,
  Picture,
  Share,
  FolderOpened,
  Camera,
  Suitcase,
  Notebook,
  User,
  Flag

} from '@element-plus/icons-vue'

const router = useRouter()

// 滚动状态
const isScrolled = ref(false)
const featuresSection = ref(null)

// 统计数据引用和滚动动画
const statRefs = ref([])
const stats = [
  { value: 10, unit: '年', label: '产品沉淀' },
  { value: 100, unit: 'M+', label: '用户选择' },
  { value: 99.9, unit: '%', label: '数据安全' }
]

// AI 功能数据
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const aiFeatures = [
  { icon: HelpFilled, title: '智能问答', desc: '检索全部笔记，智能梳理要点，AI获取知识，一键插入笔记' },
  { icon: Edit, title: '场景助手', desc: '涵盖头脑风暴、写文章等20多项场景，速读内容概要，提炼核心观点' },
  { icon: Reading, title: '随心提问', desc: '基于你的全部笔记，AI将快速检索并智能梳理要点，给出精准回答' }
]

<<<<<<< HEAD
const features = [
  { icon: Document, title: '文档', desc: '一站式文稿创作，多格式兼容，让每一次记录都顺滑高效' },
  { icon: Grid, title: '表格', desc: '智能表格处理，数据整理更高效，支持复杂计算和可视化' },
  { icon: Picture, title: 'Markdown', desc: '沉浸式Markdown编辑，实时预览，让写作更专注' },
  { icon: Share, title: '白板', desc: '多人实时协作，自由绘制，激发创意无限可能' },
  { icon: FolderOpened, title: '脑图', desc: '结构化思维整理，层级分明，理清思路脉络' },
  { icon: Camera, title: '流程图', desc: '业务流程可视化，清晰展示，提升沟通效率' }
]

const tools = [
  { name: 'AI助手', icon: 'el-icon-magic-stick', desc: '智能问答，知识检索' },
  { name: 'Markdown', icon: 'el-icon-tickets', desc: '沉浸式编辑，实时预览' },
  { name: '思维导图', icon: 'el-icon-s-tree', desc: '结构化思维整理' },
  { name: '知识图谱', icon: 'el-icon-network', desc: '知识关联，智能推荐' },
  { name: '团队协作', icon: 'el-icon-user-solid', desc: '多人协作，实时同步' }
]

=======
// 特性数据
const features = [
  { icon: Document, title: '文档', desc: '专业强大的编辑器，支持5种文稿类型，随心所欲开启顺滑的创作编辑体验' },
  { icon: Grid, title: '表格', desc: '智能表格处理，数据整理更高效，支持复杂计算和可视化' },
  { icon: Picture, title: 'Markdown', desc: '沉浸式Markdown编辑，实时预览，让写作更专注' },
  { icon: Share, title: '双链笔记', desc: '双向链接，构建知识网络，让知识不再孤立' },
  { icon: FolderOpened, title: '内容收藏', desc: '多渠道内容一键收藏，构建你的私人知识库' },
  { icon: Camera, title: 'OCR扫描', desc: '图片文字智能识别，扫描件一键转文字' }
]

// 工具数据
const tools = [
  { name: 'AI助手', icon: 'el-icon-magic-stick' },
  { name: '双链笔记', icon: 'el-icon-share' },
  { name: '网页剪藏', icon: 'el-icon-folder-opened' },
  { name: 'OCR扫描', icon: 'el-icon-camera' },
  { name: '语音速记', icon: 'el-icon-microphone' },
  { name: 'Markdown', icon: 'el-icon-tickets' },
  { name: '思维导图', icon: 'el-icon-s-operation' },
  { name: '多端同步', icon: 'el-icon-upload' },
  { name: '团队协作', icon: 'el-icon-user' }
]

// 使用场景数据
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const useCases = [
  { icon: Suitcase, title: '商务办公', desc: '会议记录、项目规划、客户资料管理，让工作更高效' },
  { icon: Reading, title: '学习教育', desc: '课堂笔记、复习资料、论文写作，让学习更轻松' },
  { icon: Picture, title: '创意设计', desc: '灵感记录、设计草图、项目策划，让创意不丢失' },
  { icon: Notebook, title: '个人生活', desc: '日记、旅行计划、购物清单，让生活更有条理' }
]

<<<<<<< HEAD
=======
// 评价数据 - 增加天数概念
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const testimonials = [
  { avatar: User, text: '用过很多文档笔记类的产品，智联笔记是最深得我心的了，悄悄记录了我的写作灵感、书评笔记、还有更多的生活故事。', name: '产品经理·李明', days: '2340' },
  { avatar: Picture, text: '5年来的书单、5年来积累的文案、5年来记下的笔记，都存在了云笔记里。就好像一个随身的资料库、魔法盒、工具箱。', name: '独立创作者·王芳', days: '1825' },
  { avatar: Flag, text: '用智联笔记写日记有多个年头了，同步功能让它们好好的保存在笔记本里，换了多部手机、电脑记录都还在。', name: '清华大学·张伟', days: '1460' },
<<<<<<< HEAD
  { avatar: Edit, text: '身为一个写手，我换了太多的写作平台，最终我定居在了智联笔记，它帮助我写下了无数故事和方案，就是我文字的温暖小家。', name: '自由撰稿人·陈晨', days: '1095' },
  { avatar: Message, text: '团队协作功能太强大了，和同事一起编辑文档效率提升了很多，实时同步让沟通变得更顺畅。', name: '项目经理·刘洋', days: '730' },
  { avatar: Briefcase, text: '作为一名律师，智联笔记帮我整理了大量的案件资料和法律条文，搜索功能让我快速找到需要的信息。', name: '执业律师·赵雪', days: '547' }
]

const faqs = [
  { question: '如何快速查找我需要的笔记？', answer: '智联笔记提供强大的全文搜索功能，支持关键词搜索、标签筛选、时间排序等多种方式，让你快速定位到需要的笔记内容。' },
  { question: '笔记可以设置访问权限吗？', answer: '当然可以，智联笔记支持为笔记设置不同的访问权限，包括公开、私有和共享，你可以灵活控制笔记的可见范围。' },
  { question: '是否支持离线使用？', answer: '是的，智联笔记支持离线使用。当你没有网络连接时，仍然可以查看和编辑笔记，网络恢复后会自动同步到云端。' },
  { question: '如何与团队成员协作？', answer: '智联笔记支持团队协作功能，你可以邀请团队成员共同编辑笔记，设置不同的访问权限，实时查看协作状态。' },
  { question: 'AI助手可以提供哪些帮助？', answer: 'AI助手可以帮助你快速检索笔记内容、智能总结文档要点、生成文章大纲、解答知识问题，大幅提升你的工作效率。' },
  { question: '支持Markdown格式编辑吗？', answer: '是的，智联笔记内置Markdown编辑器，支持实时预览，让你专注于内容创作，享受沉浸式写作体验。' }
]

const navigateToLogin = () => router.push('/login')
const navigateToRegister = () => router.push('/register')
const navigateToHome = () => router.push('/')
=======
  { avatar: Edit, text: '身为一个写手，我换了太多的写作平台，最终我定居在了智联笔记，它帮助我写下了无数故事和方案，就是我文字的温暖小家。', name: '自由撰稿人·陈晨', days: '1095' }
]

// 常见问题数据
const faqs = [
  { question: '智联笔记如何保证数据安全？', answer: '智联笔记采用银行级加密技术，数据存储在云端，多重备份，确保数据安全可靠。同时，我们严格遵守隐私政策，保护用户数据不被泄露。' },
  { question: '支持哪些设备和平台？', answer: '智联笔记支持PC端（Windows、Mac）、移动端（iOS、Android）以及网页版，多端同步，随时随地访问你的笔记。' },
  { question: '是否支持离线使用？', answer: '是的，智联笔记支持离线使用。当你没有网络连接时，仍然可以查看和编辑笔记，网络恢复后会自动同步到云端。' },
  { question: '如何与团队成员协作？', answer: '智联笔记支持团队协作功能，你可以邀请团队成员共同编辑笔记，设置不同的访问权限，实时查看协作状态。' }
]

// 3D 倾斜效果引用
const tiltRefs = ref([])

// 导航函数
const navigateToLogin = () => router.push('/login')
const navigateToRegister = () => router.push('/register')
const navigateToHome = () => router.push('/')

>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const scrollToFeatures = () => {
  featuresSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

<<<<<<< HEAD
=======
// 数字滚动动画
const animateNumbers = () => {
  statRefs.value.forEach((el, idx) => {
    if (!el) return
    const target = stats[idx].value
    let current = 0
    const increment = target / 50
    const updateNumber = () => {
      current += increment
      if (current < target) {
        el.innerText = Math.floor(current)
        requestAnimationFrame(updateNumber)
      } else {
        el.innerText = target
      }
    }
    updateNumber()
  })
}

// 3D 倾斜效果
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const handleTilt = (e, idx) => {
  const card = e.currentTarget
  const rect = card.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  const rotateX = (y - centerY) / 20
  const rotateY = (centerX - x) / 20
  card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`
}
<<<<<<< HEAD
=======

>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const resetTilt = (idx) => {
  const card = document.querySelectorAll('.testimonial-card')[idx]
  if (card) card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)'
}

<<<<<<< HEAD
const handleToolHover = (idx) => {
  const card = document.querySelectorAll('.tool-card')[idx]
  if (card) {
    card.style.transform = 'translateY(-8px)'
    card.style.boxShadow = '0 20px 40px rgba(66, 153, 225, 0.2)'
  }
}

const handleToolLeave = (idx) => {
  const card = document.querySelectorAll('.tool-card')[idx]
  if (card) {
    card.style.transform = 'translateY(0px)'
    card.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.05)'
  }
}

=======
// 滚动监听 + 视差效果
const handleScroll = () => {
  isScrolled.value = window.scrollY > 50

  // 视差英雄区域图片
  const heroImg = document.querySelector('.hero-image .floating-card')
  if (heroImg) {
    const scrolled = window.scrollY
    heroImg.style.transform = `translateY(${scrolled * 0.05}px)`
  }

  // 检测统计区域是否可见并触发数字动画
  const statsSection = document.querySelector('.stats-section')
  if (statsSection) {
    const rect = statsSection.getBoundingClientRect()
    if (rect.top < window.innerHeight - 100 && rect.bottom > 0 && !window.numbersAnimated) {
      window.numbersAnimated = true
      animateNumbers()
    }
  }
}

// 粒子背景 (Canvas实现动态粒子)
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
const initParticles = () => {
  const canvas = document.createElement('canvas')
  const container = document.querySelector('.particle-bg')
  if (!container) return
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.width = '100%'
  canvas.style.height = '100%'
  canvas.style.pointerEvents = 'none'
  container.appendChild(canvas)
  const ctx = canvas.getContext('2d')
  let particles = []
  let animationId

  const resizeCanvas = () => {
    canvas.width = container.clientWidth
    canvas.height = container.clientHeight
  }

  const createParticles = () => {
    const particleCount = 100
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2 + 1,
        alpha: Math.random() * 0.5 + 0.2,
        speedX: (Math.random() - 0.5) * 0.3,
        speedY: (Math.random() - 0.5) * 0.2,
      })
    }
  }

  const drawParticles = () => {
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    particles.forEach(p => {
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(44, 95, 138, ${p.alpha * 0.3})`
      ctx.fill()
      p.x += p.speedX
      p.y += p.speedY
      if (p.x < 0) p.x = canvas.width
      if (p.x > canvas.width) p.x = 0
      if (p.y < 0) p.y = canvas.height
      if (p.y > canvas.height) p.y = 0
    })
    animationId = requestAnimationFrame(drawParticles)
  }

  window.addEventListener('resize', () => {
    resizeCanvas()
    particles = []
    createParticles()
  })
  resizeCanvas()
  createParticles()
  drawParticles()

  onUnmounted(() => {
    cancelAnimationFrame(animationId)
    window.removeEventListener('resize', resizeCanvas)
  })
}

onMounted(() => {
<<<<<<< HEAD
  // 监听页面完全加载
  if (document.readyState === 'complete') {
    finishLoading()
  } else {
    window.addEventListener('load', finishLoading, { once: true })
  }

  const initAfterLoad = () => {
    initParticles()

    const handleNavScroll = () => {
      isScrolled.value = window.scrollY > 50
      const heroImg = document.querySelector('.hero-image .floating-card')
      if (heroImg) {
        heroImg.style.transform = `translateY(${window.scrollY * 0.05}px)`
      }
      document.querySelectorAll('.floating-element').forEach((elem, i) => {
        elem.style.transform = `translateY(${window.scrollY * 0.02 * (i + 1)}px)`
      })
    }
    window.addEventListener('scroll', handleNavScroll)
    handleNavScroll()

    // ✅ 关键修改：支持反复触发动画
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const target = entry.target
        if (entry.isIntersecting) {
          target.classList.add('in-view')
        } else {
          target.classList.remove('in-view')
        }
      })
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    })

    const targets = document.querySelectorAll(`
      .ai-features-section,
      .features-section,
      .tools-section,
      .use-cases-section,
      .testimonials-section,
      .faq-section,
      .ai-card,
      .feature-card,
      .tool-card,
      .use-case-card,
      .testimonial-card,
      .faq-item
    `)
    targets.forEach(el => observer.observe(el))

    onUnmounted(() => {
      window.removeEventListener('scroll', handleNavScroll)
      observer.disconnect()
    })
  }

  nextTick(() => {
    if (!loading.value) {
      initAfterLoad()
    } else {
      const watcher = setInterval(() => {
        if (!loading.value) {
          clearInterval(watcher)
          initAfterLoad()
        }
      }, 100)
    }
  })
})
</script>

<style scoped>
/* ========== 加载动画 ========== */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #f0f5fb, #ffffff);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
}

.loading-logo {
  font-size: 2.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1F2B3C, #2C5F8A);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  margin-bottom: 2rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(44, 95, 138, 0.2);
  border-top: 4px solid #2c5f8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #5c6f87;
  font-size: 1.1rem;
}

/* ========== 滚动动画核心 ========== */
.ai-features-section,
.features-section,
.tools-section,
.use-cases-section,
.testimonials-section,
.faq-section,
.ai-card,
.feature-card,
.tool-card,
.use-case-card,
.testimonial-card,
.faq-item {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.in-view {
  opacity: 1 !important;
  transform: translateY(0) !important;
}

/* ========== 以下为原有样式（保持不变） ========== */
=======
  window.addEventListener('scroll', handleScroll)
  handleScroll()
  initParticles()

  // 添加滚动触发动画类
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view')
      }
    })
  }, { threshold: 0.2 })

  document.querySelectorAll('.feature-card, .testimonial-card, .stat-item, .ai-card, .use-case-card, .tool-item, .faq-item').forEach(el => {
    observer.observe(el)
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 基础样式与动画定义 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background: #fafcff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  overflow-x: hidden;
  position: relative;
<<<<<<< HEAD
  scroll-behavior: smooth;
=======
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
}

.particle-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

<<<<<<< HEAD
=======
/* 导航栏 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.home-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.72);
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
}

.header-scrolled {
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(25px);
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.9rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  cursor: pointer;
  display: flex;
  align-items: baseline;
  gap: 6px;
  transition: transform 0.2s;
}

.logo:hover {
  transform: scale(1.02);
}

.logo h1 {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1F2B3C, #2C5F8A);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.logo-badge {
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(44, 95, 138, 0.12);
  padding: 2px 8px;
  border-radius: 40px;
  color: #2c5f8a;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.download-badges {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  margin-right: 1rem;
}

.download-label {
  font-size: 0.85rem;
  color: #4a627a;
  font-weight: 500;
}

.badge {
  padding: 0.4rem 1rem;
  border-radius: 40px;
  font-size: 0.85rem;
  font-weight: 500;
  background: rgba(44, 95, 138, 0.08);
  color: #2c5f8a;
  text-decoration: none;
  transition: all 0.2s;
}

.badge:hover {
  background: rgba(44, 95, 138, 0.15);
  transform: translateY(-2px);
}

.login-btn, .register-btn {
  padding: 0.55rem 1.6rem;
  border-radius: 40px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  border: none;
  font-family: inherit;
}

.login-btn {
  background: transparent;
  color: #2c5f8a;
  border: 1px solid rgba(44, 95, 138, 0.35);
}

.login-btn:hover {
  background: rgba(44, 95, 138, 0.08);
  transform: translateY(-2px);
}

.register-btn {
  background: #1f2b3c;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.register-btn:hover {
  background: #2c5f8a;
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(44, 95, 138, 0.3);
}

<<<<<<< HEAD
=======
/* 英雄区域 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.hero-section {
  margin-top: 80px;
  padding: 5rem 0 6rem;
  position: relative;
  overflow: hidden;
  background: radial-gradient(circle at 20% 40%, rgba(245, 250, 255, 0.9), #ffffff);
}

.hero-content {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 4rem;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
}

.hero-text {
  flex: 1.2;
}

.hero-text h1 {
  font-size: 3.8rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 1.2rem;
}

.gradient-text {
  background: linear-gradient(145deg, #2b6a9f, #4caf50);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.hero-text p {
  font-size: 1.2rem;
  color: #4a627a;
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 2rem;
}

.primary-btn, .secondary-btn {
  padding: 0.9rem 2rem;
  border-radius: 48px;
  font-weight: 600;
  transition: all 0.3s;
  cursor: pointer;
  border: none;
}

.primary-btn {
  background: #1f2b3c;
  color: white;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.primary-btn:hover {
  background: #2c5f8a;
  transform: translateY(-3px);
  box-shadow: 0 15px 25px -8px rgba(44, 95, 138, 0.4);
}

.secondary-btn {
  background: white;
  border: 1px solid #cfdfed;
  color: #1f2b3c;
}

.secondary-btn:hover {
  border-color: #2c5f8a;
  transform: translateY(-2px);
}

.hero-stats {
  display: flex;
<<<<<<< HEAD
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 0;
  color: #64748b;
  font-size: 0.9rem;
}

.hero-stats .stat {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.hero-stats .stat span {
  font-weight: 600;
  color: #2c5f8a;
}

.hero-stats .stat-dot {
  color: #cbd5e1;
  font-size: 1.2rem;
=======
  gap: 2rem;
}

.hero-stats .stat span {
  font-weight: 800;
  font-size: 1.3rem;
  color: #1f2b3c;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
}

.hero-image {
  flex: 0.9;
  position: relative;
}

.floating-card {
  background: white;
  border-radius: 32px;
  overflow: hidden;
  box-shadow: 0 30px 40px -20px rgba(0, 0, 0, 0.25);
  transition: transform 0.3s;
}

.floating-card img {
  width: 100%;
  display: block;
}

.floating-element {
  position: absolute;
  background: rgba(255,255,255,0.7);
  backdrop-filter: blur(8px);
  border-radius: 60px;
  padding: 12px;
  font-size: 1.5rem;
  color: #2c5f8a;
  animation: float 4s infinite ease-in-out;
}

.elem-1 { top: -20px; left: -20px; animation-delay: 0s; }
.elem-2 { bottom: 30px; right: -20px; animation-delay: 1.5s; }

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}

.scroll-indicator {
  text-align: center;
  margin-top: 3rem;
  cursor: pointer;
  animation: bounce 2s infinite;
  color: #5c6f87;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8px); }
}

<<<<<<< HEAD
=======
/* AI 功能专区 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.ai-features-section {
  padding: 5rem 0;
  background: linear-gradient(120deg, #f0f5fb, #ffffff);
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-header h2 {
  font-size: 2.6rem;
  font-weight: 700;
  color: #1f2b3c;
}

.section-sub {
  font-size: 1.1rem;
  color: #5c6f87;
  margin-top: 0.5rem;
}

.ai-features-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 0 2rem;
}

.ai-card {
  background: white;
  border-radius: 32px;
  padding: 2rem;
  transition: all 0.4s cubic-bezier(0.15, 0.75, 0.45, 1);
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 12px 28px -10px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.ai-card:hover {
  transform: translateY(-12px);
  border-color: rgba(44, 95, 138, 0.2);
  box-shadow: 0 30px 40px -18px rgba(0, 0, 0, 0.15);
}

.ai-icon {
  font-size: 2.8rem;
  margin-bottom: 1.5rem;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef3fc, white);
  border-radius: 40px;
  color: #2c5f8a;
  margin-left: auto;
  margin-right: auto;
}

.ai-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.ai-card p {
  color: #5b6e8c;
  line-height: 1.6;
}

<<<<<<< HEAD
=======
/* 特性卡片 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.features-section {
  padding: 5rem 0;
  background: white;
  position: relative;
}

.features-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 0 2rem;
}

.feature-card {
  background: #ffffff;
  border-radius: 32px;
  padding: 2rem;
  transition: all 0.4s cubic-bezier(0.15, 0.75, 0.45, 1);
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 12px 28px -10px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
<<<<<<< HEAD
=======
  opacity: 0;
  transform: translateY(30px);
  animation: fadeInUp 0.6s forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
}

.feature-card:hover {
  transform: translateY(-12px);
  border-color: rgba(44, 95, 138, 0.2);
  box-shadow: 0 30px 40px -18px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 2.4rem;
  margin-bottom: 1.5rem;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef3fc, white);
  border-radius: 24px;
  color: #2c5f8a;
}

<<<<<<< HEAD
.tools-section {
  padding: 6rem 0;
  background: linear-gradient(120deg, #f0f5fb, #ffffff);
  position: relative;
  overflow: hidden;
}

.tools-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -10%;
  width: 60%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(66, 153, 225, 0.08) 0%, transparent 70%);
}

.tools-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.8rem;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
}

.tool-card {
  background: linear-gradient(135deg, #f4f8fc, #ffffff);
  border-radius: 50px;
  padding: 1.6rem 1rem;
  transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border: 2px solid rgba(44, 95, 138, 0.06);
  box-shadow: 0 6px 20px rgba(44, 95, 138, 0.05);
}

.tool-card:hover {
  transform: translateY(-8px) scale(1.03);
  background: linear-gradient(135deg, #ffffff, #f4f8fc);
  border-color: rgba(44, 95, 138, 0.12);
  box-shadow: 0 16px 36px rgba(44, 95, 138, 0.1);
}

.tool-icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #eaf2fa, #dbe7f3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.8rem;
  transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 0 4px 14px rgba(44, 95, 138, 0.08);
}

.tool-card:hover .tool-icon-wrapper {
  transform: scale(1.18);
  background: linear-gradient(135deg, #3a6fa5, #2c5f8a);
  box-shadow: 0 8px 24px rgba(44, 95, 138, 0.3);
}

.tool-icon-wrapper i {
  font-size: 1.35rem;
  color: #3a6fa5;
  transition: color 0.3s;
}

.tool-card:hover .tool-icon-wrapper i {
  color: #ffffff;
}

.tool-card h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1f2b3c;
  margin-bottom: 0.35rem;
  text-align: center;
}

.tool-desc {
  font-size: 0.78rem;
  color: #6b7a8c;
  line-height: 1.45;
  margin: 0;
  text-align: center;
}

.tool-glow {
  position: absolute;
  bottom: -40%;
  left: -40%;
  width: 180%;
  height: 180%;
  background: radial-gradient(ellipse at center, rgba(44, 95, 138, 0.08) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.4s;
}

.tool-card:hover .tool-glow {
  opacity: 1;
}

=======
/* 效率工具 */
.tools-section {
  padding: 5rem 0;
  background: linear-gradient(120deg, #f0f5fb, #ffffff);
}

.tools-grid {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 2rem;
  padding: 0 2rem;
  text-align: center;
}

.tool-item {
  background: white;
  border-radius: 24px;
  padding: 1.5rem;
  transition: all 0.3s;
  cursor: pointer;
}

.tool-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 25px -12px rgba(0, 0, 0, 0.1);
}

.tool-item i {
  font-size: 2rem;
  color: #2c5f8a;
  display: block;
  margin-bottom: 0.8rem;
}

.tool-item span {
  font-weight: 500;
  color: #1f2b3c;
}

/* 使用场景 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.use-cases-section {
  padding: 5rem 0;
  background: white;
  position: relative;
}

.use-cases-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
  padding: 0 2rem;
}

.use-case-card {
  background: #ffffff;
  border-radius: 32px;
  padding: 2rem;
  transition: all 0.4s cubic-bezier(0.15, 0.75, 0.45, 1);
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 12px 28px -10px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.use-case-card:hover {
  transform: translateY(-12px);
  border-color: rgba(44, 95, 138, 0.2);
  box-shadow: 0 30px 40px -18px rgba(0, 0, 0, 0.15);
}

.use-case-icon {
  font-size: 2.4rem;
  margin-bottom: 1.5rem;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef3fc, white);
  border-radius: 24px;
  color: #2c5f8a;
  margin-left: auto;
  margin-right: auto;
}

<<<<<<< HEAD
=======
/* 统计 */
.stats-section {
  background: linear-gradient(120deg, #f0f5fb, #ffffff);
  padding: 4rem 2rem;
  text-align: center;
}

.stats-grid {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 2rem;
}

.stat-item h4 {
  font-size: 2.8rem;
  font-weight: 800;
  color: #1f2b3c;
}

.stat-number {
  display: inline-block;
}

/* 评价卡片 3D倾斜 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.testimonials-section {
  padding: 5rem 0;
  background: #fafcff;
}

.testimonials-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
  color: #1f2b3c;
}

.testimonials-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 0 2rem;
}

.testimonial-card {
  background: white;
  border-radius: 36px;
  padding: 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 18px 30px -12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transform-style: preserve-3d;
}

.testimonial-avatar {
  width: 56px;
  height: 56px;
  background: #eef3fc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: #2c5f8a;
  margin-bottom: 1.5rem;
}

.testimonial-meta {
  margin-top: 1rem;
}

.testimonial-days {
  font-size: 0.85rem;
  color: #8ba0bc;
  margin-top: 0.5rem;
}

<<<<<<< HEAD
=======
/* 常见问题 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.faq-section {
  padding: 5rem 0;
  background: white;
  position: relative;
}

.faq-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  padding: 0 2rem;
}

.faq-item {
  background: #fafcff;
  border-radius: 24px;
  padding: 2rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.faq-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 30px -15px rgba(0, 0, 0, 0.1);
}

.faq-item h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #1f2b3c;
}

.faq-item p {
  color: #4a627a;
  line-height: 1.6;
}

<<<<<<< HEAD
.cta-section {
  margin: 2rem 2rem 0;
  border-radius: 32px;
  background: white;
  box-shadow: 0 8px 30px rgba(44, 95, 138, 0.08);
=======
/* CTA 区域 */
.cta-section {
  margin: 2rem 2rem 0;
  border-radius: 48px;
  background: linear-gradient(110deg, #17212b, #1f3345);
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  overflow: hidden;
}

.cta-inner {
<<<<<<< HEAD
  padding: 2.5rem 2rem;
=======
  padding: 4rem 2rem;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  text-align: center;
  color: white;
}

<<<<<<< HEAD
.cta-inner h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.8rem;
  letter-spacing: 0.02em;
  background: linear-gradient(110deg, #08a3f0, #086da0);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.cta-inner p {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 1.5rem;
  line-height: 1.6;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.cta-btn {
  background: linear-gradient(110deg, #08a3f0, #086da0);
  color: white;
=======
.cta-btn {
  background: white;
  color: #1f3345;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  padding: 0.9rem 2.5rem;
  border-radius: 60px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.cta-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 15px 25px rgba(0,0,0,0.2);
}

<<<<<<< HEAD
.home-footer {
  background: #f8fafc;
  color: #475569;
  padding: 2rem 0 1rem;
  margin-top: 2rem;
=======
/* 底部 */
.home-footer {
  background: #0f1a24;
  color: #cddfed;
  padding: 3rem 0 1.5rem;
  margin-top: 3rem;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
}

.footer-content {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
<<<<<<< HEAD
  justify-content: center;
  flex-wrap: wrap;
  padding: 0 2rem;
  gap: 3rem;
}

.footer-logo {
  min-width: 180px;
}

.footer-logo h2 {
  font-size: 2.2rem;
  margin-bottom: 0.6rem;
  background: linear-gradient(135deg, #1f2b3c, #2c5f8a);
=======
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 0 2rem;
}

.footer-logo h2 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #e0eefc, #bdd4e8);
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

<<<<<<< HEAD
.footer-logo p {
  font-size: 0.95rem;
  color: #8ba0bc;
  margin-bottom: 0.8rem;
}

=======
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
.security-badge {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #8ba0bc;
}

.footer-links {
  display: flex;
<<<<<<< HEAD
  gap: 2.5rem;
=======
  gap: 4rem;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  flex-wrap: wrap;
}

.link-group h3 {
<<<<<<< HEAD
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.7rem;
  color: #1e293b;
=======
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #f0f6fe;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
}

.link-group a {
  display: block;
<<<<<<< HEAD
  color: #64748b;
  text-decoration: none;
  margin-bottom: 0.35rem;
  font-size: 0.88rem;
=======
  color: #a1bbd4;
  text-decoration: none;
  margin-bottom: 0.5rem;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  transition: 0.2s;
}

.link-group a:hover {
<<<<<<< HEAD
  color: #2c5f8a;
=======
  color: white;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  transform: translateX(4px);
}

.footer-bottom {
  text-align: center;
<<<<<<< HEAD
  padding-top: 1.2rem;
  margin-top: 1.2rem;
  font-size: 0.8rem;
  color: #94a3b8;
}

=======
  padding-top: 2rem;
  border-top: 1px solid #2a3a48;
  margin-top: 2rem;
  font-size: 0.85rem;
  color: #8ba0bc;
}

/* 响应式 */
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
@media (max-width: 1024px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  .hero-text h1 {
    font-size: 2.8rem;
  }
  .hero-actions {
    justify-content: center;
  }
  .hero-stats {
    justify-content: center;
  }
  .download-badges {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0.7rem 1rem;
  }
  .hero-section {
    padding: 3rem 0;
  }
  .hero-text h1 {
    font-size: 2.2rem;
  }
  .section-header h2 {
    font-size: 2rem;
  }
  .features-grid,
  .ai-features-grid,
  .use-cases-grid,
  .testimonials-grid,
  .faq-grid {
    grid-template-columns: 1fr;
  }
  .tools-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .footer-links {
    flex-direction: column;
    gap: 1.5rem;
  }
<<<<<<< HEAD
=======
  .stats-grid {
    flex-direction: column;
    gap: 1.5rem;
  }
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
}

@media (max-width: 480px) {
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero-stats {
<<<<<<< HEAD
    flex-wrap: wrap;
    gap: 0.8rem;
    justify-content: center;
=======
    flex-direction: column;
    gap: 0.8rem;
>>>>>>> 89d40232c06669afee800b2b5cbccdab595ce2ff
  }
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }
  .primary-btn, .secondary-btn {
    width: 100%;
  }
}
</style>