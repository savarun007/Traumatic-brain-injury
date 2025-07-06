// --- THEME TOGGLE LOGIC ---
const themeToggle = document.getElementById("theme-toggle");
const body = document.body;

function applySavedTheme() {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    body.classList.add("light-mode");
  }
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    body.classList.toggle("light-mode");
    if (body.classList.contains("light-mode")) {
      localStorage.setItem("theme", "light");
    } else {
      localStorage.setItem("theme", "dark");
    }
  });
}

// --- Glowing Cursor Effect ---
document.addEventListener("mousemove", (e) => {
  const cursorLight = document.querySelector(".cursor-light");
  if (cursorLight) {
    cursorLight.style.left = e.clientX + "px";
    cursorLight.style.top = e.clientY + "px";
  }
});

// --- Slideshow Logic ---
let slideIndex = 1;
let autoSlideTimeout;

function generateDots() {
  const slides = document.getElementsByClassName("slide-card");
  const dotsContainer = document.querySelector(".dots-container");
  if (!dotsContainer) return;
  dotsContainer.innerHTML = "";
  for (let i = 0; i < slides.length; i++) {
    const dot = document.createElement("span");
    dot.classList.add("dot");
    dot.setAttribute("onclick", `currentSlide(${i + 1})`);
    dotsContainer.appendChild(dot);
  }
}

function plusSlides(n) {
  clearTimeout(autoSlideTimeout);
  showSlides((slideIndex += n));
}

function currentSlide(n) {
  clearTimeout(autoSlideTimeout);
  showSlides((slideIndex = n));
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("slide-card");
  let dots = document.getElementsByClassName("dot");
  if (slides.length === 0 || dots.length === 0) return;

  if (n > slides.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = slides.length;
  }

  // First, hide all slides
  for (i = 0; i < slides.length; i++) {
    slides[i].classList.remove("active-slide");
    slides[i].classList.remove("fade");
  }
  // Then, deactivate all dots
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  // Now, show the correct slide and activate the correct dot
  slides[slideIndex - 1].classList.add("active-slide");
  slides[slideIndex - 1].classList.add("fade"); // Add fade class for animation
  dots[slideIndex - 1].className += " active";

  // Set timeout to restart automatic slideshow
  autoSlideTimeout = setTimeout(() => plusSlides(1), 20000);
}

// --- Initial setup when the page loads ---
document.addEventListener("DOMContentLoaded", () => {
  applySavedTheme();
  generateDots();
  showSlides(slideIndex); // This will now correctly show the first slide
});
