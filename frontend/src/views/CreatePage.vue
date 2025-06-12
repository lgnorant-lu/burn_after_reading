<template>
  <PageContainer>
    <transition name="fade-up" mode="out-in">
      <div v-if="!showResult" key="form">
        <h1 class="text-3xl font-bold text-center text-gray-100 mb-2 animate-fade-in-up">创建阅后即焚内容</h1>
        <p class="text-center text-gray-400 mb-8 animate-fade-in-up" style="animation-delay: 100ms;">分享文本或文件，一次查看后即销毁。</p>

        <div class="mb-6 animate-fade-in-up" style="animation-delay: 200ms;">
          <div class="flex justify-center bg-gray-800 p-1 rounded-lg">
            <button
              @click="formType = 'text'"
              :class="['px-6 py-2 rounded-md text-sm font-medium transition-colors', formType === 'text' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-700']"
            >
              文本
            </button>
            <button
              @click="formType = 'file'"
              :class="['px-6 py-2 rounded-md text-sm font-medium transition-colors', formType === 'file' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-700']"
            >
              文件 (最大 5MB)
            </button>
          </div>
        </div>

        <form @submit="onSubmit" class="space-y-6 animate-fade-in-up" style="animation-delay: 300ms;">
          <transition name="fade-up" mode="out-in">
            <div v-if="formType === 'text'" key="text-input">
                <label for="content" class="block text-sm font-medium text-gray-300 mb-1">秘密文本</label>
                <textarea
                  id="content"
                  v-model="contentValue"
                  rows="6"
                  class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                  placeholder="在此输入您的秘密消息..."
                ></textarea>
                <p v-if="contentError" class="text-red-400 text-sm mt-1">{{ contentError }}</p>
            </div>
            <div v-else key="file-input">
              <label for="file" class="block text-sm font-medium text-gray-300 mb-1">上传文件</label>
              <input
                type="file"
                id="file"
                @change="handleFileChange"
                class="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-indigo-300 hover:file:bg-gray-600 transition"
              />
              <p v-if="fileError" class="text-red-400 text-sm mt-1">{{ fileError }}</p>
              <p v-if="values.file?.[0]" class="text-gray-400 text-sm mt-1">已选择: {{ values.file[0].name }}</p>
            </div>
          </transition>
          <div>
              <label for="password" class="block text-sm font-medium text-gray-300 mb-1">密码保护 (可选)</label>
              <BaseInput
                  id="password"
                  type="password"
                  v-model="passwordValue"
                  :error="passwordError"
                  placeholder="设置一个访问密码"
              />
          </div>

          <div>
            <label for="expiration_type" class="block text-sm font-medium text-gray-300 mb-1">销毁条件</label>
            <select
              id="expiration_type"
              v-model="expirationValue"
              class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
            >
              <option v-for="option in expirationOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
             <p v-if="expirationError" class="text-red-400 text-sm mt-1">{{ expirationError }}</p>
          </div>

          <BaseButton type="submit" :disabled="isSubmitting" class="w-full flex justify-center !py-3">
            <BaseSpinner v-if="isSubmitting" class="w-5 h-5 mr-2" />
            {{ isSubmitting ? '正在加密...' : '生成焚毁链接' }}
          </BaseButton>
        </form>
      </div>
      <div v-else-if="showResult && submissionResult" key="result" class="text-center animate-fade-in-up">
        <div class="bg-gray-800 border border-green-500/30 rounded-xl p-8 shadow-2xl shadow-green-500/10">
          <h2 class="text-2xl font-bold text-green-400 mb-4">链接已生成！</h2>
          <p class="text-gray-400 mb-6">请复制下面的链接。它将在第一次被访问后立即销毁。</p>
          
          <div class="relative">
            <input
              :value="submissionResult.access_url"
              readonly
              class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white text-center pr-10"
            />
            <button @click="copyToClipboard(submissionResult.access_url)" class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-white transition-colors">
              <transition name="fade-up" mode="out-in">
                <svg v-if="!copied" key="copy-icon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                <svg v-else key="check-icon" class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
              </transition>
            </button>
          </div>
          <p v-if="submissionResult.expires_at" class="text-sm text-gray-500 mt-2">
            链接将于 {{ new Date(submissionResult.expires_at).toLocaleString() }} 失效
          </p>
        </div>
        
        <BaseButton @click="startNew" variant="secondary" class="mt-8">
          再创建一个
        </BaseButton>
      </div>
    </transition>

    <!-- Notification -->
    <transition name="fade-up">
      <div v-if="notification" :class="['fixed bottom-5 right-5 px-4 py-2 rounded-lg text-white shadow-lg', notification.type === 'success' ? 'bg-green-600' : 'bg-red-600']">
        {{ notification.message }}
      </div>
    </transition>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useForm, useField } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { apiService, type CreateNoteRequest, type CreateNoteResponse } from '@/services/api';

import PageContainer from '@/components/PageContainer.vue';
import BaseButton from '@/components/BaseButton.vue';
import BaseInput from '@/components/BaseInput.vue';
import BaseSpinner from '@/components/BaseSpinner.vue';

// -----------------------------------------------------------------------------
// 表单类型与模式定义 (Form Type & Schema Definition)
// -----------------------------------------------------------------------------

const formType = ref<'text' | 'file'>('text');

const baseSchema = z.object({
  password: z.string().optional(),
  expiration_type: z.enum(['read_once', 'one_hour', 'one_day', 'one_week']),
});

const textSchema = baseSchema.extend({
  content: z.string().min(1, '内容不能为空'),
  file: z.custom<FileList>().optional(),
});

const fileSchema = baseSchema.extend({
  content: z.string().optional(),
  file: z.custom<FileList>(val => val instanceof FileList && val.length > 0, '请选择一个文件').refine(
    (files) => files?.[0]?.size <= 5 * 1024 * 1024,
    '文件大小不能超过5MB'
  ),
});

const validationSchema = computed(() => {
  return toTypedSchema(formType.value === 'text' ? textSchema : fileSchema);
});

// -----------------------------------------------------------------------------
// 表单状态管理 (Form State Management)
// -----------------------------------------------------------------------------

const { handleSubmit, isSubmitting, values, resetForm, setFieldValue, setErrors } = useForm({
  validationSchema,
  initialValues: {
    content: '',
    password: '',
    expiration_type: 'read_once',
    file: undefined,
  },
});

const { value: contentValue, errorMessage: contentError } = useField<string>('content');
const { errorMessage: fileError } = useField<FileList>('file');
const { value: passwordValue, errorMessage: passwordError } = useField<string>('password');
const { value: expirationValue, errorMessage: expirationError } = useField<'read_once' | 'one_hour' | 'one_day' | 'one_week'>('expiration_type');

const submissionResult = ref<CreateNoteResponse | null>(null);
const showResult = ref(false);
const notification = ref<{ message: string; type: 'success' | 'error' } | null>(null);
const copied = ref(false);

// -----------------------------------------------------------------------------
// 逻辑处理 (Logic Handlers)
// -----------------------------------------------------------------------------

watch(formType, (newType) => {
  submissionResult.value = null;
  showResult.value = false;
  // 使用当前值来构建一个对新 schema 有效的初始状态
  const currentPassword = values.password;
  const currentExpiration = values.expiration_type;

  resetForm({
    values: {
      password: currentPassword,
      expiration_type: currentExpiration,
      content: newType === 'text' ? '' : undefined,
      file: newType === 'file' ? undefined : undefined,
    } as any, // vee-validate的类型推断在此处可能不完美，使用any临时规避
  });
});

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text);
  copied.value = true;
  showNotification('链接已复制到剪贴板！', 'success');
  setTimeout(() => {
    copied.value = false;
  }, 2000);
};

const showNotification = (message: string, type: 'success' | 'error') => {
  notification.value = { message, type };
  setTimeout(() => {
    notification.value = null;
  }, 3000);
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    setFieldValue('file', target.files);
  }
};

const onSubmit = handleSubmit(async (formValues) => {
  try {
    submissionResult.value = null;
    showResult.value = false;
    let result: CreateNoteResponse | undefined;

    if (formType.value === 'text') {
       if (!formValues.content) {
        showNotification('文本内容不能为空。', 'error');
        return;
      }
      const payload: CreateNoteRequest = {
        expiration_type: formValues.expiration_type,
        content: formValues.content,
      };
      if (formValues.password) {
        payload.password = formValues.password;
      }
      result = await apiService.createNote(payload);
    } else if (formValues.file?.[0]) {
      const file = formValues.file[0];
      result = await apiService.uploadFile(
        file,
        formValues.password,
        formValues.expiration_type
      );
    }

    if (result) {
      submissionResult.value = result;
      showResult.value = true;
      resetForm({
        values: {
          content: '',
          password: '',
          expiration_type: 'read_once',
          file: undefined,
        }
      });
    } else {
      if(formType.value === 'file') {
        showNotification('请选择一个文件。', 'error');
      }
    }
  } catch (error: any) {
    const errorMessage = error?.response?.data?.detail || '创建失败，请稍后再试。';
    setErrors({ content: errorMessage });
    showNotification(errorMessage, 'error');
  }
});

const startNew = () => {
  submissionResult.value = null;
  showResult.value = false;
};

// -----------------------------------------------------------------------------
// Expiration Options
// -----------------------------------------------------------------------------
const expirationOptions = [
  { value: 'read_once', label: '阅后即焚' },
  { value: 'one_hour', label: '1 小时后' },
  { value: 'one_day', label: '24 小时后' },
  { value: 'one_week', label: '7 天后' },
];
</script>

<style>
.fade-up-enter-active, .fade-up-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-up-enter-from, .fade-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>