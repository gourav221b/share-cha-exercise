async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  let body = null;
  const text = await res.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = { detail: text };
    }
  }
  if (!res.ok) {
    const detail = body?.detail || res.statusText;
    const err = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    err.status = res.status;
    throw err;
  }
  return body;
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "className") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2).toLowerCase(), v);
    else node.setAttribute(k, v);
  });
  for (const child of children) {
    if (child == null) continue;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

function renderChatCard(chat) {
  const status = el("div", { className: "status" });
  const shareBox = el("div", { className: "share-box", hidden: "true" });

  const createBtn = el("button", {
    text: "Create share link",
    onClick: async () => {
      createBtn.disabled = true;
      status.className = "status";
      status.textContent = "Creating…";
      try {
        const result = await api("/api/shares", {
          method: "POST",
          body: JSON.stringify({ chat_id: chat.id, ttl_days: 30 }),
        });
        const url = result.url || `/share/${result.token}`;
        const absolute = `${window.location.origin}${url.startsWith("/") ? url : `/${url}`}`;
        shareBox.hidden = false;
        shareBox.textContent = absolute;
        status.className = "status ok";
        status.textContent = `Share created${result.expires_at ? ` · expires ${result.expires_at}` : ""}`;
        openBtn.disabled = false;
        revokeBtn.disabled = false;
        openBtn.onclick = () => window.open(url, "_blank");
        revokeBtn.onclick = async () => {
          revokeBtn.disabled = true;
          try {
            await api(`/api/shares/${result.token}`, { method: "DELETE" });
            status.className = "status ok";
            status.textContent = "Share revoked.";
            shareBox.hidden = true;
            openBtn.disabled = true;
          } catch (e) {
            status.className = "status error";
            status.textContent = e.message;
            revokeBtn.disabled = false;
          }
        };
      } catch (e) {
        status.className = "status error";
        status.textContent = e.message;
      } finally {
        createBtn.disabled = false;
      }
    },
  });

  const openBtn = el("button", {
    className: "secondary",
    text: "Open link",
    disabled: "true",
  });
  const revokeBtn = el("button", {
    className: "danger",
    text: "Revoke",
    disabled: "true",
  });

  return el("article", { className: "card" }, [
    el("h2", { text: chat.title }),
    el("div", {
      className: "meta",
      text: `${chat.id} · ${chat.message_count} messages · owner ${chat.owner_id}`,
    }),
    el("div", { className: "row" }, [createBtn, openBtn, revokeBtn]),
    shareBox,
    status,
  ]);
}

async function boot() {
  const root = document.getElementById("list");
  try {
    const data = await api("/api/chats");
    root.className = "";
    root.replaceChildren(...data.chats.map(renderChatCard));
  } catch (e) {
    root.className = "status error";
    root.textContent = `Failed to load chats: ${e.message}`;
  }
}

boot();
