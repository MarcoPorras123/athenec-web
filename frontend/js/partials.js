// =========================================
// Athenec - Header y Footer compartidos
// Se inyectan en <div id="header-slot"></div> y <div id="footer-slot"></div>
// Cada pagina indica cual link esta activo con data-page en <body>
// =========================================

const HEADER_HTML = `
<header class="bg-white border-b border-gray-200 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center gap-8">
        <a href="index.html" class="flex items-center gap-2" aria-label="Athenec - inicio">
          <img src="assets/logo-athenec.jpeg" alt="Athenec" class="h-10 w-auto rounded-md" />
        </a>
        <nav class="hidden lg:flex items-center gap-6 text-athenec-blue font-medium">
          <a href="software.html" data-nav="software" class="hover:text-athenec-magenta transition">Software</a>
          <a href="asesoria.html" data-nav="asesoria" class="hover:text-athenec-magenta transition">Aprender</a>
          <a href="equipos.html" data-nav="equipos" class="hover:text-athenec-magenta transition">Soporte</a>
          <a href="#" class="hover:text-athenec-magenta transition">Socios</a>
          <a href="#" class="hover:text-athenec-magenta transition">Acerca de nosotros</a>
        </nav>
      </div>
      <div class="flex items-center gap-4 text-athenec-blue">
        <button aria-label="Buscar" class="p-2 rounded-full hover:bg-athenec-graylite transition">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 10.5A6.5 6.5 0 1 1 4 10.5a6.5 6.5 0 0 1 13 0Z"/></svg>
        </button>
        <button aria-label="Idioma" class="p-2 rounded-full hover:bg-athenec-graylite transition flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 24" class="w-6 h-4 rounded-sm overflow-hidden"><rect width="36" height="8" fill="#c8102e"/><rect y="8" width="36" height="8" fill="#ffffff"/><rect y="16" width="36" height="8" fill="#c8102e"/></svg>
          <span class="text-xs font-semibold hidden sm:inline">ES</span>
        </button>
        <a href="mailto:contacto@athenec.com" aria-label="Contacto" class="p-2 rounded-full hover:bg-athenec-graylite transition">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"/></svg>
        </a>
        <button aria-label="Menu de servicios" class="p-2 rounded-full hover:bg-athenec-graylite transition">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><circle cx="5" cy="5" r="1.8"/><circle cx="12" cy="5" r="1.8"/><circle cx="19" cy="5" r="1.8"/><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/><circle cx="5" cy="19" r="1.8"/><circle cx="12" cy="19" r="1.8"/><circle cx="19" cy="19" r="1.8"/></svg>
        </button>
        <button id="mobileMenuBtn" aria-label="Menu" class="lg:hidden p-2 rounded-md hover:bg-athenec-graylite">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5"/></svg>
        </button>
      </div>
    </div>
    <nav id="mobileNav" class="hidden lg:hidden pb-4 flex-col gap-3 text-athenec-blue font-medium">
      <a href="software.html" class="block py-1">Software</a>
      <a href="asesoria.html" class="block py-1">Aprender</a>
      <a href="equipos.html" class="block py-1">Soporte</a>
    </nav>
  </div>
</header>
`;

const FOOTER_HTML = `
<footer class="bg-athenec-bluedark text-white mt-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
      <div class="md:col-span-1">
        <img src="assets/logo-athenec.jpeg" alt="Athenec" class="h-12 w-auto rounded-md logo-blend" />
        <p class="mt-3 text-white/70 text-sm leading-relaxed">Tecnologia, conocimiento y equipamiento para transformar tus ideas.</p>
        <a href="mailto:contacto@athenec.com" class="inline-flex items-center gap-1 mt-5 text-white hover:text-athenec-magenta font-medium">
          Contactenos
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/></svg>
        </a>
        <div class="flex items-center gap-4 mt-6">
          <a href="#" aria-label="Facebook" class="hover:text-athenec-magenta transition"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H8v-2.9h2.4V9.8c0-2.4 1.4-3.7 3.6-3.7 1 0 2.1.2 2.1.2v2.4h-1.2c-1.2 0-1.6.8-1.6 1.5v1.9h2.7l-.4 2.9h-2.3v7A10 10 0 0 0 22 12Z"/></svg></a>
          <a href="#" aria-label="X" class="hover:text-athenec-magenta transition"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M18.2 2H21l-6.6 7.5L22 22h-6.8l-4.8-6.2L4.7 22H2l7-8L2 2h6.9l4.4 5.8L18.2 2Zm-1.2 18h1.9L7.1 4H5.1L17 20Z"/></svg></a>
          <a href="#" aria-label="LinkedIn" class="hover:text-athenec-magenta transition"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M4.98 3.5A2.5 2.5 0 1 1 5 8.5a2.5 2.5 0 0 1-.02-5ZM3 9h4v12H3V9Zm7 0h3.8v1.7h.05c.53-1 1.83-2.06 3.77-2.06 4.03 0 4.78 2.65 4.78 6.1V21H18v-5.3c0-1.27-.02-2.9-1.77-2.9-1.77 0-2.04 1.38-2.04 2.8V21H10V9Z"/></svg></a>
          <a href="#" aria-label="YouTube" class="hover:text-athenec-magenta transition"><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path d="M23.5 7.2s-.2-1.6-.9-2.3c-.9-.9-1.9-.9-2.4-1C16.9 3.5 12 3.5 12 3.5s-4.9 0-8.2.4c-.5.1-1.5.1-2.4 1-.7.7-.9 2.3-.9 2.3S0 9 0 10.9v1.9c0 1.8.2 3.7.2 3.7s.2 1.6.9 2.3c.9.9 2.1.9 2.6 1 1.9.2 8.3.3 8.3.3s4.9 0 8.2-.4c.5-.1 1.5-.1 2.4-1 .7-.7.9-2.3.9-2.3s.2-1.8.2-3.7v-1.9c0-1.8-.2-3.6-.2-3.6ZM9.5 15V8.8L15.8 12 9.5 15Z"/></svg></a>
        </div>
      </div>
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-wider text-white/80">Compania</h3>
        <ul class="mt-4 space-y-2 text-white/70 text-sm">
          <li><a href="#" class="hover:text-white">Acerca de nosotros</a></li>
          <li><a href="#" class="hover:text-white">Prensa</a></li>
          <li><a href="#" class="hover:text-white">Trabaja con nosotros</a></li>
          <li><a href="#" class="hover:text-white">Sostenibilidad</a></li>
          <li><a href="#" class="hover:text-white">Certificacion</a></li>
        </ul>
      </div>
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-wider text-white/80">Comunidades</h3>
        <ul class="mt-4 space-y-2 text-white/70 text-sm">
          <li><a href="software.html" class="hover:text-white">Desarrolladores</a></li>
          <li><a href="asesoria.html" class="hover:text-white">Estudiantes</a></li>
          <li><a href="asesoria.html" class="hover:text-white">Investigadores</a></li>
          <li><a href="#" class="hover:text-white">Socios</a></li>
          <li><a href="#" class="hover:text-white">Eventos</a></li>
        </ul>
      </div>
      <div>
        <h3 class="text-sm font-semibold uppercase tracking-wider text-white/80">Recursos</h3>
        <ul class="mt-4 space-y-2 text-white/70 text-sm">
          <li><a href="#" class="hover:text-white">Accesibilidad</a></li>
          <li><a href="#" class="hover:text-white">Soporte tecnico</a></li>
          <li><a href="#" class="hover:text-white">Documentacion</a></li>
          <li><a href="#" class="hover:text-white">Terminos de uso</a></li>
          <li><a href="#" class="hover:text-white">Politica de privacidad</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-white/10 mt-10 pt-6 flex flex-col md:flex-row justify-between gap-2 text-xs text-white/60">
      <p>&copy; 2026 Athenec. Todos los derechos reservados.</p>
      <p>Hecho con &#10084; en Latinoamerica.</p>
    </div>
  </div>
</footer>
`;

// ---- Inyeccion + comportamiento comun ----
document.addEventListener('DOMContentLoaded', () => {
  const headerSlot = document.getElementById('header-slot');
  const footerSlot = document.getElementById('footer-slot');
  if (headerSlot) headerSlot.innerHTML = HEADER_HTML;
  if (footerSlot) footerSlot.innerHTML = FOOTER_HTML;

  // Marca el nav activo segun data-page en <body>
  const currentPage = document.body.dataset.page;
  if (currentPage) {
    document.querySelectorAll('[data-nav]').forEach(el => {
      if (el.dataset.nav === currentPage) {
        el.classList.add('text-athenec-magenta', 'font-bold');
      }
    });
  }

  // Toggle nav mobile
  const btn = document.getElementById('mobileMenuBtn');
  const nav = document.getElementById('mobileNav');
  btn?.addEventListener('click', () => {
    nav.classList.toggle('hidden');
    nav.classList.toggle('flex');
  });
});
