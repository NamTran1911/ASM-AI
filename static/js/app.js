let currentOrderId = null;

window.onload = function () {
    checkHealth();
    loadOrders();

    document.getElementById("order-form").onsubmit = createOrder;
    document.getElementById("edit-form").onsubmit = updateOrder;
    document.getElementById("btn-predict").onclick = predictPriority;
    document.getElementById("btn-refresh").onclick = loadOrders;
    document.getElementById("btn-resend-email").onclick = resendEmail;
    document.getElementById("filter-priority").onchange = loadOrders;
    document.getElementById("filter-status").onchange = loadOrders;
    document.getElementById("search-input").oninput = loadOrders;
};

async function checkHealth() {
    const el = document.getElementById("api-status");
    try {
        const res = await fetch("/api/health");
        const data = await res.json();
        el.textContent = `Online | ML: ${data.ml_model} | LLM: ${data.llm}`;
        el.classList.add("online");
    } catch {
        el.textContent = "Mất kết nối server";
    }
}

async function loadOrders() {
    const priority = document.getElementById("filter-priority").value;
    const status = document.getElementById("filter-status").value;
    const search = document.getElementById("search-input").value.trim();

    let url = "/api/orders?";
    if (priority) url += `priority=${encodeURIComponent(priority)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;
    if (search) url += `search=${encodeURIComponent(search)}`;

    const res = await fetch(url);
    const orders = await res.json();

    document.getElementById("order-count").textContent = orders.length;
    const tbody = document.getElementById("orders-tbody");

    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Không có đơn hàng nào.</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>#${order.order_id}</td>
            <td><b>${escapeHtml(order.customer_name)}</b></td>
            <td>${escapeHtml(order.product_description)}</td>
            <td><span class="badge badge-${order.priority.toLowerCase()}">${order.priority}</span></td>
            <td>${order.status}</td>
            <td>${new Date(order.created_at).toLocaleString("vi-VN")}</td>
            <td class="actions">
                <button class="btn btn-outline" onclick="openLogs(${order.order_id})">Email</button>
                <button class="btn btn-secondary" onclick="openEdit(${order.order_id})">Sửa</button>
                <button class="btn btn-danger" onclick="deleteOrder(${order.order_id})">Xóa</button>
            </td>
        </tr>
    `).join("");
}

async function predictPriority() {
    const desc = document.getElementById("product_description").value.trim();
    if (!desc) {
        alert("Vui lòng nhập mô tả sản phẩm trước!");
        return;
    }

    const res = await fetch("/api/orders/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_description: desc }),
    });
    const data = await res.json();

    const box = document.getElementById("predict-result");
    box.style.display = "block";
    box.textContent = `AI dự đoán: ${data.priority} (độ tin cậy ${Math.round(data.confidence * 100)}%)`;
    document.getElementById("priority").value = data.priority;
}

async function createOrder(e) {
    e.preventDefault();
    const payload = {
        customer_name: document.getElementById("customer_name").value.trim(),
        product_description: document.getElementById("product_description").value.trim(),
        priority: document.getElementById("priority").value || null,
        status: document.getElementById("status").value,
    };

    const res = await fetch("/api/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        alert("Lỗi khi tạo đơn hàng!");
        return;
    }

    const created = await res.json();
    document.getElementById("order-form").reset();
    document.getElementById("predict-result").style.display = "none";
    await loadOrders();

    if (created.priority === "High") {
        alert(`Đơn #${created.order_id} có Priority High. Hệ thống đang tự động soạn email ở background!`);
    }
}

async function openEdit(orderId) {
    const res = await fetch(`/api/orders/${orderId}`);
    const order = await res.json();

    document.getElementById("edit-id").value = order.order_id;
    document.getElementById("edit-id-label").textContent = order.order_id;
    document.getElementById("edit-name").value = order.customer_name;
    document.getElementById("edit-desc").value = order.product_description;
    document.getElementById("edit-priority").value = order.priority;
    document.getElementById("edit-status").value = order.status;
    document.getElementById("edit-modal").classList.add("active");
}

async function updateOrder(e) {
    e.preventDefault();
    const orderId = document.getElementById("edit-id").value;
    const payload = {
        customer_name: document.getElementById("edit-name").value.trim(),
        product_description: document.getElementById("edit-desc").value.trim(),
        priority: document.getElementById("edit-priority").value,
        status: document.getElementById("edit-status").value,
    };

    await fetch(`/api/orders/${orderId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    closeModal("edit-modal");
    await loadOrders();
}

async function deleteOrder(orderId) {
    if (!confirm(`Bạn muốn xóa đơn hàng #${orderId}?`)) return;
    await fetch(`/api/orders/${orderId}`, { method: "DELETE" });
    await loadOrders();
}

async function openLogs(orderId) {
    currentOrderId = orderId;
    document.getElementById("log-modal-title").textContent = `Nhật ký email đơn hàng #${orderId}`;
    document.getElementById("log-modal").classList.add("active");
    await fetchLogs(orderId);
}

async function fetchLogs(orderId) {
    const body = document.getElementById("log-modal-body");
    const res = await fetch(`/api/orders/${orderId}/logs`);
    const logs = await res.json();

    if (logs.length === 0) {
        body.innerHTML = "<p>Chưa có email nào được tạo cho đơn hàng này.</p>";
        return;
    }

    body.innerHTML = logs.map(log => `
        <div class="log-item">
            <div><b>${escapeHtml(log.email_subject || "")}</b> - ${new Date(log.created_at).toLocaleString("vi-VN")}</div>
            <div class="log-content">${escapeHtml(log.email_content)}</div>
        </div>
    `).join("");
}

async function resendEmail() {
    if (!currentOrderId) return;
    await fetch(`/api/orders/${currentOrderId}/trigger-email`, { method: "POST" });
    setTimeout(() => fetchLogs(currentOrderId), 1200);
}

function closeModal(id) {
    document.getElementById(id).classList.remove("active");
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
