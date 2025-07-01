 // Loading overlay
       window.addEventListener('load', function() {
           const loadingOverlay = document.getElementById('loadingOverlay');
           setTimeout(() => {
               loadingOverlay.style.opacity = '0';
               setTimeout(() => {
                   loadingOverlay.style.display = 'none';
               }, 500);
           }, 1000);
       });

       // Header scroll effect
       window.addEventListener('scroll', function() {
           const header = document.getElementById('header');
           if (window.scrollY > 100) {
               header.classList.add('scrolled');
           } else {
               header.classList.remove('scrolled');
           }
       });

       // Smooth scrolling for navigation links
       document.querySelectorAll('a[href^="#"]').forEach(anchor => {
           anchor.addEventListener('click', function (e) {
               e.preventDefault();
               const target = document.querySelector(this.getAttribute('href'));
               if (target) {
                   target.scrollIntoView({
                       behavior: 'smooth',
                       block: 'start'
                   });
               }
           });
       });

       // Fade in animation on scroll
       const observerOptions = {
           threshold: 0.1,
           rootMargin: '0px 0px -50px 0px'
       };

       const observer = new IntersectionObserver(function(entries) {
           entries.forEach(entry => {
               if (entry.isIntersecting) {
                   entry.target.classList.add('visible');
               }
           });
       }, observerOptions);

       document.querySelectorAll('.fade-in').forEach(el => {
           observer.observe(el);
       });

       // Form submission
       document.getElementById('contactForm').addEventListener('submit', function(e) {
           e.preventDefault();
           
           const formData = new FormData(this);
           const name = formData.get('name');
           const email = formData.get('email');
           const phone = formData.get('phone');
           const service = formData.get('service');
           const message = formData.get('message');
           
           // Create WhatsApp message
           const whatsappMessage = `Olá! Meu nome é ${name}.

*Dados de Contato:*
📧 E-mail: ${email}
📱 Telefone: ${phone || 'Não informado'}

*Serviço de Interesse:* ${service || 'Não especificado'}

*Mensagem:*
${message}

Gostaria de receber um orçamento e mais informações sobre os serviços da Divisions Tech.`;

           const whatsappURL = `https://wa.me/5511999999999?text=${encodeURIComponent(whatsappMessage)}`;
           
           // Open WhatsApp
           window.open(whatsappURL, '_blank');
           
           // Reset form
           this.reset();
           
           // Show success message
           alert('Obrigado pelo contato! Você será redirecionado para o WhatsApp para finalizar sua solicitação.');
       });

       // Mobile menu toggle (basic implementation)
       document.getElementById('mobileMenuToggle').addEventListener('click', function() {
           const navMenu = document.querySelector('.nav-menu');
           navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
       });

       // Counter animation for stats
       function animateCounters() {
           const counters = document.querySelectorAll('.stat-number');
           counters.forEach(counter => {
               const target = counter.textContent.replace(/[^\d]/g, '');
               const increment = target / 50;
               let current = 0;
               
               const updateCounter = () => {
                   if (current < target) {
                       current += increment;
                       counter.textContent = Math.ceil(current) + (counter.textContent.includes('%') ? '%' : '+');
                       setTimeout(updateCounter, 40);
                   } else {
                       counter.textContent = counter.textContent;
                   }
               };
               
               updateCounter();
           });
       }

       // Trigger counter animation when stats section is visible
       const statsObserver = new IntersectionObserver(function(entries) {
           entries.forEach(entry => {
               if (entry.isIntersecting) {
                   animateCounters();
                   statsObserver.unobserve(entry.target);
               }
           });
       });

       const statsSection = document.querySelector('.stats-grid');
       if (statsSection) {
           statsObserver.observe(statsSection);
       }

       // Cursor trail effect (optional enhancement)
       document.addEventListener('mousemove', function(e) {
           const cursor = document.createElement('div');
           cursor.style.cssText = `
               position: fixed;
               width: 4px;
               height: 4px;
               background: var(--primary-teal);
               border-radius: 50%;
               pointer-events: none;
               z-index: 9999;
               left: ${e.clientX}px;
               top: ${e.clientY}px;
               opacity: 0.7;
               transform: translate(-50%, -50%);
               animation: cursorFade 0.5s ease-out forwards;
           `;
           
           document.body.appendChild(cursor);
           
           setTimeout(() => {
               cursor.remove();
           }, 500);
       });

       // Add cursor fade animation
       const style = document.createElement('style');
       style.textContent = `
           @keyframes cursorFade {
               0% {
                   opacity: 0.7;
                   transform: translate(-50%, -50%) scale(1);
               }
               100% {
                   opacity: 0;
                   transform: translate(-50%, -50%) scale(0.5);
               }
           }
       `;
       document.head.appendChild(style);