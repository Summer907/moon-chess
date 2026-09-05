import { onBeforeUnmount, onMounted, type Ref } from "vue";

export function useDialogFocus(element: Ref<HTMLElement | null>, close: () => void) {
  let previous: HTMLElement | null = null;
  function keydown(event: KeyboardEvent) {
    if (event.key === "Escape") { event.preventDefault(); close(); return; }
    if (event.key !== "Tab" || !element.value) return;
    const focusable = Array.from(element.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]):not([tabindex="-1"]), a[href], input:not([disabled]), [tabindex="0"]',
    )).filter(item => item.getClientRects().length > 0);
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (!first || !last) { event.preventDefault(); element.value.focus(); return; }
    if (event.shiftKey && (document.activeElement === first || document.activeElement === element.value)) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || document.activeElement === element.value)) {
      event.preventDefault(); first.focus();
    }
  }
  onMounted(() => {
    previous = document.activeElement as HTMLElement | null;
    element.value?.focus();
    document.addEventListener("keydown", keydown);
  });
  onBeforeUnmount(() => {
    document.removeEventListener("keydown", keydown);
    previous?.focus();
  });
}
