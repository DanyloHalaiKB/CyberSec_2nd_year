/* =========================================================================
   Лабораторна робота №4 — Робота з JavaScript
   Галай Данило, КБ-205, варіант 7

   Зміст:
     1. localStorage — збереження та вивід інформації про ОС і браузер
     2. Fetch API  — відгуки з jsonplaceholder (posts/7/comments)
     3. Модальне вікно форми зворотного зв'язку через 60 секунд
     4. Перемикач денної/нічної теми (ручний + автоматичний за часом доби)
   ========================================================================= */

'use strict';

/* Номер варіанта — використовується у запиті до JSONPlaceholder */
const VARIANT = 7;

/* ---------------------------------------------------------------------------
   1. ЗБЕРІГАННЯ ДАНИХ У БРАУЗЕРІ (localStorage)
   ------------------------------------------------------------------------ */

/**
 * Збирає всю доступну інформацію про операційну систему та браузер.
 * navigator.platform офіційно застарілий, але методичка вимагає саме його,
 * тому читаємо його разом із сучасним navigator.userAgentData.
 */
function collectSystemInfo() {
  const info = {
    'User Agent': navigator.userAgent,
    'Платформа': navigator.platform,
    'Мова інтерфейсу': navigator.language,
    'Усі мови': (navigator.languages || []).join(', '),
    'Ядер процесора': navigator.hardwareConcurrency ?? 'невідомо',
    "Пам'ять пристрою (ГБ)": navigator.deviceMemory ?? 'невідомо',
    'Онлайн': navigator.onLine ? 'так' : 'ні',
    'Cookie увімкнені': navigator.cookieEnabled ? 'так' : 'ні',
    'Роздільна здатність екрана': `${screen.width}×${screen.height}`,
    'Розмір вікна': `${window.innerWidth}×${window.innerHeight}`,
    'Глибина кольору': `${screen.colorDepth} біт`,
    'Часовий пояс': Intl.DateTimeFormat().resolvedOptions().timeZone,
    'Зсув від UTC (хв)': new Date().getTimezoneOffset(),
    'Збережено': new Date().toLocaleString('uk-UA'),
  };

  // Сучасний API: дає назву й версію браузера без парсингу User Agent
  if (navigator.userAgentData) {
    info['Мобільний пристрій'] = navigator.userAgentData.mobile ? 'так' : 'ні';
    const brands = navigator.userAgentData.brands
      .map((b) => `${b.brand} ${b.version}`)
      .join(', ');
    if (brands) info['Браузер (UA-CH)'] = brands;
  }

  return info;
}

/**
 * localStorage зберігає ЛИШЕ рядки, тому об'єкт серіалізуємо через
 * JSON.stringify, а при зчитуванні розбираємо назад через JSON.parse.
 */
function saveSystemInfo() {
  const info = collectSystemInfo();
  localStorage.setItem('systemInfo', JSON.stringify(info));
  return info;
}

/** Виводить увесь вміст localStorage у підвалі сайту. */
function renderSystemInfo() {
  const list = document.getElementById('sysinfoList');
  if (!list) return;

  list.innerHTML = '';

  // Перебираємо ВСІ ключі localStorage, а не лише systemInfo
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const raw = localStorage.getItem(key);

    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = raw; // значення не є JSON — виводимо як є
    }

    if (parsed && typeof parsed === 'object') {
      for (const [field, value] of Object.entries(parsed)) {
        appendRow(list, `${key} → ${field}`, value);
      }
    } else {
      appendRow(list, key, parsed);
    }
  }
}

function appendRow(list, label, value) {
  const dt = document.createElement('dt');
  dt.textContent = label;

  const dd = document.createElement('dd');
  dd.textContent = String(value);

  list.append(dt, dd);
}

/* ---------------------------------------------------------------------------
   2. ДИНАМІЧНИЙ ВМІСТ ІЗ СЕРВЕРА (Fetch API)
   ------------------------------------------------------------------------ */

/**
 * Завантажує "відгуки" (коментарі) з безкоштовного тестового API.
 * Номер поста = номер варіанта (7).
 * async/await читається як послідовний код, але не блокує сторінку.
 */
async function loadReviews() {
  const box = document.getElementById('reviewsList');
  if (!box) return;

  const url = `https://jsonplaceholder.typicode.com/posts/${VARIANT}/comments`;

  try {
    const response = await fetch(url);

    // fetch НЕ кидає помилку на 404/500 — статус треба перевіряти вручну
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const comments = await response.json();
    renderReviews(comments);
  } catch (error) {
    box.innerHTML =
      `<p class="reviews__status reviews__status--error">
         Не вдалося завантажити відгуки: ${error.message}
       </p>`;
    console.error('Помилка завантаження відгуків:', error);
  }
}

/** Відображає відгуки В ПОРЯДКУ ЇХ ОТРИМАННЯ (масив не сортуємо). */
function renderReviews(comments) {
  const box = document.getElementById('reviewsList');
  box.innerHTML = '';

  comments.forEach((comment, index) => {
    const card = document.createElement('article');
    card.className = 'review';

    const head = document.createElement('div');
    head.className = 'review__head';

    const name = document.createElement('h3');
    name.className = 'review__name';
    name.textContent = `${index + 1}. ${comment.name}`;

    const email = document.createElement('a');
    email.className = 'review__email';
    email.href = `mailto:${comment.email}`;
    email.textContent = comment.email;

    const body = document.createElement('p');
    body.className = 'review__body';
    body.textContent = comment.body;

    head.append(name, email);
    card.append(head, body);
    box.append(card);
  });
}

/* ---------------------------------------------------------------------------
   3. МОДАЛЬНЕ ВІКНО ФОРМИ ЗВОРОТНОГО ЗВ'ЯЗКУ
   ------------------------------------------------------------------------ */

const MODAL_DELAY_MS = 60_000; // 1 хвилина

function initContactModal() {
  const modal = document.getElementById('contactModal');
  const closeBtn = document.getElementById('modalClose');
  const backdrop = modal?.querySelector('[data-close]');
  const form = document.getElementById('contactForm');
  const status = document.getElementById('formStatus');

  if (!modal) return;

  const openModal = () => {
    // якщо користувач уже закривав вікно в цій сесії — більше не показуємо
    if (sessionStorage.getItem('modalDismissed') === 'true') return;
    modal.hidden = false;
    document.body.classList.add('is-modal-open');
    closeBtn?.focus();
  };

  const closeModal = () => {
    modal.hidden = true;
    document.body.classList.remove('is-modal-open');
    sessionStorage.setItem('modalDismissed', 'true');
  };

  // Таймер на 60 секунд
  setTimeout(openModal, MODAL_DELAY_MS);

  closeBtn?.addEventListener('click', closeModal);
  backdrop?.addEventListener('click', closeModal);

  // Закриття клавішею Escape
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.hidden) closeModal();
  });

  // Попередження, якщо ендпойнт Formspree ще не підставлений
  form?.addEventListener('submit', (event) => {
    if (form.action.includes('ВАШ_ЕНДПОЙНТ')) {
      event.preventDefault();
      status.textContent =
        'Форма не надіслана: у атрибуті action ще стоїть заглушка ' +
        'ВАШ_ЕНДПОЙНТ. Замініть її на ендпойнт із formspree.io.';
      status.className = 'form__status form__status--error';
    }
  });
}

/* ---------------------------------------------------------------------------
   4. ПЕРЕМИКАЧ ДЕННОЇ / НІЧНОЇ ТЕМИ
   ------------------------------------------------------------------------ */

const DAY_START = 7;  // 07:00
const DAY_END = 21;   // 21:00

/** Денна тема з 07:00 до 21:00, нічна — в увесь інший час. */
function themeByTime() {
  const hours = new Date().getHours();
  return hours >= DAY_START && hours < DAY_END ? 'light' : 'dark';
}

function applyTheme(theme) {
  const isDark = theme === 'dark';

  document.body.classList.toggle('dark-mode', isDark);

  const btn = document.getElementById('themeToggle');
  const icon = document.getElementById('themeToggleIcon');
  const text = document.getElementById('themeToggleText');

  if (btn) btn.setAttribute('aria-pressed', String(isDark));
  if (icon) icon.textContent = isDark ? '☀' : '🌙';
  if (text) text.textContent = isDark ? 'Денна тема' : 'Нічна тема';

  localStorage.setItem('theme', theme);
}

function initTheme() {
  // Пріоритет: ручний вибір користувача → автовизначення за часом доби
  const saved = localStorage.getItem('theme');
  applyTheme(saved || themeByTime());

  document.getElementById('themeToggle')?.addEventListener('click', () => {
    const current = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });
}

/* ---------------------------------------------------------------------------
   ТОЧКА ВХОДУ
   ------------------------------------------------------------------------ */

document.addEventListener('DOMContentLoaded', () => {
  saveSystemInfo();     // 1. записали дані про ОС/браузер у localStorage
  initTheme();          // 4. тема (до рендеру, щоб не блимало)
  renderSystemInfo();   // 1. вивели весь localStorage у підвалі
  loadReviews();        // 2. запит на сервер за відгуками
  initContactModal();   // 3. таймер модального вікна
});
