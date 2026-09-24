/**
 * CASA BACO — ENGINE INTERACTIVO DE CONVERSIÓN & UX
 * Script de interactividad: Simulador de catas, enlaces dinámicos a WhatsApp,
 * microestado en vivo, custom cursor Lagarto y checkout modal.
 */

document.addEventListener('DOMContentLoaded', () => {

  // --- 1. SIMULADOR INTERACTIVO DE CATAS A MEDIDA ---
  const guestsInput = document.getElementById('sim-guests');
  const guestsDisplay = document.getElementById('sim-guests-display');
  const guestsSummary = document.getElementById('sim-summary-guests');
  const pricePerPersonDisplay = document.getElementById('sim-price-per-person');
  const totalPriceDisplay = document.getElementById('sim-total-price');
  const whatsappBtn = document.getElementById('sim-whatsapp-btn');

  const styleCards = document.querySelectorAll('.style-option-card');
  const pairingCards = document.querySelectorAll('.pairing-option-card');

  function calculateSimulator() {
    if (!guestsInput) return;

    const numGuests = parseInt(guestsInput.value, 10);
    guestsDisplay.textContent = numGuests;
    if (guestsSummary) guestsSummary.textContent = numGuests;

    // Obtener precio del estilo seleccionado
    let basePrice = 32;
    let styleName = 'Iniciación al Vino';
    const checkedStyle = document.querySelector('input[name="experience-style"]:checked');
    if (checkedStyle) {
      basePrice = parseInt(checkedStyle.dataset.price, 10);
      styleCards.forEach(c => c.classList.remove('selected'));
      checkedStyle.closest('.style-option-card').classList.add('selected');
      
      if (checkedStyle.value === 'naturales') styleName = 'Vinos Naturales y Mínima Intervención';
      else if (checkedStyle.value === 'catalanes') styleName = '100% Vinos Catalanes Singulares';
      else styleName = 'Iniciación al Vino & Variedades de Autor';
    }

    // Obtener precio del maridaje seleccionado
    let pairingPrice = 12;
    let pairingName = 'Quesos de Pastor';
    const checkedPairing = document.querySelector('input[name="pairing-style"]:checked');
    if (checkedPairing) {
      pairingPrice = parseInt(checkedPairing.dataset.price, 10);
      pairingCards.forEach(c => c.classList.remove('selected'));
      checkedPairing.closest('.pairing-option-card').classList.add('selected');

      if (checkedPairing.value === 'embutidos') pairingName = 'Embutidos Artesanos de Autor';
      else if (checkedPairing.value === 'completo') pairingName = 'Maridaje Completo (Quesos + Embutidos + Tostas)';
      else pairingName = 'Quesos de Pastor Afinados';
    }

    const pricePerPerson = basePrice + pairingPrice;
    const totalPrice = pricePerPerson * numGuests;

    pricePerPersonDisplay.textContent = `${pricePerPerson} €`;
    totalPriceDisplay.textContent = `${totalPrice} €`;

    // Generar enlace pre-rellenado para WhatsApp Business
    const message = `¡Hola Casa Baco! Quisiera solicitar fecha para una Cata a Medida:\n\n` +
      `• Asistentes: ${numGuests} personas\n` +
      `• Estilo: ${styleName}\n` +
      `• Maridaje: ${pairingName}\n` +
      `• Presupuesto estimado: ${pricePerPerson}€/persona (${totalPrice}€ en total)\n\n` +
      `¿Podríais confirmarme disponibilidad para las próximas semanas? ¡Muchas gracias!`;

    const encodedMessage = encodeURIComponent(message);
    whatsappBtn.href = `https://wa.me/34600000000?text=${encodedMessage}`;
  }

  // Listeners para el simulador
  if (guestsInput) {
    guestsInput.addEventListener('input', calculateSimulator);
  }

  styleCards.forEach(card => {
    card.addEventListener('click', () => {
      const radio = card.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        calculateSimulator();
      }
    });
  });

  pairingCards.forEach(card => {
    card.addEventListener('click', () => {
      const radio = card.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        calculateSimulator();
      }
    });
  });

  // Cálculo inicial
  calculateSimulator();


  // --- 2. MODAL DE RESERVA DE CATAS DIRECTAS ---
  const bookingModal = document.getElementById('booking-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const modalCataTitle = document.getElementById('modal-cata-title');
  const modalCataDate = document.getElementById('modal-cata-date');
  const modalTotalPrice = document.getElementById('modal-total-price');
  const modalSeatsSelect = document.getElementById('modal-seats-select');
  let currentModalBasePrice = 38;

  document.querySelectorAll('.open-booking-modal').forEach(btn => {
    btn.addEventListener('click', () => {
      const cata = btn.dataset.cata || 'Cata Guiada';
      const fecha = btn.dataset.fecha || 'Próxima sesión';
      currentModalBasePrice = parseInt(btn.dataset.precio || '38', 10);

      modalCataTitle.textContent = cata;
      modalCataDate.textContent = fecha;
      updateModalTotal();
      bookingModal.classList.remove('hidden');
    });
  });

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
      bookingModal.classList.add('hidden');
    });
  }

  if (bookingModal) {
    bookingModal.addEventListener('click', (e) => {
      if (e.target === bookingModal) {
        bookingModal.classList.add('hidden');
      }
    });
  }

  if (modalSeatsSelect) {
    modalSeatsSelect.addEventListener('change', updateModalTotal);
  }

  function updateModalTotal() {
    if (!modalSeatsSelect || !modalTotalPrice) return;
    const seats = parseInt(modalSeatsSelect.value, 10);
    const total = seats * currentModalBasePrice;
    modalTotalPrice.textContent = `${total} €`;
  }


  // --- 3. SELECTOR DEL CLUB DEL LAGARTO (Recogida vs Envío) ---
  const btnStore = document.getElementById('club-mode-store');
  const btnDelivery = document.getElementById('club-mode-delivery');
  const planPriceVals = document.querySelectorAll('.plan-price-val');

  if (btnStore && btnDelivery) {
    btnStore.addEventListener('click', () => {
      btnStore.className = 'club-toggle-btn px-6 py-2.5 rounded-full text-xs font-semibold tracking-wider transition-all duration-200 bg-copper text-deep';
      btnDelivery.className = 'club-toggle-btn px-6 py-2.5 rounded-full text-xs font-semibold tracking-wider text-[#A8A29E] transition-all duration-200 hover:text-white';

      planPriceVals.forEach(el => {
        const base = parseInt(el.dataset.base, 10);
        el.textContent = `${base} €`;
      });
    });

    btnDelivery.addEventListener('click', () => {
      btnDelivery.className = 'club-toggle-btn px-6 py-2.5 rounded-full text-xs font-semibold tracking-wider transition-all duration-200 bg-copper text-deep';
      btnStore.className = 'club-toggle-btn px-6 py-2.5 rounded-full text-xs font-semibold tracking-wider text-[#A8A29E] transition-all duration-200 hover:text-white';

      planPriceVals.forEach(el => {
        const base = parseInt(el.dataset.base, 10) + 5;
        el.textContent = `${base} €`;
      });
    });
  }

  document.querySelectorAll('.subscribe-plan-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const plan = btn.dataset.plan || 'Plan del Club';
      const isDelivery = btnDelivery && btnDelivery.classList.contains('active-mode');
      const deliveryText = isDelivery ? 'con Envío a domicilio en Barcelona (+5€)' : 'con Recogida en tienda';
      const msg = `¡Hola Casa Baco! Quiero unirme a "El Club del Lagarto": ${plan} (${deliveryText}). ¿Cómo procedo al alta?`;
      window.open(`https://wa.me/34600000000?text=${encodeURIComponent(msg)}`, '_blank');
    });
  });


  // --- 4. CUSTOM CURSOR CON RASTRO DE LAGARTO (Desktop) ---
  const cursor = document.getElementById('custom-cursor');
  if (cursor && window.innerWidth > 1024) {
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursor.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
    });

    // Efecto sutil sobre elementos interactivos
    document.querySelectorAll('a, button, input, select, label').forEach(el => {
      el.addEventListener('mouseenter', () => {
        cursor.classList.add('scale-125');
      });
      el.addEventListener('mouseleave', () => {
        cursor.classList.remove('scale-125');
      });
    });
  }


  // --- 5. MENÚ MÓVIL TOGGLE ---
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });

    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
      });
    });
  }


  // --- 6. CÁLCULO DEL ESTADO DE APERTURA EN TIEMPO REAL (Barcelona Timezone) ---
  function updateStoreStatus() {
    const statusTextEl = document.getElementById('live-status-text');
    if (!statusTextEl) return;

    const now = new Date();
    // Obtener día de la semana (0: domingo, 1: lunes, ..., 6: sábado)
    const day = now.getDay();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const currentTimeDec = hours + minutes / 60;

    let isOpen = false;
    let closeHour = '21:30 h';

    if (day === 0) {
      statusTextEl.textContent = 'Cerrado hoy por descanso · Abrimos el martes a las 17:30 h';
    } else if (day === 1) {
      statusTextEl.textContent = 'Lunes cerrado · Visítanos mañana martes de 17:30 a 21:30 h';
    } else if (day >= 2 && day <= 4) { // Martes a Jueves: 17:30 a 21:30
      if (currentTimeDec >= 17.5 && currentTimeDec < 21.5) {
        statusTextEl.textContent = 'Abierto hoy hasta las 21:30 h';
      } else if (currentTimeDec < 17.5) {
        statusTextEl.textContent = 'Abrimos hoy a las 17:30 h · C/ Independència 305';
      } else {
        statusTextEl.textContent = 'Cerrado por hoy · Abrimos mañana a las 17:30 h';
      }
    } else if (day === 5) { // Viernes: 17:00 a 22:30
      if (currentTimeDec >= 17.0 && currentTimeDec < 22.5) {
        statusTextEl.textContent = 'Abierto hoy hasta las 22:30 h';
      } else if (currentTimeDec < 17.0) {
        statusTextEl.textContent = 'Abrimos hoy a las 17:00 h · C/ Independència 305';
      } else {
        statusTextEl.textContent = 'Cerrado por hoy · Abrimos mañana a las 11:30 h';
      }
    } else if (day === 6) { // Sábado: 11:30 a 15:00 y 17:30 a 22:30
      if ((currentTimeDec >= 11.5 && currentTimeDec < 15.0) || (currentTimeDec >= 17.5 && currentTimeDec < 22.5)) {
        statusTextEl.textContent = currentTimeDec < 15.0 ? 'Abierto hoy hasta las 15:00 h' : 'Abierto hoy hasta las 22:30 h';
      } else if (currentTimeDec >= 15.0 && currentTimeDec < 17.5) {
        statusTextEl.textContent = 'Pausa de tarde · Reabrimos a las 17:30 h';
      } else if (currentTimeDec < 11.5) {
        statusTextEl.textContent = 'Abrimos hoy a las 11:30 h · Sesión vermut y catas';
      } else {
        statusTextEl.textContent = 'Cerrado por hoy · Volvemos el martes';
      }
    }
  }

  updateStoreStatus();


  // --- 7. SPLASH SCREEN CINEMATOGRÁFICO (Fondo Negro con Logo Centrado) ---
  const splashScreen = document.getElementById('splash-screen');
  if (splashScreen) {
    const hideSplash = () => {
      setTimeout(() => {
        splashScreen.classList.add('splash-hidden');
        setTimeout(() => {
          splashScreen.style.display = 'none';
        }, 550);
      }, 750);
    };

    if (document.readyState === 'complete') {
      hideSplash();
    } else {
      window.addEventListener('load', hideSplash, { once: true });
    }

    // Fallback de seguridad
    setTimeout(() => {
      if (!splashScreen.classList.contains('splash-hidden')) {
        splashScreen.classList.add('splash-hidden');
        setTimeout(() => {
          splashScreen.style.display = 'none';
        }, 550);
      }
    }, 1800);
  }


  // --- 8. FÍSICA REACTIVA AL SCROLL: MOVIMIENTO 2D / 3D DE LA LAGARTIJA (OPCIÓN 3) ---
  const heroLizardStage = document.getElementById('hero-lizard-stage');
  const headerLizardIcon = document.getElementById('header-lizard-icon');

  if (heroLizardStage || headerLizardIcon) {
    let lastScrollY = window.scrollY;
    let scrollVelocity = 0;
    let targetTiltX = 0;
    let currentTiltX = 0;
    let targetTiltZ = 0;
    let currentTiltZ = 0;
    let targetTranslateY = 0;
    let currentTranslateY = 0;
    let targetHeaderRotate = 0;
    let currentHeaderRotate = 0;
    let isTicking = false;
    let mouseTiltX = 0;
    let mouseTiltY = 0;

    // Escuchar scroll para medir velocidad e inercia
    window.addEventListener('scroll', () => {
      const currentScrollY = window.scrollY;
      const delta = currentScrollY - lastScrollY;
      lastScrollY = currentScrollY;

      // Calcular velocidad con amortiguación
      scrollVelocity = delta;

      // Límites de inclinación orgánica según pantalla (más sutil en móvil)
      const isMobile = window.innerWidth < 768;
      const maxTiltX = isMobile ? 6 : 10;
      const maxTiltZ = isMobile ? 3 : 6;
      const maxHeaderRot = isMobile ? 12 : 20;

      // Parallax sutil de profundidad (máx 50px de recorrido)
      if (currentScrollY < window.innerHeight * 1.2) {
        targetTranslateY = Math.min(currentScrollY * 0.14, 50);
      }

      // Inclinación reactiva a la inercia del scroll
      targetTiltX = Math.max(Math.min(scrollVelocity * 0.4, maxTiltX), -maxTiltX);
      targetTiltZ = Math.max(Math.min(scrollVelocity * -0.25, maxTiltZ), -maxTiltZ);

      // Rotación orgánica de la mini lagartija del header
      targetHeaderRotate = Math.max(Math.min(scrollVelocity * 0.5, maxHeaderRot), -maxHeaderRot);

      if (!isTicking) {
        isTicking = true;
        requestAnimationFrame(updateLizardPhysics);
      }
    }, { passive: true });

    // Micro-interacción táctil con el ratón en escritorio sobre el Hero
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches && heroLizardStage) {
      const heroSection = document.getElementById('hero');
      if (heroSection) {
        heroSection.addEventListener('mousemove', (e) => {
          const rect = heroSection.getBoundingClientRect();
          const normX = (e.clientX - rect.left) / rect.width - 0.5;
          const normY = (e.clientY - rect.top) / rect.height - 0.5;
          mouseTiltY = normX * 8; // rotación lateral sutil
          mouseTiltX = -normY * 6; // inclinación vertical sutil
          if (!isTicking) {
            isTicking = true;
            requestAnimationFrame(updateLizardPhysics);
          }
        });

        heroSection.addEventListener('mouseleave', () => {
          mouseTiltX = 0;
          mouseTiltY = 0;
          if (!isTicking) {
            isTicking = true;
            requestAnimationFrame(updateLizardPhysics);
          }
        });
      }
    }

    // Bucle de física con interpolación suave (Lerp)
    function updateLizardPhysics() {
      // Retornar gradualmente la inercia a reposo
      scrollVelocity *= 0.88;
      targetTiltX *= 0.88;
      targetTiltZ *= 0.88;
      targetHeaderRotate *= 0.85;

      // Interpolación lineal (Lerp factor = 0.1)
      const lerpFactor = 0.1;
      currentTiltX += (targetTiltX + mouseTiltX - currentTiltX) * lerpFactor;
      currentTiltZ += (targetTiltZ - currentTiltZ) * lerpFactor;
      currentTranslateY += (targetTranslateY - currentTranslateY) * lerpFactor;
      currentHeaderRotate += (targetHeaderRotate - currentHeaderRotate) * lerpFactor;

      // Aplicar transformaciones al stage del Hero
      if (heroLizardStage) {
        const totalTiltY = mouseTiltY;
        heroLizardStage.style.transform = `translate3d(0, ${currentTranslateY.toFixed(2)}px, 0) rotateX(${currentTiltX.toFixed(2)}deg) rotateY(${totalTiltY.toFixed(2)}deg) rotateZ(${currentTiltZ.toFixed(2)}deg)`;
      }

      // Aplicar micro-rotación a la mini-lagartija del header
      if (headerLizardIcon) {
        headerLizardIcon.style.transform = `rotate(${currentHeaderRotate.toFixed(2)}deg)`;
      }

      // Comprobar si las fuerzas ya se han detenido para pausar el bucle rAF
      const isResting =
        Math.abs(scrollVelocity) < 0.05 &&
        Math.abs(currentTiltX - mouseTiltX) < 0.05 &&
        Math.abs(currentTiltZ) < 0.05 &&
        Math.abs(currentTranslateY - targetTranslateY) < 0.05 &&
        Math.abs(currentHeaderRotate) < 0.05;

      if (!isResting) {
        requestAnimationFrame(updateLizardPhysics);
      } else {
        isTicking = false;
      }
    }
  }

});
