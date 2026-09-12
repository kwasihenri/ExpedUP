document.addEventListener('DOMContentLoaded', () => {
  initFlyInAnimations();
  initNavScroll();
  initRoleMatrix();
  initPlatformModals();
  initLiveDemo();
});

function initFlyInAnimations() {
  const animatedElements = document.querySelectorAll('.fly-up, .fly-down, .fly-left, .fly-right, .fly-scale');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => {
          entry.target.classList.add('fly-in');
        }, parseInt(delay));
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -40px 0px'
  });

  animatedElements.forEach(el => observer.observe(el));
}

function initNavScroll() {
  const nav = document.querySelector('.lp-nav');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      nav?.classList.add('stuck');
    } else {
      nav?.classList.remove('stuck');
    }
  });
}

function initRoleMatrix() {
  const chips = document.querySelectorAll('.lp-role-chip');
  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
    });
  });
}

function initPlatformModals() {
  const modal = document.getElementById('platform-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const nameElem = document.getElementById('modal-platform-name');
  const iconElem = document.getElementById('modal-platform-icon');
  const form = document.getElementById('waitlist-form');

  const comingSoonBtns = document.querySelectorAll('[data-coming-soon]');

  comingSoonBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const platform = btn.dataset.comingSoon || 'Platform';
      const icon = btn.dataset.icon || 'fa-solid fa-desktop';

      if (nameElem) nameElem.textContent = platform;
      if (iconElem) iconElem.className = icon + ' lp-platform-icon';
      if (modal) modal.classList.add('active');
    });
  });

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = form.querySelector('input[type="email"]');
      if (emailInput && emailInput.value) {
        if (modal) modal.classList.remove('active');
        showToast(`Thank you! ${emailInput.value} has been added to early access.`);
        emailInput.value = '';
      }
    });
  }
}

function showToast(message) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<i class="fa-solid fa-circle-check" style="color:var(--sl-success);"></i> ${message}`;
  container.appendChild(toast);

  setTimeout(() => toast.classList.add('show'), 50);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function initLiveDemo() {
  const input = document.getElementById('demo-search-input');
  const btn = document.getElementById('demo-search-btn');
  const stack = document.getElementById('demo-stack-results');

  if (!input || !btn || !stack) return;

  btn.addEventListener('click', () => {
    const val = input.value.trim() || 'kwasihenri';
    runScan(val);
  });

  function runScan(target) {
    stack.style.opacity = '0.5';
    setTimeout(() => {
      stack.innerHTML = `
        <div class="lp-stack-card">
          <div class="lp-stack-head">
            <span class="lp-stack-title">EXPEDITION REPORT: ${target.toUpperCase()}</span>
            <span class="badge badge-success">Completed</span>
          </div>
          <div class="lp-stack-row">
            <span><i class="fa-brands fa-github" style="color:var(--sl-primary);"></i> GitHub Profile</span>
            <span class="lp-badge-ok">Active Match</span>
          </div>
          <div class="lp-stack-row">
            <span><i class="fa-brands fa-x-twitter" style="color:var(--sl-primary);"></i> X / Twitter</span>
            <span class="lp-badge-ok">Verified</span>
          </div>
          <div class="lp-stack-row">
            <span><i class="fa-solid fa-globe" style="color:var(--sl-success);"></i> Web Domain (${target.toLowerCase()}.dev)</span>
            <span class="lp-badge-warn">Available</span>
          </div>
        </div>
      `;
      stack.style.opacity = '1';
    }, 400);
  }
}
