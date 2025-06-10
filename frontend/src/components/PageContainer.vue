<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-4">
    <div class="w-full" :class="`max-w-${maxWidth}`">
      <slot name="header"></slot>
      <div class="card animate-fade-in">
        <slot></slot>
      </div>
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  maxWidth: {
    type: String as () => 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl',
    default: 'md',
  },
});
</script> 