// 2. Logic điều khiển Modal và Kiểm tra thanh toán
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('payment-modal');
    const payBtn = document.getElementById('pay-bill-btn');
    const closeBtn = document.querySelector('.close-btn');

    // Hai phần nội dung bên trong Modal
    const qrSection = document.getElementById('qr-section');
    const successSection = document.getElementById('success-section');

    let paymentInterval = null;

    // Hàm bắt đầu kiểm tra trạng thái từ Server
    function startCheckingStatus() {
        if (paymentInterval) clearInterval(paymentInterval);

        paymentInterval = setInterval(() => {
            // Kiểm tra ORDER_ID (biến này khai báo ở script trong HTML)
            if (typeof ORDER_ID === "undefined" || !ORDER_ID || ORDER_ID === "None") return;

            fetch(`/check_payment/${ORDER_ID}`)
                .then(res => res.json())
                .then(data => {
                    console.log("Trạng thái đơn hàng:", data.status);

                    // Khi trạng thái chuyển thành "Chưa xong" (đã thanh toán qua Webhook)
                    if (data.status === "Chưa xong") {
                        clearInterval(paymentInterval);

                        // HIỆU ỨNG THAY THẾ NỘI DUNG NGAY TRÊN MODAL
                        if (qrSection && successSection) {
                            qrSection.style.display = "none";      // Ẩn mã QR
                            successSection.style.display = "block"; // Hiện tích xanh thành công
                        }

                        // Chờ 3 giây để khách thấy thông báo thành công rồi mới chuyển trang
                        setTimeout(() => {
                            window.location.href = "/myorders"; // Hoặc "/success" tùy bạn
                        }, 3000);
                    }
                })
                .catch(err => console.error("Lỗi API check_payment:", err));
        }, 3000); // Kiểm tra mỗi 3 giây
    }

    // Sự kiện khi bấm nút "Pay bill"
    if (payBtn) {
        payBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // Mỗi lần mở lại modal, reset lại giao diện (hiện QR, ẩn Success)
            if (qrSection) qrSection.style.display = "block";
            if (successSection) successSection.style.display = "none";

            modal.style.display = "block";
            startCheckingStatus();
            console.log("Đã mở Modal và đang kiểm tra đơn hàng:", ORDER_ID);
        });
    }

    // Hàm đóng Modal
    function closeModal() {
        modal.style.display = "none";
        if (paymentInterval) {
            clearInterval(paymentInterval);
            console.log("Đã đóng Modal và dừng kiểm tra.");
        }
    }

    if (closeBtn) closeBtn.onclick = closeModal;

    // Đóng Modal khi bấm vào vùng ngoài (overlay)
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    };
});