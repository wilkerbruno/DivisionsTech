/* ============================================================
   DIVISIONS TECH — script.js  v4.0
   ============================================================ */

const $ = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);

// ── Loading — some IMEDIATAMENTE, sem esperar fontes ou rede ──
(function() {
  function hideLoading() {
    var ov = document.getElementById('loadingOverlay');
    if (!ov) return;
    ov.style.transition = 'opacity 0.2s ease';
    ov.style.opacity = '0';
    setTimeout(function() {
      ov.style.display = 'none';
    }, 220);
  }
  // Some assim que o DOM estiver pronto (não espera CSS externo, fontes ou imagens)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hideLoading);
  } else {
    hideLoading();
  }
  // Fallback absoluto: 800ms no máximo
  setTimeout(hideLoading, 800);
})();

// ── Header scroll ─────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const h = $('#header');
  if (h) h.classList.toggle('scrolled', window.scrollY > 60);
});

// ── Mark active nav link ──────────────────────────────────────
(function markActive() {
  const page = location.pathname.split('/').pop() || 'index.html';
  $$('.nav-link').forEach(a => {
    const href = (a.getAttribute('href') || '').split('/').pop();
    if (href === page) a.classList.add('active');
  });
})();

// ── Mobile menu ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const toggle  = $('#mobileMenuToggle');
  const menu    = $('#navMenu');
  const overlay = $('#navOverlay');

  const close = () => {
    menu && menu.classList.remove('active');
    overlay && overlay.classList.remove('active');
    document.body.style.overflow = '';
  };

  toggle && toggle.addEventListener('click', e => {
    e.stopPropagation();
    const open = menu.classList.toggle('active');
    overlay && overlay.classList.toggle('active', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  overlay && overlay.addEventListener('click', close);
  $$('.nav-link, .cta-button').forEach(l => l.addEventListener('click', close));
  window.addEventListener('resize', () => { if (window.innerWidth > 768) close(); });

  // ── Counter animation ────────────────────────────────────
  const statsObs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.querySelectorAll('.stat-number').forEach(el => {
        const raw    = el.textContent;
        const suffix = raw.replace(/[\d.]/g, '');
        const target = parseFloat(raw.replace(/[^\d.]/g, '')) || 0;
        let cur = 0;
        const tick = () => {
          cur = Math.min(cur + target / 50, target);
          el.textContent = (Number.isInteger(target) ? Math.ceil(cur) : cur.toFixed(1)) + suffix;
          if (cur < target) setTimeout(tick, 40);
        };
        tick();
      });
      statsObs.unobserve(entry.target);
    });
  }, { threshold: 0.4 });
  const sg = $('.stats-grid');
  if (sg) statsObs.observe(sg);

  // ── Portfolio filter ──────────────────────────────────────
  $$('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      $$('.filter-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      const cat = this.dataset.filter;
      $$('.portfolio-item').forEach(item => {
        const show = cat === 'all' || item.dataset.category === cat;
        item.style.opacity = show ? '1' : '0.3';
        item.style.transform = show ? '' : 'scale(0.97)';
        item.style.pointerEvents = show ? '' : 'none';
      });
    });
  });

  // ── Plan card hover dim ───────────────────────────────────
  $$('.plan-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      $$('.plan-card').forEach(c => { if (c !== card) c.style.opacity = '.7'; });
    });
    card.addEventListener('mouseleave', () => {
      $$('.plan-card').forEach(c => { c.style.opacity = ''; });
    });
  });

  // ── FAQ accordion ─────────────────────────────────────────
  $$('.faq-question').forEach(q => {
    q.addEventListener('click', () => {
      const item   = q.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      $$('.faq-item').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });

  // ── Contact form ──────────────────────────────────────────
  const form = $('#contactForm');
  if (form) {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const fd      = new FormData(form);
      const name    = fd.get('name');
      const email   = fd.get('email');
      const phone   = fd.get('phone')   || 'Não informado';
      const service = fd.get('service') || 'Não especificado';
      const message = fd.get('message');
      const btn     = form.querySelector('.form-submit');

      if (btn) { btn.disabled = true; btn.textContent = 'Enviando…'; }

      const waText = encodeURIComponent(
        `Olá! Meu nome é ${name}.\n\n📧 ${email}\n📱 ${phone}\n🛠 ${service}\n\n${message}`
      );

      const params = { from_name:name, reply_to:email, phone, service, message,
                       to_email:'wilker.gandra@divisionstech.com' };
      try {
        if (typeof emailjs !== 'undefined') {
          await emailjs.send('service_dyicxfy', 'template_a79ld1m', params);
        }
        window.open(`https://wa.me/5583993654478?text=${waText}`, '_blank');
        form.reset();
        alert('Mensagem enviada! Abrimos o WhatsApp para agilizar o atendimento 🚀');
      } catch {
        window.open(`https://wa.me/5583993654478?text=${waText}`, '_blank');
        alert('Redirecionamos para o WhatsApp para continuarmos o atendimento!');
      } finally {
        if (btn) { btn.disabled = false; btn.textContent = 'Enviar Mensagem'; }
      }
    });
  }
});

// ── Fade-in on scroll ─────────────────────────────────────────
const io = new IntersectionObserver(
  entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
  { threshold: 0.08, rootMargin: '0px 0px -30px 0px' }
);
document.addEventListener('DOMContentLoaded', () => {
  $$('.fade-in').forEach(el => io.observe(el));
});

/* ============================================================
   CHECKOUT — Fluxo de contratação de hospedagem
   ============================================================ */
// Detecta automaticamente a URL da API com base em onde o site está hospedado.
const API_BASE = (() => {
  const { hostname, protocol } = window.location;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }
  return `${protocol}//${window.location.host}/api`;
})();

const PLAN_INFO = {
  standard: { name: 'Standard', price: 'R$ 39,90/mês' },
  plus:     { name: 'Plus',     price: 'R$ 69,90/mês' },
  pro:      { name: 'Pro',      price: 'R$ 89,90/mês' },
};

let selectedPlan = '';

function startCheckout(plan) {
  selectedPlan = plan;
  const info = PLAN_INFO[plan];
  if (!info) return;

  // Atualiza labels do modal
  const el = id => document.getElementById(id);
  if (el('modalPlanName'))  el('modalPlanName').textContent  = info.name;
  if (el('modalPlanPrice')) el('modalPlanPrice').textContent = info.price;
  if (el('checkoutPlan'))   el('checkoutPlan').value         = plan;

  // Mostra passo 1 (domínio)
  showStep(1);
  openCheckoutModal();
}

function openCheckoutModal() {
  const modal = document.getElementById('checkoutModal');
  if (modal) { modal.classList.add('open'); document.body.style.overflow = 'hidden'; }
}

function closeCheckoutModal() {
  const modal = document.getElementById('checkoutModal');
  if (modal) { modal.classList.remove('open'); document.body.style.overflow = ''; }
  // Reseta formulário
  const form = document.getElementById('checkoutForm');
  if (form) form.reset();
  showStep(1);
  selectedPlan = '';
}

function showStep(n) {
  $$('.checkout-step').forEach(s => s.classList.remove('active'));
  const step = document.getElementById(`step${n}`);
  if (step) step.classList.add('active');
}

function chooseDomain(hasDomain) {
  document.getElementById('hasDomain').value = hasDomain ? '1' : '0';
  const domainRow = document.getElementById('domainRow');
  if (domainRow) domainRow.style.display = hasDomain ? 'block' : 'none';
  showStep(2);
}

async function submitCheckout(e) {
  e.preventDefault();
  const form = document.getElementById('checkoutForm');
  const btn  = form.querySelector('.checkout-submit-btn');
  btn.disabled = true;
  btn.textContent = 'Processando…';

  const data = {
    name:       form.querySelector('[name=name]').value,
    email:      form.querySelector('[name=email]').value,
    phone:      form.querySelector('[name=phone]').value,
    cpf:        form.querySelector('[name=cpf]')?.value || '',
    plan:       selectedPlan,
    has_domain: form.querySelector('[name=has_domain]').value === '1',
    domain:     form.querySelector('[name=domain]')?.value || '',
  };

  try {
    const r = await fetch(`${API_BASE}/payments/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!r.ok) throw new Error('Erro na API');
    const result = await r.json();

    // Redireciona para o Mercado Pago
    window.location.href = result.init_point;
  } catch (err) {
    console.error(err);
    alert('Não foi possível conectar ao servidor de pagamento.\nTente novamente ou entre em contato pelo WhatsApp.');
    btn.disabled = false;
    btn.textContent = 'Ir para Pagamento';
  }
}

window.startCheckout      = startCheckout;
window.closeCheckoutModal = closeCheckoutModal;
window.chooseDomain       = chooseDomain;
window.submitCheckout     = submitCheckout;