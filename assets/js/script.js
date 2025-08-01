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

// ===== FORM SUBMISSION (EmailJS + WhatsApp) =====
document.getElementById('contactForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);

    const name = formData.get('name');
    const email = formData.get('email');
    const phone = formData.get('phone');
    const service = formData.get('service');
    const message = formData.get('message');

    // (Opcional) desabilitar botão para evitar duplo clique
    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.innerText || submitBtn.value;
        if (submitBtn.innerText !== undefined) submitBtn.innerText = 'Enviando...';
        if (submitBtn.value !== undefined) submitBtn.value = 'Enviando...';
    }

    // Monta mensagem do WhatsApp como você já fazia
    const whatsappMessage = `Olá! Meu nome é ${name}.

*Dados de Contato:*
📧 E-mail: ${email}
📱 Telefone: ${phone || 'Não informado'}

*Serviço de Interesse:* ${service || 'Não especificado'}

*Mensagem:*
${message}

Gostaria de receber um orçamento e mais informações sobre os serviços da Divisions Tech.`;

    const whatsappURL = `https://wa.me/5531994057689?text=${encodeURIComponent(whatsappMessage)}`;

    // ===== Envio por EmailJS =====
    // Preencha com seus IDs do EmailJS:
    const SERVICE_ID = 'service_dyicxfy';
    const TEMPLATE_ID = 'template_a79ld1m';

    // Params devem bater com as variáveis do seu template ({{from_name}}, {{reply_to}}, etc.)
    const templateParams = {
        from_name: name,
        reply_to: email,
        phone: phone || 'Não informado',
        service: service || 'Não especificado',
        message: message || '',
        // Opção B (destinatário via código). Garanta que o template use {{to_email}}.
        to_email: 'divisionstech@gmail.com'
    };

    try {
        await emailjs.send(SERVICE_ID, TEMPLATE_ID, templateParams);

        // Sucesso: WhatsApp opcional para agilizar o atendimento
        window.open(whatsappURL, '_blank');

        form.reset();
        alert('Obrigado pelo contato! Seu e-mail foi enviado com sucesso e abrimos o WhatsApp para finalizar sua solicitação.');
    } catch (err) {
        console.error('Falha no EmailJS:', err);
        // Fallback: ainda assim abre WhatsApp para você não perder o lead
        window.open(whatsappURL, '_blank');
        alert('Não foi possível enviar o e-mail agora. Abrimos o WhatsApp para dar continuidade ao atendimento.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            if (submitBtn.innerText !== undefined) submitBtn.innerText = submitBtn.dataset.originalText || 'Enviar';
            if (submitBtn.value !== undefined) submitBtn.value = submitBtn.dataset.originalText || 'Enviar';
        }
    }
});

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    const navOverlay = document.getElementById('navOverlay');
    const navLinks = document.querySelectorAll('.nav-link, .cta-button');

    // Toggle menu
    mobileMenuToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        navMenu.classList.toggle('active');
        navOverlay.classList.toggle('active');
        document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking overlay
    navOverlay.addEventListener('click', function() {
        navMenu.classList.remove('active');
        navOverlay.classList.remove('active');
        document.body.style.overflow = '';
    });


    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navMenu.classList.contains('active') && 
            !navMenu.contains(e.target) && 
            !mobileMenuToggle.contains(e.target)) {
            navMenu.classList.remove('active');
            navOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });


    // Close menu when clicking nav links
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
            navOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Close menu on window resize if open
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            navMenu.classList.remove('active');
            navOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
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