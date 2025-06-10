<template>
  <PageContainer>
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center animate-fade-in-up">
      <BaseSpinner class="w-10 h-10 mx-auto mb-4" />
      <h1 class="text-2xl font-bold text-gray-100">正在检索安全笔记...</h1>
      <p class="text-gray-400">请稍候，我们正在安全地处理您的请求。</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center animate-fade-in-up">
      <div class="bg-red-900/20 border border-red-500/30 rounded-xl p-8">
        <h1 class="text-3xl font-bold text-red-500">访问错误</h1>
        <p class="text-gray-400 mt-4">{{ error }}</p>
        <RouterLink to="/create" class="mt-6 inline-block">
          <BaseButton variant="secondary">创建一条新消息</BaseButton>
        </RouterLink>
      </div>
    </div>

    <!-- Password Prompt State -->
    <div v-else-if="needsPassword && !noteContent && !fileBlob" class="max-w-md mx-auto text-center animate-fade-in-up">
       <h1 class="text-2xl font-bold text-gray-100 mb-4">需要密码</h1>
       <p class="text-gray-400 mb-6">此内容受密码保护，请输入密码以继续。</p>
       
       <form @submit="onPasswordSubmit" class="space-y-4">
        <BaseInput
          id="password"
          type="password"
          v-model="passwordValue"
          :error="passwordError"
          placeholder="输入访问密码"
          class="text-center"
        />
        <BaseButton type="submit" :disabled="isSubmittingPassword" class="w-full !py-3">
            <BaseSpinner v-if="isSubmittingPassword" class="w-5 h-5 mr-2" />
            {{ isSubmittingPassword ? '正在解密...' : '查看内容' }}
        </BaseButton>
       </form>
    </div>

    <!-- Content Display State -->
    <div v-else-if="noteContent || fileBlob" class="max-w-2xl mx-auto animate-fade-in-up">
      <div class="bg-gray-800 border border-indigo-500/30 rounded-xl p-8 shadow-2xl shadow-indigo-500/10">
        <div v-if="noteInfo?.note_type === 'text' && noteContent">
          <h2 class="text-2xl font-bold text-gray-100 mb-4">秘密文本</h2>
          <pre class="whitespace-pre-wrap break-words bg-gray-900 p-4 rounded-lg text-gray-200 font-sans">{{ noteContent }}</pre>
        </div>

        <div v-if="noteInfo?.note_type === 'file' && fileBlob" class="text-center">
            <h2 class="text-2xl font-bold text-gray-100 mb-4">安全文件</h2>
            <p class="text-gray-400 mb-6">文件已准备好下载。点击下方按钮开始下载。</p>
            <BaseButton @click="downloadFileContent" class="w-full md:w-auto">
              下载 {{ fileName || '文件' }}
            </BaseButton>
        </div>
        
        <!-- 调试信息 -->
        <div v-if="noteInfo?.note_type === 'file' && !fileBlob" class="text-center">
            <h2 class="text-2xl font-bold text-red-400 mb-4">调试：文件类型但无Blob数据</h2>
            <p class="text-gray-400 mb-2">noteInfo.note_type: {{ noteInfo?.note_type }}</p>
            <p class="text-gray-400 mb-2">fileBlob存在: {{ !!fileBlob }}</p>
            <p class="text-gray-400 mb-2">fileName: {{ fileName }}</p>
            <p class="text-gray-400 mb-6">可能的原因：文件下载请求失败</p>
        </div>
        
        <!-- 调试信息：条件检查 -->
        <div v-if="fileBlob" class="text-center mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <h3 class="text-lg font-bold text-blue-400 mb-2">🔍 按钮渲染条件调试</h3>
            <p class="text-gray-400 mb-1">noteInfo存在: {{ !!noteInfo }}</p>
            <p class="text-gray-400 mb-1">noteInfo.note_type: "{{ noteInfo?.note_type }}"</p>
            <p class="text-gray-400 mb-1">是否等于'file': {{ noteInfo?.note_type === 'file' }}</p>
            <p class="text-gray-400 mb-1">fileBlob存在: {{ !!fileBlob }}</p>
            <p class="text-gray-400 mb-1">按钮应该显示: {{ noteInfo?.note_type === 'file' && !!fileBlob }}</p>
            <p class="text-gray-400">fileName: {{ fileName }}</p>
        </div>
      </div>
       <div class="mt-8 text-center p-4 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
          <p class="font-semibold text-yellow-400">注意：此内容已被永久销毁。</p>
          <p class="text-yellow-500 text-sm">关闭此页面后，内容将无法再次访问。</p>
        </div>
    </div>

  </PageContainer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { apiService, type NoteInfoResponse } from '@/services/api';
import axios from 'axios';

// API客户端配置
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001',
  timeout: 30000,
});

import PageContainer from '@/components/PageContainer.vue';
import BaseButton from '@/components/BaseButton.vue';
import BaseSpinner from '@/components/BaseSpinner.vue';
import BaseInput from '@/components/BaseInput.vue';
import { useForm, useField } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';


const route = useRoute();
const noteId = route.params.id as string;

// State Management
const isLoading = ref(true);
const isSubmittingPassword = ref(false);
const error = ref<string | null>(null);
const needsPassword = ref(false);
const noteInfo = ref<NoteInfoResponse | null>(null);
const noteContent = ref<string | null>(null);
const fileBlob = ref<Blob | null>(null);
const fileName = ref<string | null>(null);

// Password Form Validation
const passwordSchema = toTypedSchema(
  z.object({
    password: z.string().min(1, '密码不能为空'),
  })
);
const { handleSubmit, setFieldError } = useForm({ validationSchema: passwordSchema });
const { value: passwordValue, errorMessage: passwordError } = useField<string>('password');

/**
 * 根据笔记类型和密码获取内容的核心函数
 */
const getContent = async (password?: string) => {
  if (!noteInfo.value) {
    error.value = "无法确定笔记类型。";
    return;
  }
  
  error.value = null;
  
  try {
    if (noteInfo.value.note_type === 'text') {
      const response = await apiService.getNote(noteId, password);
      noteContent.value = response.content;
    } else { // 'file'
      console.log('正在下载文件...');
      const response = await apiClient.post<Blob>(
        `/note/${noteId}/download`,
        { password },
        { 
          headers: { 'Content-Type': 'application/json' },
          responseType: 'blob' 
        }
      );
      
      console.log('文件下载响应:', response);
      console.log('响应数据类型:', typeof response.data);
      console.log('响应数据大小:', response.data.size);
      console.log('响应头:', response.headers);
      
      let fName = 'downloaded_file';
      // 从响应头中提取文件名
      const contentDisposition = response.headers['content-disposition'];
      console.log('Content-Disposition头:', contentDisposition);
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) {
          fName = match[1];
        }
      }
      
      fileBlob.value = response.data;
      fileName.value = fName;
      console.log('设置fileBlob和fileName:', fileBlob.value, fileName.value);
    }
  } catch (err: any) {
    throw err;
  }
};

const onPasswordSubmit = handleSubmit(async (values) => {
  isSubmittingPassword.value = true;
  try {
    await getContent(values.password);
  } catch (err: any) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      setFieldError('password', "密码错误。");
    } else if (err.response?.status === 404) {
      error.value = "笔记不存在或已被销毁。";
    } else {
      error.value = "无法获取内容，请稍后再试。";
    }
    // 清空密码，以便用户重试
    passwordValue.value = '';
  } finally {
    isSubmittingPassword.value = false;
  }
});

const downloadFileContent = () => {
    console.log('下载按钮被点击');
    console.log('fileBlob.value:', fileBlob.value);
    console.log('fileName.value:', fileName.value);
    
    if (!fileBlob.value) {
      console.error('fileBlob 为空');
      error.value = "文件数据丢失，请重新访问链接。";
      return;
    }
    
    if (!fileName.value) {
      console.warn('fileName 为空，使用默认名称');
      fileName.value = 'downloaded_file';
    }
    
    try {
      const url = window.URL.createObjectURL(fileBlob.value);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName.value;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      console.log('下载触发成功');
    } catch (err) {
      console.error('下载失败:', err);
      error.value = "下载失败，请重新尝试。";
    }
}

onMounted(async () => {
  if (!noteId) {
    error.value = "无效的笔记ID。";
    isLoading.value = false;
    return;
  }
  
  try {
    const info = await apiService.getNoteInfo(noteId);
    noteInfo.value = info;
    needsPassword.value = info.password_protected;

    if (!info.password_protected) {
      isLoading.value = true; // 开始获取内容，显示加载
      await getContent();
    }
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = "笔记不存在或已被销毁。";
    } else {
      error.value = "无法获取笔记信息，请稍后再试。";
    }
  } finally {
    isLoading.value = false;
  }
});
</script>
