document.addEventListener("DOMContentLoaded", () => {

  /* ================= REVEAL SYSTEM ================= */

  document.querySelectorAll(".reveal").forEach((el, i) => {
    setTimeout(() => el.classList.add("active"), i * 220);
  });


  /* ================= CARD AI GLOW ================= */

  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("mousemove", () => {
      card.style.boxShadow = "0 0 45px rgba(0,200,255,0.35)";
    });
    card.addEventListener("mouseleave", () => {
      card.style.boxShadow = "0 0 25px rgba(0,160,255,0.15)";
    });
  });


  /* ================= NEURAL TITLE PULSE ================= */

  document.querySelectorAll(".title").forEach(t => {
    setInterval(() => {
      t.style.textShadow = `0 0 ${12 + Math.random()*25}px rgba(0,220,255,0.9)`;
    }, 700);
  });

});


/* ================= FAULT BAR ANIMATION ================= */

window.addEventListener("load", () => {
  document.querySelectorAll(".fault-bar-fill").forEach(bar => {
    const percent = bar.getAttribute("data-percent");
    setTimeout(() => {
      bar.style.width = percent + "%";
    }, 700);
  });
});


/* ================= SUPERNOVA LOADER ================= */

function startLoading() {
  const btn = document.getElementById("analyzeBtn");
  const loader = document.getElementById("loader");
  const back = document.getElementById("backLink");

  if (btn && loader) {
    btn.style.display = "none";
    if(back) back.style.display = "none";
    loader.classList.remove("hidden");
  }
  return true;
}
