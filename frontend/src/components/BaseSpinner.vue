<template>
  <div class="flex items-center justify-center space-x-2">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2" :class="`border-${color}-500`"></div>
    <span v-if="text" :class="`text-${color}-500`">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps({
  text: {
    type: String,
    default: '加载中...',
  },
  color: {
    type: String,
    default: 'primary',
  },
});
</script> 