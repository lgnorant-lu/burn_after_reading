<template>
  <PageContainer max-width="md">
    <template #header>
      <!-- Logo和标题 -->
      <div class="text-center mb-8">
        <div class="mx-auto h-16 w-16 flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mb-4">
          <svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-4xl font-bold text-white">Burn After Reading</h1>
        <p class="text-gray-400 mt-2">安全的阅后即焚消息分享</p>
      </div>
    </template>
    
    <!-- 主要操作内容 -->
    <div class="space-y-4">
      <h2 class="text-xl font-semibold text-center mb-6">选择操作</h2>
      
      <!-- 创建消息按钮 -->
      <RouterLink 
        to="/create" 
        class="block"
      >
        <BaseButton variant="primary" class="w-full py-4 text-lg">
          创建新消息
        </BaseButton>
      </RouterLink>

      <!-- 分割线 -->
      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-600"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-gray-800 text-gray-400">或</span>
        </div>
      </div>

      <!-- 访问消息区域 -->
      <div class="space-y-3">
        <BaseInput
          id="noteId"
          v-model="noteId"
          placeholder="输入消息ID或完整链接"
          @keyup.enter="accessNote"
        />
        <BaseButton 
          variant="secondary"
          class="w-full py-3"
          :disabled="!noteId.trim()"
          @click="accessNote"
        >
          访问消息
        </BaseButton>
      </div>
    </div>

    <template #footer>
      <!-- 功能说明 -->
      <div class="text-center space-y-2 text-sm text-gray-400 mt-8">
        <p>🔒 端到端加密保护</p>
        <p>🔥 阅读后自动销毁</p>
        <p>📁 支持文件分享 (最大5MB)</p>
        <p>⏰ 多种过期时间选项</p>
      </div>

      <!-- 版本信息 -->
      <div class="text-center text-xs text-gray-500 mt-4">
        <p>Powered by Burn After Reading v0.2.0</p>
      </div>
    </template>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import PageContainer from '../components/PageContainer.vue';
import BaseButton from '../components/BaseButton.vue';
import BaseInput from '../components/BaseInput.vue';

const router = useRouter();
const noteId = ref('');

const accessNote = () => {
  if (!noteId.value.trim()) return;
  
  let id = noteId.value.trim();
  const urlMatch = id.match(/\/access\/([^/]+)/);
  if (urlMatch) {
    id = urlMatch[1];
  }
  
  router.push(`/access/${encodeURIComponent(id)}`);
};
</script> 