/**
 * Plataforma de Aprendizaje Personalizado
 * Javascript principal
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
  });
  
  /**
   * Inicializa la aplicación
   */
  function initializeApp() {
    // Configurar toggles de la interfaz
    setupSidebarToggle();
    setupDarkModeToggle();
    
    // Inicializar componentes según la página actual
    initializeCurrentPage();
    
    // Configurar navegación
    setupNavigation();
    
    // Configurar dropdown de usuario
    setupUserDropdown();
  }
  
  /**
   * Configura el botón para abrir/cerrar la barra lateral en móviles
   */
  function setupSidebarToggle() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
      
      // Cerrar sidebar cuando se hace clic fuera
      document.addEventListener('click', (event) => {
        if (sidebar.classList.contains('open') && 
            !sidebar.contains(event.target) && 
            event.target !== sidebarToggle) {
          sidebar.classList.remove('open');
        }
      });
    }
  }
  
  /**
   * Configura el botón de modo oscuro
   */
  function setupDarkModeToggle() {
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    
    if (darkModeToggle) {
      // Comprobar preferencia guardada
      const isDarkMode = localStorage.getItem('darkMode') === 'true';
      
      // Aplicar modo oscuro si está guardado
      if (isDarkMode) {
        document.body.classList.add('dark-theme');
        darkModeToggle.setAttribute('aria-pressed', 'true');
      }
      
      // Configurar toggle
      darkModeToggle.addEventListener('click', () => {
        const isCurrentlyDark = document.body.classList.toggle('dark-theme');
        localStorage.setItem('darkMode', isCurrentlyDark.toString());
        darkModeToggle.setAttribute('aria-pressed', isCurrentlyDark.toString());
      });
    }
  }
  
  /**
   * Inicializa componentes específicos de la página actual
   */
  function initializeCurrentPage() {
    const currentPage = document.body.dataset.page;
    
    // Marcar ítem activo en la navegación
    const activeNavItem = document.querySelector(`.nav-item[data-page="${currentPage}"]`);
    if (activeNavItem) {
      activeNavItem.classList.add('active');
    }
    
    // Inicializar componentes específicos según la página
    switch (currentPage) {
      case 'dashboard':
        initializeDashboard();
        break;
      case 'chat':
        initializeChat();
        break;
      case 'lesson':
        initializeLesson();
        break;
      case 'evaluation':
        initializeEvaluation();
        break;
    }
  }
  
  /**
   * Configura la navegación entre páginas
   */
  function setupNavigation() {
    // Prevenir comportamiento por defecto y cargar página con AJAX
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (event) => {
        if (!item.classList.contains('active')) {
          // Aquí podríamos implementar navegación SPA con AJAX
          // Por ahora, simplemente navegar normalmente
        }
      });
    });
  }
  
  /**
   * Configura el dropdown del usuario
   */
  function setupUserDropdown() {
    const userDropdown = document.querySelector('.user-dropdown-toggle');
    const userMenu = document.querySelector('.user-dropdown-menu');
    
    if (userDropdown && userMenu) {
      userDropdown.addEventListener('click', (event) => {
        event.stopPropagation();
        userMenu.classList.toggle('hidden');
      });
      
      // Cerrar al hacer clic fuera
      document.addEventListener('click', () => {
        if (!userMenu.classList.contains('hidden')) {
          userMenu.classList.add('hidden');
        }
      });
    }
  }
  
  /**
   * Inicializa la página del dashboard
   */
  function initializeDashboard() {
    // Cargar datos de progreso
    fetchUserProgress()
      .then(data => {
        updateProgressCharts(data);
        updateRecommendations(data);
      })
      .catch(error => {
        console.error('Error al cargar datos de progreso:', error);
        showErrorMessage('No se pudieron cargar los datos de progreso. Por favor, intenta más tarde.');
      });
  }
  
  /**
   * Obtiene datos de progreso del usuario
   */
  async function fetchUserProgress() {
    // Simulación de datos para demostración
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          overallProgress: 68,
          subjects: [
            { id: 1, name: 'Matemáticas', progress: 75, lastActivity: '2023-04-15' },
            { id: 2, name: 'Ciencias', progress: 60, lastActivity: '2023-04-10' },
            { id: 3, name: 'Lenguaje', progress: 82, lastActivity: '2023-04-16' },
          ],
          recommendations: [
            { id: 101, title: 'Ecuaciones Diferenciales', type: 'lesson' },
            { id: 102, title: 'Práctica de Redacción', type: 'exercise' }
          ]
        });
      }, 500);
    });
  }
  
  /**
   * Actualiza gráficos de progreso
   */
  function updateProgressCharts(data) {
    // Actualizar barra de progreso general
    const overallProgressEl = document.querySelector('.overall-progress-value');
    const overallProgressBarEl = document.querySelector('.overall-progress-bar-fill');
    
    if (overallProgressEl && overallProgressBarEl) {
      overallProgressEl.textContent = `${data.overallProgress}%`;
      overallProgressBarEl.style.width = `${data.overallProgress}%`;
    }
    
    // Actualizar tarjetas de materias
    const subjectsContainer = document.querySelector('.subjects-container');
    if (subjectsContainer && data.subjects.length) {
      subjectsContainer.innerHTML = data.subjects.map(subject => `
        <div class="dashboard-card">
          <div class="dashboard-card-title">
            <i class="fas fa-book"></i>
            ${subject.name}
          </div>
          <div class="dashboard-card-value">${subject.progress}%</div>
          <div class="progress-bar">
            <div class="progress-bar-fill" style="width: ${subject.progress}%"></div>
          </div>
          <div class="dashboard-card-subtitle">
            Última actividad: ${formatDate(subject.lastActivity)}
          </div>
        </div>
      `).join('');
    }
  }
  
  /**
   * Actualiza sección de recomendaciones
   */
  function updateRecommendations(data) {
    const recommendationsContainer = document.querySelector('.recommendations-container');
    if (recommendationsContainer && data.recommendations.length) {
      recommendationsContainer.innerHTML = data.recommendations.map(item => `
        <div class="dashboard-card">
          <div class="dashboard-card-title">
            <i class="fas fa-${item.type === 'lesson' ? 'book-open' : 'pencil-alt'}"></i>
            ${item.title}
          </div>
          <div class="dashboard-card-subtitle">
            ${item.type === 'lesson' ? 'Lección recomendada' : 'Ejercicio práctico'}
          </div>
          <a href="/${item.type}/${item.id}" class="btn btn-primary mt-3">
            ${item.type === 'lesson' ? 'Comenzar lección' : 'Realizar ejercicio'}
          </a>
        </div>
      `).join('');
    }
  }
  
  /**
   * Formatea una fecha en formato legible
   */
  function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  }
  
  /**
   * Muestra un mensaje de error
   */
  function showErrorMessage(message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-message p-3 mb-4 bg-danger text-white rounded';
    errorContainer.innerHTML = `
      <div class="flex items-center gap-2">
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
      </div>
    `;
    
    const contentContainer = document.querySelector('.content-container');
    if (contentContainer) {
      contentContainer.prepend(errorContainer);
      
      // Eliminar después de 5 segundos
      setTimeout(() => {
        errorContainer.remove();
      }, 5000);
    }
  }