<script setup lang="ts">
import { ref, reactive, provide } from 'vue'
import { RouterView } from 'vue-router'

// 全局状态
const isLoading = ref(false)

const notification = reactive({
  show: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'info'
})

// 全局方法
const showNotification = (message: string, type: typeof notification.type = 'info') => {
  notification.message = message
  notification.type = type
  notification.show = true
  
  setTimeout(() => {
    notification.show = false
  }, 3000)
}

const setLoading = (loading: boolean) => {
  isLoading.value = loading
}

// 提供给子组件使用
provide('loading', { isLoading, setLoading })
provide('notification', { showNotification })
</script>

<template>
  <div id="app" class="min-h-screen gradient-bg">
    <!-- 全局加载指示器 -->
    <Transition name="fade">
      <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    </Transition>

    <!-- 主要内容区域 -->
    <main class="relative z-10">
      <RouterView v-slot="{ Component }">
        <Transition name="slide-up" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <!-- 全局通知区域 -->
    <div class="fixed top-4 right-4 z-40">
      <Transition name="slide-up">
        <div
          v-if="notification.show"
          :class="[
            'px-4 py-3 rounded-lg shadow-lg max-w-sm',
            notification.type === 'success' ? 'bg-green-600 text-white' :
            notification.type === 'error' ? 'bg-red-600 text-white' :
            'bg-blue-600 text-white'
          ]"
        >
          {{ notification.message }}
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
