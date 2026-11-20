let currentViewingOrderId = null;

document.addEventListener("DOMContentLoaded", () => {
    checkSystemHealth();
    loadOrders();
    bindEvents();
});

function bindEvents() {
    // Form tao don hang
    const orderForm = document.getElementById("order-form");
    if (orderForm) {
        orderForm.addEventListener("submit", handleCreateOrder);
    }

    // Nut du doan priority bang AI
    const btnPredict = document.getElementById("btn-predict");
    if (btnPredict) {
        btnPredict.addEventListener("click", handlePredictPriority);
    }

    // Form cap nhat don hang
    const editForm = document.getElementById("edit-order-form");
    if (editForm) {
        editForm.addEventListener("submit", handleUpdateOrder);
    }

    // Bo loc va tim kiem
    const searchInput = document.getElementById("search-input");
    const filterPriority = document.getElementById("filter-priority");
    const filterStatus = document.getElementById("filter-status");
    const btnRefresh = document.getElementById("btn-refresh");

    if (searchInput) searchInput.addEventListener("input", debounce(loadOrders, 300));
    if (filterPriority) filterPriority.addEventListener("change", loadOrders);
    if (filterStatus) filterStatus.addEventListener("change", loadOrders);
    if (btnRefresh) btnRefresh.addEventListener("click", loadOrders);

    // Nut kich hoat lai email phan hoi
    const btnManualEmail = document.getElementById("btn-manual-email");
    if (btnManualEmail) {
        btnManualEmail.addEventListener("click", handleTriggerEmail);
    }
}

async function checkSystemHealth() {
    const statusEl = document.getElementById("api-status");
    try {
        const res = await fetch("/api/health");
        const data = await res.json();
        if (data.status === "ok") {
            statusEl.textContent = `Hệ thống hoạt động | DB: ${data.database} | LLM: ${data.llm_provider}`;
            statusEl.classList.add("online");
        } else {
            statusEl.textContent = "Hệ thống phản hồi bất thường";
        }
    } catch (err) {
        statusEl.textContent = "Mất kết nối máy chủ";
    }
}

async function loadOrders() {
    const tbody = document.getElementById("orders-tbody");
    const priority = document.getElementById("filter-priority")?.value || "";
    const status = document.getElementById("filter-status")?.value || "";
    const search = document.getElementById("search-input")?.value || "";

    const params = new URLSearchParams();
    if (priority) params.append("priority", priority);
    if (status) params.append("status", status);
    if (search) params.append("search", search);

    try {
        const res = await fetch(`/api/orders?${params.toString()}`);
        if (!res.ok) throw new Error("Khong the tai danh sach");
        const orders = await res.json();

        updateStats(orders);
        renderOrdersTable(orders);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Lỗi khi tải dữ liệu đơn hàng.</td></tr>`;
    }
}

function updateStats(orders) {
    const total = orders.length;
    const high = orders.filter(o => o.priority === "High").length;
    const pending = orders.filter(o => o.status === "Pending").length;
    const completed = orders.filter(o => o.status === "Completed").length;

    document.getElementById("stat-total").textContent = total;
    document.getElementById("stat-high").textContent = high;
    document.getElementById("stat-pending").textContent = pending;
    document.getElementById("stat-completed").textContent = completed;
}

function renderOrdersTable(orders) {
    const tbody = document.getElementById("orders-tbody");
    if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Chưa có đơn hàng nào phù hợp.</td></tr>`;
        return;
    }

    tbody.innerHTML = orders.map(order => {
        const priorityBadgeClass = `badge-${order.priority.toLowerCase()}`;
        const statusBadgeClass = `badge-status ${order.status.toLowerCase()}`;
        const dateStr = formatDate(order.created_at);

        return `
            <tr>
                <td>#${order.order_id}</td>
                <td><strong>${escapeHtml(order.customer_name)}</strong></td>
                <td>${escapeHtml(order.product_description)}</td>
                <td><span class="badge ${priorityBadgeClass}">${order.priority}</span></td>
                <td><span class="badge ${statusBadgeClass}">${order.status}</span></td>
                <td>${dateStr}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-outline btn-sm" onclick="openLogModal(${order.order_id})">Nhật ký</button>
                        <button class="btn btn-secondary btn-sm" onclick="openEditModal(${order.order_id})">Sửa</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteOrder(${order.order_id})">Xóa</button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

async function handlePredictPriority() {
    const descInput = document.getElementById("product_description");
    const resultBox = document.getElementById("predict-result");
    const prioritySelect = document.getElementById("priority");

    const description = descInput.value.trim();
    if (!description) {
        alert("Vui lòng nhập mô tả sản phẩm trước khi dự đoán.");
        descInput.focus();
        return;
    }

    resultBox.style.display = "block";
    resultBox.textContent = "Đang phân tích mô tả với mô hình Machine Learning...";

    try {
        const res = await fetch("/api/orders/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_description: description })
        });
        if (!res.ok) throw new Error("Loi du doan");
        const data = await res.json();

        const confidencePct = Math.round(data.confidence * 100);
        resultBox.textContent = `Kết quả dự đoán: ${data.priority} (Độ tin cậy: ${confidencePct}%)`;

        // Tu dong chon option tuong ung tren form
        if (prioritySelect) {
            prioritySelect.value = data.priority;
        }
    } catch (err) {
        resultBox.textContent = "Không thể dự đoán vào lúc này. Vui lòng chọn thủ công.";
    }
}

async function handleCreateOrder(e) {
    e.preventDefault();
    const btnSubmit = document.getElementById("btn-submit-order");
    const customerName = document.getElementById("customer_name").value.trim();
    const description = document.getElementById("product_description").value.trim();
    const priority = document.getElementById("priority").value;
    const status = document.getElementById("status").value;

    if (!customerName || !description) {
        alert("Vui lòng điền đủ tên khách hàng và mô tả sản phẩm.");
        return;
    }

    btnSubmit.disabled = true;
    btnSubmit.textContent = "Đang xử lý...";

    try {
        const payload = {
            customer_name: customerName,
            product_description: description,
            priority: priority || undefined,
            status: status
        };

        const res = await fetch("/api/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Lỗi khi tạo đơn hàng");
        const newOrder = await res.json();

        // Lam sach form
        document.getElementById("order-form").reset();
        document.getElementById("predict-result").style.display = "none";

        await loadOrders();

        if (newOrder.priority === "High") {
            alert(`Đơn hàng #${newOrder.order_id} là đơn High Priority. Hệ thống đã kích hoạt Background Task để tự động soạn email phản hồi!`);
        }
    } catch (err) {
        alert("Không thể tạo đơn hàng. Vui lòng thử lại.");
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Tạo đơn hàng";
    }
}

async function openEditModal(orderId) {
    try {
        const res = await fetch(`/api/orders/${orderId}`);
        if (!res.ok) throw new Error("Khong the tai don hang");
        const order = await res.json();

        document.getElementById("edit-order-id").value = order.order_id;
        document.getElementById("edit-order-id-label").textContent = order.order_id;
        document.getElementById("edit-customer-name").value = order.customer_name;
        document.getElementById("edit-product-description").value = order.product_description;
        document.getElementById("edit-priority").value = order.priority;
        document.getElementById("edit-status").value = order.status;

        document.getElementById("edit-modal").classList.add("active");
    } catch (err) {
        alert("Lỗi khi mở form chỉnh sửa đơn hàng.");
    }
}

function closeEditModal() {
    document.getElementById("edit-modal").classList.remove("active");
}

async function handleUpdateOrder(e) {
    e.preventDefault();
    const orderId = document.getElementById("edit-order-id").value;
    const customerName = document.getElementById("edit-customer-name").value.trim();
    const description = document.getElementById("edit-product-description").value.trim();
    const priority = document.getElementById("edit-priority").value;
    const status = document.getElementById("edit-status").value;

    try {
        const res = await fetch(`/api/orders/${orderId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_name: customerName,
                product_description: description,
                priority: priority,
                status: status
            })
        });

        if (!res.ok) throw new Error("Loi cap nhat");
        closeEditModal();
        await loadOrders();
    } catch (err) {
        alert("Không thể cập nhật đơn hàng.");
    }
}

async function deleteOrder(orderId) {
    if (!confirm(`Bạn có chắc chắn muốn xóa đơn hàng #${orderId}?`)) return;

    try {
        const res = await fetch(`/api/orders/${orderId}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Loi khi xoa");
        await loadOrders();
    } catch (err) {
        alert("Lỗi khi xóa đơn hàng.");
    }
}

async function openLogModal(orderId) {
    currentViewingOrderId = orderId;
    const modal = document.getElementById("log-modal");
    const title = document.getElementById("modal-title");
    const body = document.getElementById("modal-logs-body");

    title.textContent = `Nhật ký xử lý & Email cho đơn hàng #${orderId}`;
    body.innerHTML = "Đang tải nhật ký từ OrderLogs...";
    modal.classList.add("active");

    await fetchAndRenderLogs(orderId);
}

async function fetchAndRenderLogs(orderId) {
    const body = document.getElementById("modal-logs-body");
    try {
        const res = await fetch(`/api/orders/${orderId}/logs`);
        if (!res.ok) throw new Error("Loi tai nhat ky");
        const logs = await res.json();

        if (!logs || logs.length === 0) {
            body.innerHTML = `
                <div class="text-muted">
                    Chưa có nhật ký nào cho đơn hàng này.<br>
                    (Email tự động chỉ kích hoạt cho đơn hàng High Priority qua Background Task).
                </div>
            `;
            return;
        }

        body.innerHTML = logs.map(log => `
            <div class="log-item">
                <div class="log-item-header">
                    <span>Hành động: <strong>${log.action}</strong></span>
                    <span>${formatDate(log.created_at)}</span>
                </div>
                <div style="font-size: 0.85rem; margin-bottom: 6px;">
                    <strong>Tiêu đề:</strong> ${escapeHtml(log.email_subject || "Không có")} | 
                    <strong>Người nhận:</strong> ${escapeHtml(log.recipient || "Khách hàng")} | 
                    <strong>Trạng thái:</strong> ${log.status}
                </div>
                <div class="log-item-content">${escapeHtml(log.email_content)}</div>
            </div>
        `).join("");
    } catch (err) {
        body.innerHTML = '<div class="text-muted">Lỗi khi tải nhật ký.</div>';
    }
}

function closeLogModal() {
    document.getElementById("log-modal").classList.remove("active");
    currentViewingOrderId = null;
}

async function handleTriggerEmail() {
    if (!currentViewingOrderId) return;
    const btn = document.getElementById("btn-manual-email");
    btn.disabled = true;
    btn.textContent = "Đang yêu cầu...";

    try {
        const res = await fetch(`/api/orders/${currentViewingOrderId}/trigger-email`, { method: "POST" });
        if (!res.ok) throw new Error("Loi");
        
        // Doi 1.5 giay de background task hoan tat roi load lai
        setTimeout(async () => {
            await fetchAndRenderLogs(currentViewingOrderId);
            btn.disabled = false;
            btn.textContent = "Tạo lại email phản hồi";
        }, 1500);
    } catch (err) {
        alert("Lỗi kích hoạt background task.");
        btn.disabled = false;
        btn.textContent = "Tạo lại email phản hồi";
    }
}

function formatDate(isoStr) {
    if (!isoStr) return "";
    const d = new Date(isoStr);
    return d.toLocaleString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
        day: "2-digit",
        month: "2-digit",
        year: "numeric"
    });
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
