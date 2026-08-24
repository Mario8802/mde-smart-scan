(() => {
  const form = document.querySelector("[data-scan-form]");
  if (!form) return;

  const input = form.querySelector("input[type=file]");
  const preview = form.querySelector("[data-preview]");
  const processing = form.querySelector("[data-processing]");

  input?.addEventListener("change", () => {
    const file = input.files?.[0];
    if (!file || !preview) return;
    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
    preview.onload = () => URL.revokeObjectURL(preview.src);
  });

  form.addEventListener("submit", () => {
    if (processing) processing.hidden = false;
  });
})();
