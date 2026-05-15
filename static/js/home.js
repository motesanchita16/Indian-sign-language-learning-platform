// static/js/home.js

// Poll label to update live preview label
let last = "";
async function pollHomeLabel(){
  try {
    const r = await fetch('/get_label');
    const txt = (await r.text()).trim();
    if(txt !== last){
      last = txt;
      const el = document.getElementById('live-label');
      if(el) el.innerText = txt || '...';
    }
  } catch (e) {
    console.error("Poll error:", e);
  }
}
setInterval(pollHomeLabel, 600);
pollHomeLabel();

// Speak preview button
document.addEventListener("click", (ev) => {
  if(ev.target && ev.target.id === "speak-preview"){
    const text = (document.getElementById('live-label') || {}).innerText || 'No sign';
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 0.95;
    speechSynthesis.speak(utter);
  }
});

// simple dark toggle on logo click (persist)
(function(){
  const theme = localStorage.getItem('theme');
  if(theme === 'dark') document.body.classList.add('dark');
  const logo = document.querySelector('.logo');
  if(logo){
    logo.style.cursor = 'pointer';
    logo.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    });
  }
})();
