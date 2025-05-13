<template>
  <component :is="type" v-bind="linkProps">
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue';
import { isExternal } from '@/utils/validate';

const props = defineProps({
  to: {
    type: String,
    required: true
  }
});

// 判断链接类型
const isExternalLink = computed(() => {
  return isExternal(props.to);
});

// 组件类型
const type = computed(() => {
  if (isExternalLink.value) {
    return 'a';
  }
  return 'router-link';
});

// 链接属性
const linkProps = computed(() => {
  if (isExternalLink.value) {
    return {
      href: props.to,
      target: '_blank',
      rel: 'noopener'
    };
  }
  return {
    to: props.to
  };
});
</script> 