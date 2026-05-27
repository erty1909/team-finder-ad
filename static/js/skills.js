// Skills UI — supports entity-type="user" or "project"
(function(){
  document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("skills-container");
    if (!container) return;

    // Determine entity type and build base URLs
    const entityType = container.dataset.entityType || "project";
    const entityId   = container.dataset.entityId || container.dataset.projectId;
    const autocompleteUrl = entityType === "user" ? "/users/skills/" : "/projects/skills/";
    const addUrl          = entityType === "user"
      ? `/users/${entityId}/skills/add/`
      : `/projects/${entityId}/skills/add/`;
    const removeUrlBase   = entityType === "user"
      ? `/users/${entityId}/skills/`
      : `/projects/${entityId}/skills/`;

    const addBtn        = document.getElementById("add-skill-btn");
    const inputWrapper  = document.getElementById("skill-input-wrapper");
    const input         = document.getElementById("skill-input");
    const suggestions   = document.getElementById("skill-suggestions");

    if (!addBtn || !inputWrapper || !input || !suggestions) return;

    addBtn.addEventListener("click", () => {
      addBtn.classList.add("hidden");
      inputWrapper.classList.remove("hidden");
      input.value = "";
      suggestions.innerHTML = "";
      suggestions.classList.add("hidden");
      input.focus();
    });

    let t = null;
    input.addEventListener("input", () => {
      const q = input.value.trim();
      clearTimeout(t);
      if (!q) { suggestions.classList.add("hidden"); suggestions.innerHTML = ""; return; }
      t = setTimeout(async () => {
        const res = await fetch(`${autocompleteUrl}?q=${encodeURIComponent(q)}`);
        if (!res.ok) return;
        const data = await res.json();
        suggestions.innerHTML = "";
        data.forEach(s => {
          const li = document.createElement("li");
          li.textContent = s.name; li.dataset.id = s.id; li.className = "suggestion-item";
          suggestions.appendChild(li);
        });
        const exact = data.some(s => s.name.toLowerCase() === q.toLowerCase());
        if (!exact) {
          const liNew = document.createElement("li");
          liNew.textContent = `Создать «${q}»`; liNew.dataset.name = q; liNew.className = "create-new";
          suggestions.appendChild(liNew);
        }
        suggestions.classList.remove("hidden");
      }, 200);
    });

    suggestions.addEventListener("mousedown", async (e) => {
      const li = e.target.closest("li");
      if (!li) return;
      if (li.classList.contains("create-new")) await addSkillByName(li.dataset.name);
      else if (li.dataset.id) await addSkillById(li.dataset.id);
      hideInput();
    });

    input.addEventListener("keydown", async (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const q = input.value.trim();
        if (!q) return;
        const first = suggestions.querySelector("li");
        if (first && first.dataset.id) await addSkillById(first.dataset.id);
        else await addSkillByName(q);
        hideInput();
      }
      if (e.key === "Escape") hideInput();
    });

    input.addEventListener("blur", () => setTimeout(hideInput, 120));

    function hideInput() {
      inputWrapper.classList.add("hidden");
      suggestions.classList.add("hidden");
      addBtn.classList.remove("hidden");
    }

    container.addEventListener("click", async (e) => {
      if (e.target.classList.contains("remove-skill-btn")) {
        const chip = e.target.closest(".skill-chip");
        const skillId = chip.dataset.id;
        const res = await fetch(`${removeUrlBase}${skillId}/remove/`, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        if (res.ok) chip.remove();
      }
    });

    async function addSkillById(skillId) {
      const res = await fetch(addUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({ skill_id: skillId }),
      });
      if (res.ok) { const skill = await res.json(); appendChip(skill.skill_id || skill.id, skill.name); }
    }

    async function addSkillByName(name) {
      const res = await fetch(addUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({ name }),
      });
      if (res.ok) { const skill = await res.json(); appendChip(skill.skill_id || skill.id, skill.name); }
    }

    function appendChip(id, name) {
      if (container.querySelector(`.skill-chip[data-id="${id}"]`)) return;
      const chip = document.createElement("span");
      chip.className = "skill-chip"; chip.dataset.id = id;
      chip.innerHTML = `${name} <button type="button" class="remove-skill-btn" aria-label="Удалить" title="Удалить">×</button>`;
      container.insertBefore(chip, addBtn);
      const empty = container.querySelector(".skill-empty");
      if (empty) empty.remove();
    }

    function getCookie(name) {
      let v = null;
      if (document.cookie) {
        for (let c of document.cookie.split(";")) {
          c = c.trim();
          if (c.startsWith(name + "=")) { v = decodeURIComponent(c.substring(name.length + 1)); break; }
        }
      }
      return v;
    }
  });
})();
