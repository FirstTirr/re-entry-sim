import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

window.addEventListener('error', function(e) {
  const errDiv = document.createElement('div');
  errDiv.style = "position: fixed; top: 0; left: 0; z-index: 9999; background: red; color: white; padding: 20px;";
  errDiv.innerHTML = e.error ? e.error.stack : e.message;
  document.body.appendChild(errDiv);
});

window.addEventListener('unhandledrejection', function(e) {
  const errDiv = document.createElement('div');
  errDiv.style = "position: fixed; top: 0; left: 0; z-index: 9999; background: red; color: white; padding: 20px;";
  errDiv.innerHTML = "Promise Error: " + (e.reason ? e.reason.stack : e.reason);
  document.body.appendChild(errDiv);
});

createApp(App).mount('#app')
