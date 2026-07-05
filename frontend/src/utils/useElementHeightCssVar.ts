import { computed, onBeforeUnmount, ref, watch } from "vue";

export function useElementHeightCssVar(variableName: string) {
  const elementRef = ref<HTMLElement | null>(null);
  const height = ref(0);
  let observer: ResizeObserver | null = null;

  function updateHeight(element: HTMLElement) {
    height.value = Math.ceil(element.getBoundingClientRect().height);
  }

  function stopObserving() {
    observer?.disconnect();
    observer = null;
  }

  watch(
    elementRef,
    (element) => {
      stopObserving();
      if (!element) {
        height.value = 0;
        return;
      }

      updateHeight(element);
      observer = new ResizeObserver(() => updateHeight(element));
      observer.observe(element);
    },
    { flush: "post", immediate: true },
  );

  onBeforeUnmount(stopObserving);

  const heightStyle = computed(() => {
    return height.value > 0 ? { [variableName]: `${height.value}px` } : {};
  });

  return {
    elementRef,
    heightStyle,
  };
}
