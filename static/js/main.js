// --- Ingrediënten panel (cook mode) ---

const panel = document.getElementById("ing-panel");
const overlay = document.getElementById("ing-overlay");
const toggleBtn = document.getElementById("ing-toggle");
const closeBtn = document.getElementById("ing-close");

function openPanel() {
  panel?.classList.add("open");
  overlay?.classList.add("open");
}

function closePanel() {
  panel?.classList.remove("open");
  overlay?.classList.remove("open");
}

toggleBtn?.addEventListener("click", openPanel);
closeBtn?.addEventListener("click", closePanel);
overlay?.addEventListener("click", closePanel);

// --- Dynamische ingrediëntenrijen ---

const ingList = document.getElementById("ingredient-list");

function isLastRow(row) {
  return row === ingList?.lastElementChild;
}

function renumberRows() {
  ingList?.querySelectorAll(".ingredient-row").forEach((row, i) => {
    row.querySelector("input[name^='item_']").name = `item_${i}`;
    row.querySelector("input[name^='amount_']").name = `amount_${i}`;
    row.querySelector("input[name^='unit_']").name = `unit_${i}`;
  });
}

function addRow() {
  const div = document.createElement("div");
  div.className = "ingredient-row";
  div.draggable = true;
  const idx = ingList.querySelectorAll(".ingredient-row").length;
  div.innerHTML = `
    <span class="drag-handle">⠿</span>
    <input name="item_${idx}" placeholder="Ingredient">
    <input name="amount_${idx}" placeholder="Hoeveelheid" type="number" step="any" class="amount-field">
    <input name="unit_${idx}" placeholder="Eenheid" class="unit-field">
  `;
  ingList.appendChild(div);
  attachListeners(div);
  attachDrag(div);
}

function attachListeners(row) {
  row.querySelectorAll("input").forEach(input => {
    input.addEventListener("input", () => {
      if (isLastRow(row) && input.value.trim() !== "") {
        addRow();
      }
    });
  });
}

// --- Drag & drop ---

let dragSrc = null;

function attachDrag(row) {
  row.addEventListener("dragstart", e => {
    dragSrc = row;
    row.classList.add("dragging");
    e.dataTransfer.effectAllowed = "move";
  });

  row.addEventListener("dragend", () => {
    row.classList.remove("dragging");
    ingList?.querySelectorAll(".ingredient-row").forEach(r => r.classList.remove("drag-over"));
    renumberRows();
  });

  row.addEventListener("dragover", e => {
    e.preventDefault();
    if (row === dragSrc) return;
    ingList?.querySelectorAll(".ingredient-row").forEach(r => r.classList.remove("drag-over"));
    row.classList.add("drag-over");
  });

  row.addEventListener("drop", e => {
    e.preventDefault();
    if (!dragSrc || dragSrc === row) return;
    const rows = [...ingList.querySelectorAll(".ingredient-row")];
    const srcIdx = rows.indexOf(dragSrc);
    const dstIdx = rows.indexOf(row);
    if (srcIdx < dstIdx) {
      row.after(dragSrc);
    } else {
      row.before(dragSrc);
    }
  });
}

ingList?.querySelectorAll(".ingredient-row").forEach(row => {
  attachListeners(row);
  attachDrag(row);
});

// --- Tag widget ---

const tagBox = document.getElementById("tag-input-box");
const tagText = document.getElementById("tag-text");
const tagsValue = document.getElementById("tags-value");

function getTags() {
  return tagsValue?.value
    ? tagsValue.value.split(",").map(t => t.trim()).filter(Boolean)
    : [];
}

function setTags(tags) {
  if (tagsValue) tagsValue.value = tags.join(",");
}

function renderTag(tag) {
  const pill = document.createElement("span");
  pill.className = "tag-pill";
  pill.innerHTML = `${tag}<button type="button" class="tag-remove" data-tag="${tag}">×</button>`;
  pill.querySelector(".tag-remove").addEventListener("click", () => {
    const tags = getTags().filter(t => t !== tag);
    setTags(tags);
    pill.remove();
  });
  // insert before the text input
  tagBox?.insertBefore(pill, tagText);
}

function addTag(raw) {
  const tag = raw.trim().toLowerCase().replace(/,/g, "");
  if (!tag) return;
  const existing = getTags();
  if (existing.includes(tag)) return;
  setTags([...existing, tag]);
  renderTag(tag);
}

tagText?.addEventListener("keydown", e => {
  if (e.key === " " || e.key === "Enter") {
    e.preventDefault();
    addTag(tagText.value);
    tagText.value = "";
  } else if (e.key === "Backspace" && tagText.value === "") {
    // verwijder laatste tag bij backspace op leeg veld
    const tags = getTags();
    if (!tags.length) return;
    const last = tags[tags.length - 1];
    setTags(tags.slice(0, -1));
    tagBox?.querySelector(`.tag-pill:last-of-type`)?.remove();
  }
});

tagBox?.addEventListener("click", () => tagText?.focus());

// bestaande tag pills klikbaar maken (al gerenderd via Jinja)
tagBox?.querySelectorAll(".tag-remove").forEach(btn => {
  btn.addEventListener("click", () => {
    const tag = btn.dataset.tag;
    const tags = getTags().filter(t => t !== tag);
    setTags(tags);
    btn.closest(".tag-pill").remove();
  });
});
