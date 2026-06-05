async function updateUnreadCount() {
  try {
    const resp = await fetch("/users/notifications/unread-count/", { headers: { "X-Requested-With": "fetch" } });
    if (!resp.ok) return;
    const data = await resp.json();
    const badge = document.getElementById("notifBadge");
    if (!badge) return;
    const count = Number(data.count || 0);
    badge.textContent = String(count);
    badge.classList.toggle("d-none", count <= 0);
  } catch (e) {
    // Тихо игнорируем ошибки сети
  }
}

updateUnreadCount();
setInterval(updateUnreadCount, 30000);

