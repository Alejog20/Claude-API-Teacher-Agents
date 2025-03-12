/**
 * Plataforma de Aprendizaje Personalizado
 * Funcionalidad de chat con agentes
 */

// Configuración inicial
let currentAgent = 'coordinator';
let chatHistory = [];
let isWaitingForResponse = false;

// Inicialización del chat
function initializeChat() {
  // Seleccionar elementos del DOM
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.querySelector('.chat-messages');
  const agentSelector = document.querySelector('.agent-selector');
  
  // Cargar historial del chat si existe
  loadChatHistory();
  
  // Configurar el formulario de chat
  if (chatForm) {
    chatForm.addEventListener('submit', handleChatSubmit);
  }
  
  // Configurar selector de agentes
  if (agentSelector) {
    agentSelector.addEventListener('change', (event) => {
      changeAgent(event.target.value);
    });
  }
  
  // Ajustar altura del textarea al escribir
  if (chatInput) {
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
    });
  }
  
  // Mostrar mensaje de bienvenida si no hay historial
  if (chatHistory.length === 0) {
    addSystemMessage(getWelcomeMessage());
  }
}

/**
 * Maneja el envío del formulario de chat
 */
function handleChatSubmit(event) {
  event.preventDefault();
  
  const chatInput = document.getElementById('chat-input');
  const userMessage = chatInput.value.trim();
  
  if (userMessage && !isWaitingForResponse) {
    // Agregar mensaje del usuario al chat
    addUserMessage(userMessage);
    
    // Limpiar input y ajustar altura
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Obtener respuesta del agente
    getAgentResponse(userMessage);
  }
}

/**
 * Agrega un mensaje del usuario al chat
 */
function addUserMessage(message) {
  const chatMessages = document.querySelector('.chat-messages');
  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  const messageElement = document.createElement('div');
  messageElement.className = 'message message-user';
  messageElement.innerHTML = `
    <div>${escapeHtml(message)}</div>
    <div class="message-meta">${timestamp}</div>
  `;
  
  chatMessages.appendChild(messageElement);
  
  // Guardar en historial
  chatHistory.push({ role: 'user', content: message, timestamp });
  saveChatHistory();
  
  // Scroll al final
  scrollToBottom();
}

/**
 * Agrega un mensaje del agente al chat
 */
function addAgentMessage(message, agentName) {
  const chatMessages = document.querySelector('.chat-messages');
  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  const messageElement = document.createElement('div');
  messageElement.className = 'message message-agent';
  
  // Convertir texto a HTML con formato
  const formattedMessage = formatMessage(message);
  
  messageElement.innerHTML = `
    <div class="message-agent-name text-primary mb-1">${getAgentDisplayName(agentName || currentAgent)}</div>
    <div>${formattedMessage}</div>
    <div class="message-meta">${timestamp}</div>
  `;
  
  chatMessages.appendChild(messageElement);
  
  // Guardar en historial
  chatHistory.push({ 
    role: 'assistant', 
    content: message, 
    agent: agentName || currentAgent, 
    timestamp 
  });
  saveChatHistory();
  
  // Scroll al final
  scrollToBottom();
}

/**
 * Agrega un mensaje del sistema al chat
 */
function addSystemMessage(message) {
  const chatMessages = document.querySelector('.chat-messages');
  
  const messageElement = document.createElement('div');
  messageElement.className = 'message message-system p-3 bg-secondary rounded text-center';
  messageElement.innerHTML = message;
  
  chatMessages.appendChild(messageElement);
  
  // Scroll al final
  scrollToBottom();
}

/**
 * Obtiene respuesta del agente
 */
async function getAgentResponse(userMessage) {
  // Mostrar indicador de escritura
  showTypingIndicator();
  isWaitingForResponse = true;
  
  try {
    // Simulación de API para demostración
    // En producción, reemplazar por llamada real a la API
    const response = await simulateAgentResponse(userMessage);
    
    // Ocultar indicador de escritura
    hideTypingIndicator();
    
    // Mostrar respuesta
    addAgentMessage(response.message, response.agent);
    
    // Si el agente cambió, actualizar selector
    if (response.agent !== currentAgent && response.agent) {
      currentAgent = response.agent;
      updateAgentSelector();
    }
  } catch (error) {
    // Ocultar indicador de escritura
    hideTypingIndicator();
    
    // Mostrar error
    addSystemMessage(`
      <div class="text-danger">
        <i class="fas fa-exclamation-circle"></i> 
        Ocurrió un error al comunicarse con el agente. Por favor, intenta nuevamente.
      </div>
    `);
    console.error('Error al obtener respuesta:', error);
  } finally {
    isWaitingForResponse = false;
  }
}

/**
 * Simula una respuesta del agente (para demostración)
 */
function simulateAgentResponse(userMessage) {
  return new Promise((resolve) => {
    // Simular tiempo de respuesta variable
    const responseTime = 1000 + Math.random() * 2000;
    
    setTimeout(() => {
      let response;
      const lowerMessage = userMessage.toLowerCase();
      
      // Simular cambio de agente basado en preguntas
      let responseAgent = currentAgent;
      
      if (lowerMessage.includes('matemática') || lowerMessage.includes('problema') || 
          lowerMessage.includes('ecuación') || lowerMessage.includes('cálculo')) {
        responseAgent = 'mathematics';
      } else if (lowerMessage.includes('ciencia') || lowerMessage.includes('física') || 
                lowerMessage.includes('química') || lowerMessage.includes('biología')) {
        responseAgent = 'science';
      } else if (lowerMessage.includes('escribir') || lowerMessage.includes('redacción') || 
                lowerMessage.includes('gramática') || lowerMessage.includes('ensayo')) {
        responseAgent = 'language';
      }
      
      // Respuestas predefinidas basadas en el agente
      switch (responseAgent) {
        case 'coordinator':
          response = getCoordinatorResponse(userMessage);
          break;
        case 'mathematics':
          response = getMathematicsResponse(userMessage);
          break;
        case 'science':
          response = getScienceResponse(userMessage);
          break;
        case 'language':
          response = getLanguageResponse(userMessage);
          break;
        default:
          response = "Lo siento, no entendí tu pregunta. ¿Podrías reformularla?";
      }
      
      resolve({
        message: response,
        agent: responseAgent
      });
    }, responseTime);
  });
}

/**
 * Obtiene respuesta del agente coordinador
 */
function getCoordinatorResponse(userMessage) {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('hola') || lowerMessage.includes('saludos') || lowerMessage.includes('buenos días')) {
    return "¡Hola! Soy el Coordinador de Aprendizaje, ¿en qué puedo ayudarte hoy? Puedo guiarte sobre cualquier tema de estudio o derivarte con un especialista.";
  } else if (lowerMessage.includes('ayuda') || lowerMessage.includes('cómo funciona')) {
    return "Estoy aquí para ayudarte con tu aprendizaje personalizado. Puedes preguntarme sobre cualquier materia, y te conectaré con el especialista adecuado. También puedo mostrarte tu progreso y recomendarte lecciones.";
  } else if (lowerMessage.includes('quién eres') || lowerMessage.includes('qué haces')) {
    return "Soy tu Coordinador de Aprendizaje, diseñado para adaptar tu experiencia educativa a tus necesidades. Analizo tu nivel de conocimiento, identifico tus fortalezas y áreas de mejora, y te conecto con agentes especializados para maximizar tu potencial de aprendizaje.";
  } else {
    return "Entiendo que quieres saber más sobre eso. Dime específicamente qué tema te interesa aprender, y puedo coordinarte con el especialista más adecuado o recomendarte lecciones personalizadas.";
  }
}

/**
 * Obtiene respuesta del agente de matemáticas
 */
function getMathematicsResponse(userMessage) {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('ecuación') || lowerMessage.includes('resolver')) {
    return "Las ecuaciones son relaciones matemáticas que expresan la igualdad entre dos expresiones. Para resolverlas, buscamos el valor de la incógnita que hace verdadera la igualdad. ¿Te gustaría ver un ejemplo paso a paso?";
  } else if (lowerMessage.includes('derivada') || lowerMessage.includes('cálculo')) {
    return "Las derivadas nos ayudan a entender el ritmo de cambio de una función. Son fundamentales en cálculo y tienen múltiples aplicaciones en física, economía y otras ciencias. ¿Quieres que te explique el concepto con más detalle?";
  } else if (lowerMessage.includes('probabilidad') || lowerMessage.includes('estadística')) {
    return "La probabilidad cuantifica la posibilidad de que ocurra un evento. Es la base de la estadística, que nos permite analizar datos y hacer predicciones. ¿Hay algún concepto específico que te interese explorar?";
  } else {
    return "Como especialista en matemáticas, puedo ayudarte con álgebra, geometría, cálculo, probabilidad y más. ¿Qué concepto matemático específico te gustaría entender mejor?";
  }
}

/**
 * Obtiene respuesta del agente de ciencias
 */
function getScienceResponse(userMessage) {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('física') || lowerMessage.includes('movimiento') || lowerMessage.includes('fuerza')) {
    return "La física estudia las propiedades fundamentales de la materia, la energía, el espacio y el tiempo. Las leyes del movimiento de Newton son esenciales para entender cómo los objetos responden a las fuerzas. ¿Te gustaría explorar algún concepto físico específico?";
  } else if (lowerMessage.includes('química') || lowerMessage.includes('elemento') || lowerMessage.includes('molécula')) {
    return "La química examina la composición, estructura y propiedades de la materia. La tabla periódica es una herramienta fundamental que organiza los elementos según sus propiedades. ¿Hay algún tema químico que te interese especialmente?";
  } else if (lowerMessage.includes('biología') || lowerMessage.includes('célula') || lowerMessage.includes('organismo')) {
    return "La biología estudia los seres vivos y sus procesos vitales. Las células son la unidad básica de la vida, y cada organismo tiene características adaptadas a su entorno. ¿Qué aspecto de la biología te gustaría conocer mejor?";
  } else {
    return "Como especialista en ciencias, puedo ayudarte con física, química, biología y ciencias de la tierra. ¿Sobre qué fenómeno científico te gustaría aprender hoy?";
  }
}

/**
 * Obtiene respuesta del agente de lenguaje
 */
function getLanguageResponse(userMessage) {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('gramática') || lowerMessage.includes('sintaxis')) {
    return "La gramática es el conjunto de reglas que estructuran un lenguaje. Una buena comprensión de la sintaxis te permitirá expresar tus ideas con mayor claridad y precisión. ¿Hay alguna regla gramatical específica que te cause dificultad?";
  } else if (lowerMessage.includes('ensayo') || lowerMessage.includes('redacción')) {
    return "Para escribir un buen ensayo, es importante tener una tesis clara, argumentos sólidos y una estructura coherente. La redacción efectiva comunica ideas complejas de manera accesible. ¿Te gustaría que te guíe en el proceso de escritura?";
  } else if (lowerMessage.includes('literatura') || lowerMessage.includes('leer')) {
    return "La literatura nos permite explorar diferentes perspectivas y realidades. La lectura crítica desarrolla tu capacidad de análisis y enriquece tu comprensión del mundo. ¿Hay algún género o autor que te interese particularmente?";
  } else {
    return "Como especialista en lenguaje, puedo ayudarte con gramática, redacción, comprensión lectora y literatura. ¿Qué habilidad comunicativa te gustaría desarrollar hoy?";
  }
}

/**
 * Cambia el agente actual
 */
function changeAgent(agentId) {
  currentAgent = agentId;
  addSystemMessage(`Ahora estás conversando con: <strong>${getAgentDisplayName(agentId)}</strong>`);
}

/**
 * Actualiza el selector de agentes
 */
function updateAgentSelector() {
  const agentSelector = document.querySelector('.agent-selector');
  if (agentSelector) {
    agentSelector.value = currentAgent;
  }
}

/**
 * Muestra indicador de escritura
 */
function showTypingIndicator() {
  const chatMessages = document.querySelector('.chat-messages');
  
  // Crear indicador si no existe
  let typingIndicator = document.querySelector('.typing-indicator');
  if (!typingIndicator) {
    typingIndicator = document.createElement('div');
    typingIndicator.className = 'message message-agent typing-indicator';
    typingIndicator.innerHTML = `
      <div class="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
    chatMessages.appendChild(typingIndicator);
  }
  
  // Hacer visible
  typingIndicator.classList.remove('hidden');
  
  // Scroll al final
  scrollToBottom();
}

/**
 * Oculta indicador de escritura
 */
function hideTypingIndicator() {
  const typingIndicator = document.querySelector('.typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

/**
 * Obtiene nombre de visualización del agente
 */
function getAgentDisplayName(agentId) {
  const agentNames = {
    'coordinator': 'Coordinador de Aprendizaje',
    'mathematics': 'Especialista en Matemáticas',
    'science': 'Especialista en Ciencias',
    'language': 'Especialista en Lenguaje',
    'feedback': 'Analista de Progreso'
  };
  
  return agentNames[agentId] || 'Asistente';
}

/**
 * Obtiene mensaje de bienvenida
 */
function getWelcomeMessage() {
  return `
    <div class="welcome-message">
      <div class="text-primary mb-2">
        <i class="fas fa-robot fa-2x"></i>
      </div>
      <h3 class="mb-2">¡Bienvenido a tu Asistente de Aprendizaje!</h3>
      <p>Estoy aquí para ayudarte en tu camino de aprendizaje personalizado.</p>
      <p class="mt-2">¿Sobre qué tema te gustaría aprender hoy?</p>
    </div>
  `;
}

/**
 * Formatea un mensaje para mostrar con formato
 */
function formatMessage(text) {
  // Convertir saltos de línea a HTML
  let formatted = text.replace(/\n/g, '<br>');
  
  // Convertir asteriscos en negritas
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convertir guiones bajos en cursiva
  formatted = formatted.replace(/\_(.*?)\_/g, '<em>$1</em>');
  
  // Convertir listas
  const lines = formatted.split('<br>');
  let inList = false;
  
  for (let i = 0; i < lines.length; i++) {
    // Detectar elementos de lista
    if (lines[i].match(/^\d+\.\s/)) {
      if (!inList) {
        lines[i] = '<ol>' + lines[i].replace(/^\d+\.\s/, '<li>') + '</li>';
        inList = 'ol';
      } else if (inList === 'ol') {
        lines[i] = lines[i].replace(/^\d+\.\s/, '<li>') + '</li>';
      } else {
        lines[i - 1] += '</ul>';
        lines[i] = '<ol>' + lines[i].replace(/^\d+\.\s/, '<li>') + '</li>';
        inList = 'ol';
      }
    } else if (lines[i].match(/^[\-\*]\s/)) {
      if (!inList) {
        lines[i] = '<ul>' + lines[i].replace(/^[\-\*]\s/, '<li>') + '</li>';
        inList = 'ul';
      } else if (inList === 'ul') {
        lines[i] = lines[i].replace(/^[\-\*]\s/, '<li>') + '</li>';
      } else {
        lines[i - 1] += '</ol>';
        lines[i] = '<ul>' + lines[i].replace(/^[\-\*]\s/, '<li>') + '</li>';
        inList = 'ul';
      }
    } else if (inList) {
      lines[i - 1] += inList === 'ul' ? '</ul>' : '</ol>';
      inList = false;
    }
  }
  
  // Cerrar lista si es necesario
  if (inList) {
    lines[lines.length - 1] += inList === 'ul' ? '</ul>' : '</ol>';
  }
  
  return lines.join('<br>');
}

/**
 * Guarda el historial del chat en localStorage
 */
function saveChatHistory() {
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

/**
 * Carga el historial del chat desde localStorage
 */
function loadChatHistory() {
  const savedHistory = localStorage.getItem('chatHistory');
  if (savedHistory) {
    try {
      chatHistory = JSON.parse(savedHistory);
      
      // Restaurar historial en la interfaz
      const chatMessages = document.querySelector('.chat-messages');
      if (chatMessages) {
        chatMessages.innerHTML = '';
        
        chatHistory.forEach(message => {
          if (message.role === 'user') {
            addUserMessage(message.content);
          } else if (message.role === 'assistant') {
            addAgentMessage(message.content, message.agent);
          }
        });
      }
    } catch (error) {
      console.error('Error al cargar historial:', error);
      chatHistory = [];
    }
  }
}

/**
 * Hace scroll al final del chat
 */
function scrollToBottom() {
  const chatMessages = document.querySelector('.chat-messages');
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}