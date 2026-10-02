/* =========================================================================
   Лабораторна робота №6 — Бекенд-сервіс на Node.js
   Галай Данило, КБ-205
   Варіант 7 → фреймворк Koa, додаткове поле phone (необов'язкове)

   Що робить сервер:
     1. віддає статичний сайт із public/
     2. приймає POST /api/contact, валідує дані
     3. дописує звернення у data/feedback.jsonl (формат JSON Lines)
     4. слухає 0.0.0.0:3000 — доступний з іншого пристрою локальної мережі
   ========================================================================= */

import Koa from 'koa';
import Router from '@koa/router';
import serve from 'koa-static';
import { bodyParser } from '@koa/bodyparser';

import { mkdir, appendFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/* ---------- Шляхи ---------------------------------------------------------
   __dirname недоступний у ES-модулях, тому обчислюємо його вручну.
   Усі шляхи будуються від каталогу проєкту через node:path — так сервер
   працює незалежно від того, з якої теки його запустили.
   ------------------------------------------------------------------------ */
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PUBLIC_DIR = path.join(__dirname, 'public');
const DATA_DIR = path.join(__dirname, 'data');          // ПОЗА public/
const DATA_FILE = path.join(DATA_DIR, 'feedback.jsonl');

const HOST = '0.0.0.0';
const PORT = 3000;

const MAX_BODY = '10kb';

/* ---------- Правила валідації --------------------------------------------- */
const LIMITS = {
  name: 60,
  email: 120,
  subject: 120,
  message: 1000,
  phone: 30,
};

// Базова перевірка формату пошти: щось@щось.домен без пробілів
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

// Варіант 7: поле phone необов'язкове; якщо заповнене — лише + цифри пробіли ( ) -
const PHONE_RE = /^[+0-9 ()-]+$/;

/**
 * Перевіряє тіло запиту.
 * @returns {{ok: true, record: object} | {ok: false, error: string}}
 */
function validate(body) {
  // Тіло має бути саме об'єктом (масив і null теж мають тип 'object')
  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    return { ok: false, error: 'Request body must be a JSON object.' };
  }

  const required = ['name', 'email', 'subject', 'message'];

  for (const field of required) {
    if (typeof body[field] !== 'string') {
      return { ok: false, error: `Field "${field}" must be a string.` };
    }
    if (body[field].trim() === '') {
      return { ok: false, error: `Field "${field}" is required.` };
    }
    if (body[field].trim().length > LIMITS[field]) {
      return { ok: false, error: `Field "${field}" is too long (max ${LIMITS[field]}).` };
    }
  }

  if (!EMAIL_RE.test(body.email.trim())) {
    return { ok: false, error: 'A valid email address is required.' };
  }

  // --- додаткове поле варіанта: phone ---
  let phone = '';

  if (body.phone !== undefined && body.phone !== null && body.phone !== '') {
    if (typeof body.phone !== 'string') {
      return { ok: false, error: 'Field "phone" must be a string.' };
    }

    phone = body.phone.trim();

    if (phone.length > LIMITS.phone) {
      return { ok: false, error: `Field "phone" is too long (max ${LIMITS.phone}).` };
    }
    if (!PHONE_RE.test(phone)) {
      return {
        ok: false,
        error: 'Field "phone" may contain only +, digits, spaces, parentheses and hyphens.',
      };
    }
  }

  // id та createdAt створює СЕРВЕР — значенням від браузера довіряти не можна
  const record = {
    id: randomUUID(),
    createdAt: new Date().toISOString(),
    name: body.name.trim(),
    email: body.email.trim(),
    subject: body.subject.trim(),
    message: body.message.trim(),
    phone,
  };

  return { ok: true, record };
}

/* ---------- Запис у файл --------------------------------------------------
   JSON Lines: один рядок = один завершений JSON-об'єкт.
   appendFile дописує рядок у кінець, не читаючи й не перезаписуючи файл.
   ------------------------------------------------------------------------ */
async function saveRecord(record) {
  await mkdir(DATA_DIR, { recursive: true });
  await appendFile(DATA_FILE, JSON.stringify(record) + '\n', 'utf8');
}

/* ---------- Застосунок ----------------------------------------------------- */
const app = new Koa();
const router = new Router();

// 1) Обробник помилок — найперший у ланцюжку middleware.
//    Браузеру віддається загальне повідомлення, технічні деталі лишаються в логах.
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (error) {
    console.error('[server error]', error);
    ctx.status = error.status && error.status < 500 ? error.status : 500;
    ctx.body = {
      ok: false,
      error: ctx.status === 500 ? 'Internal server error.' : 'Invalid request.',
    };
  }
});

// 2) Розбір JSON-тіла з обмеженням розміру
app.use(bodyParser({
  jsonLimit: MAX_BODY,
  textLimit: MAX_BODY,
  formLimit: MAX_BODY,
  enableTypes: ['json'],
}));

// 3) Маршрут API
router.post('/api/contact', async (ctx) => {
  const result = validate(ctx.request.body);

  if (!result.ok) {
    ctx.status = 400;                       // Bad Request
    ctx.body = { ok: false, error: result.error };
    return;
  }

  await saveRecord(result.record);

  ctx.status = 201;                         // Created
  ctx.body = {
    ok: true,
    message: 'Feedback saved locally.',
    id: result.record.id,
  };
});

app.use(router.routes());
app.use(router.allowedMethods());

// 4) Роздача статичного сайту засобами фреймворка.
//    Власну обробку шляхів не пишемо: помилка в ній дозволила б вийти за межі public/.
app.use(serve(PUBLIC_DIR));

app.listen(PORT, HOST, () => {
  console.log(`Сервер працює:  http://localhost:${PORT}`);
  console.log(`Локальна мережа: http://<IP-комп'ютера>:${PORT}`);
  console.log(`Звернення пишуться у: ${DATA_FILE}`);
});
