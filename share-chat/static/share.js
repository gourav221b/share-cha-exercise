function tokenFromPath() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[parts.length - 1] || "";
}

function renderMessages(snapshot) {
  const messages = snapshot?.messages || [];
  if (!messages.length) {
    return Object.assign(document.createElement("div"), {
      className: "empty",
      textContent: "No messages in this share.",
    });
  }

  const card = document.createElement("div");
  card.className = "card";

  for (const msg of messages) {
    const block = document.createElement("div");
    block.className = "message";

    const role = document.createElement("div");
    role.className = "role";
    role.textContent = msg.role || "unknown";
    block.appendChild(role);

    const body = document.createElement("p");
    body.textContent = msg.content || "";
    block.appendChild(body);

    const names = [];
    for (const f of msg.uploaded_files || []) {
      if (f.filename) names.push(f.filename);
    }
    for (const f of msg.generated_file_names || []) {
      if (f.filename) names.push(f.filename);
    }
    if (names.length) {
      const files = document.createElement("div");
      files.className = "files";
      files.textContent = `Files: ${names.join(", ")}`;
      block.appendChild(files);
    }

    card.appendChild(block);
  }
  return card;
}

async function boot() {
  const token = tokenFromPath();
  const titleEl = document.getElementById("title");
  const banner = document.getElementById("banner");
  const messages = document.getElementById("messages");

  try {
    const res = await fetch(`/api/shares/${encodeURIComponent(token)}`);
    const text = await res.text();
    let body = null;
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = { detail: text };
      }
    }
    if (!res.ok) {
      titleEl.textContent = "Share unavailable";
      messages.className = "status error";
      messages.textContent = body?.detail || res.statusText;
      return;
    }

    const snapshot = body.snapshot || body;
    titleEl.textContent = body.title || snapshot.title || "Shared chat";
    if (snapshot.has_artifacts) {
      banner.hidden = false;
      banner.textContent =
        "This chat referenced files. Public shares only show filenames — download links are omitted.";
    }
    messages.replaceWith(renderMessages(snapshot));
  } catch (e) {
    messages.className = "status error";
    messages.textContent = e.message;
  }
}

boot();
