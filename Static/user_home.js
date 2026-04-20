let idx = 1
    const foods = document.getElementById("foods")
    const tong = foods.children.length -2
    const dotContainer = document.getElementById("dots")

    // Tạo dots
    for(let i = 0; i < tong; i++) {
        let dot = document.createElement("span")
        dot.classList.add("dot")
        dot.onclick = () => showSlide(i+1)
        dotContainer.appendChild(dot)
    }

    const dots = document.getElementsByClassName("dot")

    function updateDots() {
        for (let d of dots) d.classList.remove("active")
        let dot_idx = idx -1
        if (idx === 0) dot_idx = tong - 1
    if (idx === tong +1) dot_idx = 0

        dots[dot_idx].classList.add("active")
    }

    function showSlide(i) {
        idx = i
    foods.style.transition = "0.5s"
    foods.style.transform = `translateX(-${idx * 100}%)`
    updateDots()
}

    function nextSlide() {
        showSlide(idx + 1)
    }

    function prevSlide() {
        showSlide(idx - 1)
    }

    foods.addEventListener("transitionend", () => {
    if (idx === tong +1) {
        foods.style.transition = "none"
        idx = 1
        foods.style.transform = `translateX(-${idx * 100}%)`
    }

    if (idx === 0) {
        foods.style.transition = "none"
        idx = tong
        // mỗi lần chuyển ảnh sẽ sang trái 500px
        foods.style.transform = `translateX(-${idx * 100}%)`
    }
})

    setInterval(() => {
        nextSlide()
    }, 3000)

        showSlide(1)

   console.log(window.innerWidth);