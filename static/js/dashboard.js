/**
 * Plataforma de Aprendizaje Personalizado
 * Funcionalidad del Dashboard
 */

// Inicialización del dashboard
function initializeDashboard() {
    // Cargar datos del estudiante
    fetchStudentData()
      .then(data => {
        renderDashboard(data);
      })
      .catch(error => {
        console.error('Error al cargar datos:', error);
        showErrorMessage('No se pudieron cargar tus datos de aprendizaje. Por favor, intenta más tarde.');
      });
    
    // Configurar selectores y filtros
    setupTimeRangeFilter();
    setupSubjectFilter();
    
    // Inicializar gráficos
    initializeCharts();
  }
  
  /**
   * Obtiene datos del estudiante
   */
  async function fetchStudentData() {
    // Simulación de datos para demostración
    // En producción, reemplazar por llamada real a la API
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user: {
            name: "Estudiante Ejemplo",
            level: "Intermedio",
            joinDate: "2023-01-15",
            totalStudyTime: 45.5 // horas
          },
          progress: {
            overall: 68,
            bySubject: [
              { id: 1, name: "Matemáticas", progress: 75, level: 4, lastActivity: "2023-04-15" },
              { id: 2, name: "Ciencias", progress: 60, level: 3, lastActivity: "2023-04-10" },
              { id: 3, name: "Lenguaje", progress: 82, level: 5, lastActivity: "2023-04-16" },
              { id: 4, name: "Historia", progress: 45, level: 2, lastActivity: "2023-03-20" }
            ]
          },
          recommendations: [
            { id: 101, title: "Ecuaciones Diferenciales", type: "lesson", subject: "Matemáticas", 
              description: "Aprende a resolver ecuaciones diferenciales de primer orden", 
              estimatedTime: 45 },
            { id: 102, title: "Práctica de Redacción", type: "exercise", subject: "Lenguaje", 
              description: "Ejercicios para mejorar tu escritura argumentativa", 
              estimatedTime: 30 },
            { id: 103, title: "La Revolución Industrial", type: "lesson", subject: "Historia", 
              description: "Causas y consecuencias de la Revolución Industrial", 
              estimatedTime: 60 }
          ],
          recentActivity: [
            { id: 201, title: "Fracciones Algebraicas", type: "lesson", subject: "Matemáticas", 
              date: "2023-04-15", status: "completed", score: 85 },
            { id: 202, title: "La Célula", type: "exercise", subject: "Ciencias", 
              date: "2023-04-10", status: "completed", score: 92 },
            { id: 203, title: "Análisis de Texto", type: "evaluation", subject: "Lenguaje", 
              date: "2023-04-02", status: "completed", score: 78 }
          ],
          studyHabits: {
            daysActive: [1, 0, 1, 1, 0, 1, 1], // Dom a Sáb
            timeBySubject: [
              { subject: "Matemáticas", hours: 20.5 },
              { subject: "Ciencias", hours: 12.3 },
              { subject: "Lenguaje", hours: 8.7 },
              { subject: "Historia", hours: 4.0 }
            ],
            timeByHour: [
              { hour: "6-9", percent: 10 },
              { hour: "9-12", percent: 15 },
              { hour: "12-15", percent: 20 },
              { hour: "15-18", percent: 30 },
              { hour: "18-21", percent: 20 },
              { hour: "21-24", percent: 5 }
            ]
          }
        });
      }, 500);
    });
  }
  
  /**
   * Renderiza el dashboard con los datos
   */
  function renderDashboard(data) {
    // Renderizar información del usuario
    renderUserInfo(data.user);
    
    // Renderizar tarjetas de progreso
    renderProgressCards(data.progress);
    
    // Renderizar sección de recomendaciones
    renderRecommendations(data.recommendations);
    
    // Renderizar actividad reciente
    renderRecentActivity(data.recentActivity);
    
    // Actualizar gráficos con los datos
    updateCharts(data.studyHabits, data.progress);
  }
  
  /**
   * Renderiza la información del usuario
   */
  function renderUserInfo(user) {
    const userInfoEl = document.querySelector('.user-info');
    
    if (!userInfoEl) return;
    
    userInfoEl.innerHTML = `
      <div class="dashboard-card">
        <div class="user-info-header flex items-center gap-3 mb-3">
          <div class="user-avatar rounded-full bg-primary text-white flex items-center justify-center" style="width: 50px; height: 50px;">
            ${getInitials(user.name)}
          </div>
          <div>
            <h2 class="text-xl font-bold">${user.name}</h2>
            <div class="text-secondary">Nivel: ${user.level}</div>
          </div>
        </div>
        <div class="user-stats flex gap-4 mt-4">
          <div class="user-stat">
            <div class="user-stat-label text-secondary">Tiempo de estudio</div>
            <div class="user-stat-value text-xl font-bold">${user.totalStudyTime.toFixed(1)} h</div>
          </div>
          <div class="user-stat">
            <div class="user-stat-label text-secondary">Miembro desde</div>
            <div class="user-stat-value">${formatDate(user.joinDate)}</div>
          </div>
        </div>
      </div>
    `;
  }
  
  /**
   * Renderiza las tarjetas de progreso
   */
  function renderProgressCards(progress) {
    const progressContainerEl = document.querySelector('.progress-container');
    
    if (!progressContainerEl) return;
    
    // Tarjeta de progreso general
    const overallProgressHtml = `
      <div class="dashboard-card">
        <div class="dashboard-card-title">
          <i class="fas fa-chart-line"></i>
          Progreso General
        </div>
        <div class="dashboard-card-value">${progress.overall}%</div>
        <div class="progress-bar">
          <div class="progress-bar-fill" style="width: ${progress.overall}%"></div>
        </div>
        <div class="dashboard-card-subtitle">
          Sigue así, vas por buen camino.
        </div>
      </div>
    `;
    
    // Tarjetas de progreso por materia
    const subjectProgressHtml = progress.bySubject.map(subject => `
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
          Nivel ${subject.level} · Última actividad: ${formatDate(subject.lastActivity)}
        </div>
      </div>
    `).join('');
    
    progressContainerEl.innerHTML = overallProgressHtml + subjectProgressHtml;
  }
  
  /**
   * Renderiza las recomendaciones
   */
  function renderRecommendations(recommendations) {
    const recommendationsEl = document.querySelector('.recommendations-container');
    
    if (!recommendationsEl) return;
    
    recommendationsEl.innerHTML = `
      <h2 class="section-title mb-4">Recomendaciones Personalizadas</h2>
      <div class="recommendations-grid dashboard-grid">
        ${recommendations.map(item => `
          <div class="dashboard-card">
            <div class="dashboard-card-title">
              <i class="fas fa-${item.type === 'lesson' ? 'book-open' : item.type === 'exercise' ? 'pencil-alt' : 'clipboard-check'}"></i>
              ${item.title}
            </div>
            <div class="text-secondary mb-2">${item.subject}</div>
            <p class="mb-3">${item.description}</p>
            <div class="flex justify-between items-center">
              <span class="text-secondary"><i class="far fa-clock"></i> ${item.estimatedTime} min</span>
              <a href="/${item.type}/${item.id}" class="btn btn-primary">
                ${item.type === 'lesson' ? 'Comenzar lección' : item.type === 'exercise' ? 'Realizar ejercicio' : 'Iniciar evaluación'}
              </a>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }
  
  /**
   * Renderiza la actividad reciente
   */
  function renderRecentActivity(activities) {
    const activityEl = document.querySelector('.recent-activity-container');
    
    if (!activityEl) return;
    
    activityEl.innerHTML = `
      <h2 class="section-title mb-4">Actividad Reciente</h2>
      <div class="activity-list">
        ${activities.map(activity => `
          <div class="dashboard-card mb-3">
            <div class="flex justify-between items-center">
              <div>
                <div class="font-bold">${activity.title}</div>
                <div class="text-secondary">${activity.subject} · ${formatDate(activity.date)}</div>
              </div>
              <div class="activity-score bg-${getScoreClass(activity.score)} rounded-full text-white w-10 h-10 flex items-center justify-center">
                ${activity.score}
              </div>
            </div>
            <div class="mt-2">
              <span class="status-badge bg-${getStatusClass(activity.status)} text-white text-xs px-2 py-1 rounded-full">
                ${formatStatus(activity.status)}
              </span>
              <span class="text-secondary text-sm">
                ${activity.type === 'lesson' ? 'Lección' : activity.type === 'exercise' ? 'Ejercicio' : 'Evaluación'}
              </span>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }
  
  /**
   * Inicializa los gráficos del dashboard
   */
  function initializeCharts() {
    // Inicializar contenedores de gráficos (si se está usando una librería de gráficos)
    // Por simplicidad, usaremos representaciones básicas en este ejemplo
    
    const studyHabitsEl = document.querySelector('.study-habits-container');
    
    if (!studyHabitsEl) return;
    
    studyHabitsEl.innerHTML = `
      <h2 class="section-title mb-4">Hábitos de Estudio</h2>
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="dashboard-card-title">
            <i class="fas fa-calendar-alt"></i>
            Días de Actividad
          </div>
          <div class="days-activity-chart mt-3 flex justify-between">
            <!-- El contenido se actualizará con los datos reales -->
          </div>
        </div>
        <div class="dashboard-card">
          <div class="dashboard-card-title">
            <i class="fas fa-clock"></i>
            Horario de Estudio
          </div>
          <div class="time-distribution-chart mt-3">
            <!-- El contenido se actualizará con los datos reales -->
          </div>
        </div>
        <div class="dashboard-card">
          <div class="dashboard-card-title">
            <i class="fas fa-book"></i>
            Tiempo por Materia
          </div>
          <div class="subject-time-chart mt-3">
            <!-- El contenido se actualizará con los datos reales -->
          </div>
        </div>
      </div>
    `;
  }
  
  /**
   * Actualiza los gráficos con datos
   */
  function updateCharts(studyHabits, progress) {
    // Actualizar gráfico de días de actividad
    const daysActivityEl = document.querySelector('.days-activity-chart');
    if (daysActivityEl) {
      const daysOfWeek = ['D', 'L', 'M', 'X', 'J', 'V', 'S'];
      
      daysActivityEl.innerHTML = studyHabits.daysActive.map((active, index) => `
        <div class="day-activity-item text-center">
          <div class="day-label text-secondary text-sm">${daysOfWeek[index]}</div>
          <div class="day-indicator mt-2 ${active ? 'bg-primary' : 'bg-secondary'}" 
               style="width: 24px; height: 24px; border-radius: 4px;"></div>
        </div>
      `).join('');
    }
    
    // Actualizar gráfico de distribución de tiempo
    const timeDistributionEl = document.querySelector('.time-distribution-chart');
    if (timeDistributionEl) {
      timeDistributionEl.innerHTML = `
        <div class="time-bars flex items-end justify-between h-32">
          ${studyHabits.timeByHour.map(timeSlot => `
            <div class="time-bar-container text-center">
              <div class="time-bar bg-primary rounded-t" 
                   style="height: ${timeSlot.percent * 1.2}px; width: 20px;"></div>
              <div class="time-label text-xs text-secondary mt-1">${timeSlot.hour}</div>
            </div>
          `).join('')}
        </div>
      `;
    }
    
    // Actualizar gráfico de tiempo por materia
    const subjectTimeEl = document.querySelector('.subject-time-chart');
    if (subjectTimeEl) {
      // Calcular el total de horas
      const totalHours = studyHabits.timeBySubject.reduce((sum, item) => sum + item.hours, 0);
      
      subjectTimeEl.innerHTML = `
        <div class="subject-bars">
          ${studyHabits.timeBySubject.map(subject => `
            <div class="subject-bar-container mb-3">
              <div class="flex justify-between mb-1">
                <div>${subject.subject}</div>
                <div>${subject.hours.toFixed(1)}h</div>
              </div>
              <div class="progress-bar">
                <div class="progress-bar-fill" 
                     style="width: ${(subject.hours / totalHours * 100).toFixed(0)}%"></div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }
  }
  
  /**
   * Configura el filtro de rango de tiempo
   */
  function setupTimeRangeFilter() {
    const timeRangeEl = document.querySelector('.time-range-filter');
    
    if (!timeRangeEl) return;
    
    timeRangeEl.innerHTML = `
      <div class="filter-container">
        <select class="time-range-select" id="time-range-select">
          <option value="week">Esta semana</option>
          <option value="month" selected>Este mes</option>
          <option value="3months">Últimos 3 meses</option>
          <option value="year">Este año</option>
        </select>
      </div>
    `;
    
    // Añadir evento de cambio
    const selectEl = document.getElementById('time-range-select');
    if (selectEl) {
      selectEl.addEventListener('change', () => {
        // Recargar datos con el nuevo rango
        fetchStudentData()
          .then(data => {
            renderDashboard(data);
          })
          .catch(error => {
            console.error('Error al filtrar datos:', error);
          });
      });
    }
  }
  
  /**
   * Configura el filtro de materias
   */
  function setupSubjectFilter() {
    const subjectFilterEl = document.querySelector('.subject-filter');
    
    if (!subjectFilterEl) return;
    
    // Cargar materias disponibles
    fetchAvailableSubjects()
      .then(subjects => {
        subjectFilterEl.innerHTML = `
          <div class="filter-container">
            <select class="subject-select" id="subject-select">
              <option value="all" selected>Todas las materias</option>
              ${subjects.map(subject => `
                <option value="${subject.id}">${subject.name}</option>
              `).join('')}
            </select>
          </div>
        `;
        
        // Añadir evento de cambio
        const selectEl = document.getElementById('subject-select');
        if (selectEl) {
          selectEl.addEventListener('change', () => {
            // Recargar datos con la materia seleccionada
            fetchStudentData()
              .then(data => {
                renderDashboard(data);
              })
              .catch(error => {
                console.error('Error al filtrar datos:', error);
              });
          });
        }
      })
      .catch(error => {
        console.error('Error al cargar materias:', error);
      });
  }
  
  /**
   * Obtiene las materias disponibles
   */
  async function fetchAvailableSubjects() {
    // Simulación de datos para demostración
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: 1, name: "Matemáticas" },
          { id: 2, name: "Ciencias" },
          { id: 3, name: "Lenguaje" },
          { id: 4, name: "Historia" }
        ]);
      }, 300);
    });
  }
  
  /**
   * Formatea una fecha en formato legible
   */
  function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  }
  
  /**
   * Obtiene las iniciales de un nombre
   */
  function getInitials(name) {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase();
  }
  
  /**
   * Obtiene la clase CSS para un puntaje
   */
  function getScoreClass(score) {
    if (score >= 90) return 'success';
    if (score >= 70) return 'primary';
    if (score >= 50) return 'warning';
    return 'danger';
  }
  
  /**
   * Obtiene la clase CSS para un estado
   */
  function getStatusClass(status) {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'pending': return 'secondary';
      default: return 'secondary';
    }
  }
  
  /**
   * Formatea un estado para mostrar
   */
  function formatStatus(status) {
    switch (status) {
      case 'completed': return 'Completado';
      case 'in_progress': return 'En progreso';
      case 'pending': return 'Pendiente';
      default: return status;
    }
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