const navToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
}

const filterButtons = document.querySelectorAll('[data-filter]');
const filterItems = document.querySelectorAll('[data-category]');

if (filterButtons.length) {
  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.getAttribute('data-filter');
      filterButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');

      filterItems.forEach((item) => {
        const category = item.getAttribute('data-category');
        if (target === 'all' || category.includes(target)) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });
}

const contactForm = document.querySelector('#contact-form');
const formMessage = document.querySelector('.form-message');

if (contactForm) {
  contactForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const requiredFields = contactForm.querySelectorAll('[data-required]');
    let valid = true;

    requiredFields.forEach((field) => {
      if (!field.value.trim()) {
        valid = false;
        field.style.borderColor = '#dc3545';
      } else {
        field.style.borderColor = 'var(--border)';
      }
    });

    const emailField = contactForm.querySelector('input[type="email"]');
    if (emailField) {
      const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value.trim());
      if (!emailValid) {
        valid = false;
        emailField.style.borderColor = '#dc3545';
      }
    }

    if (formMessage) {
      if (valid) {
        formMessage.textContent = '感谢您的提交，我们将在24小时内与您联系。';
        formMessage.className = 'form-message success';
        formMessage.style.display = 'block';
        contactForm.reset();
      } else {
        formMessage.textContent = '请完整填写必填信息，并确认邮箱格式正确。';
        formMessage.className = 'form-message error';
        formMessage.style.display = 'block';
      }
    }
  });
}
