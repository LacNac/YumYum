// Lấy các phần tử
const modal = document.getElementById("paymentModal");
const btn = document.querySelector(".btn-checkout"); // Nút bấm thanh toán của bạn
const closeBtn = document.querySelector(".close-btn");

// Mở modal khi bấm nút
btn.onclick = function() {
    modal.style.display = "block";
}

// Đóng modal khi bấm dấu x
closeBtn.onclick = function() {
    modal.style.display = "none";
}

// Đóng khi bấm ra ngoài vùng trắng
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}