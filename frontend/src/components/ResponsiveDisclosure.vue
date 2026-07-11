<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    title: string;
    statusText?: string;
    defaultMobileOpen?: boolean;
    forceOpen?: boolean;
  }>(),
  {
    statusText: "",
    defaultMobileOpen: false,
    forceOpen: false,
  },
);

const isDesktop = ref(false);
const mobileOpen = ref(props.defaultMobileOpen || props.forceOpen);
let desktopQuery: MediaQueryList | undefined;

const expanded = computed(() => isDesktop.value || mobileOpen.value);

function syncDesktop(event: MediaQueryListEvent | MediaQueryList) {
  isDesktop.value = event.matches;
}

function toggle() {
  if (!isDesktop.value) {
    mobileOpen.value = !mobileOpen.value;
  }
}

watch(
  () => props.forceOpen,
  (shouldOpen) => {
    if (shouldOpen) {
      mobileOpen.value = true;
    }
  },
);

onMounted(() => {
  desktopQuery = window.matchMedia("(min-width: 901px)");
  syncDesktop(desktopQuery);
  desktopQuery.addEventListener("change", syncDesktop);
});

onBeforeUnmount(() => {
  desktopQuery?.removeEventListener("change", syncDesktop);
});
</script>

<template>
  <section class="responsive-disclosure" :class="{ 'is-open': expanded }">
    <button
      class="responsive-disclosure__trigger"
      type="button"
      :aria-expanded="expanded"
      @click="toggle"
    >
      <span class="responsive-disclosure__title">{{ title }}</span>
      <span v-if="statusText" class="responsive-disclosure__status">{{ statusText }}</span>
      <span class="responsive-disclosure__chevron" aria-hidden="true"></span>
    </button>
    <div v-show="expanded" class="responsive-disclosure__content">
      <slot />
    </div>
  </section>
</template>
