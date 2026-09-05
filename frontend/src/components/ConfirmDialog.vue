<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
const emit = defineEmits<{ confirm: []; cancel: [] }>();
const dialog = ref<HTMLDialogElement>();
const { t } = useI18n();
let previous: HTMLElement | null = null;
onMounted(() => {
  previous = document.activeElement as HTMLElement | null;
  dialog.value?.showModal();
});
onBeforeUnmount(() => {
  dialog.value?.close();
  previous?.focus();
});
</script>

<template>
  <Teleport to="body">
    <dialog ref="dialog" class="confirm-dialog" aria-labelledby="confirm-title" @cancel.prevent="emit('cancel')">
      <h2 id="confirm-title">{{ t('ux.confirmTitle') }}</h2>
      <p>{{ t('ux.confirmBody') }}</p>
      <div class="button-row">
        <button autofocus @click="emit('cancel')">{{ t('ux.cancel') }}</button>
        <button class="primary" @click="emit('confirm')">{{ t('ux.confirm') }}</button>
      </div>
    </dialog>
  </Teleport>
</template>
