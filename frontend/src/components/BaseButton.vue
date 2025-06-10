<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      'relative overflow-hidden group px-6 py-2 rounded-lg text-white font-semibold transition-all duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-900',
      variants[variant],
      { 'opacity-50 cursor-not-allowed': disabled }
    ]"
    @click="$emit('click', $event)"
  >
    <span class="relative z-10"><slot /></span>
    <span v-if="!disabled" class="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity duration-300"></span>
    <span v-if="!disabled" class="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-500 ease-in-out"></span>
  </button>
</template>

<script setup lang="ts">
type ButtonType = 'button' | 'submit' | 'reset';
type ButtonVariant = 'primary' | 'secondary' | 'danger';

defineProps({
  type: {
    type: String as () => ButtonType,
    default: 'button',
  },
  variant: {
    type: String as () => ButtonVariant,
    default: 'primary',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['click']);

const variants = {
  primary: 'bg-indigo-600 hover:bg-indigo-500 focus:ring-indigo-500',
  secondary: 'bg-gray-700 hover:bg-gray-600 focus:ring-gray-500',
  danger: 'bg-red-600 hover:bg-red-500 focus:ring-red-500',
};
</script> 