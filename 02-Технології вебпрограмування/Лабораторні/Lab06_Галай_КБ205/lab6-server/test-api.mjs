/* Автоматична перевірка сервера: запускає server.js, шле запити, друкує результат.
   Запуск:  node test-api.mjs   */
import { spawn } from 'node:child_process';
import { readFile, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_FILE = path.join(__dirname, 'data', 'feedback.jsonl');
const BASE = 'http://127.0.0.1:3000';

await rm(DATA_FILE, { force: true });

const srv = spawn(process.execPath, ['server.js'], { cwd: __dirname, stdio: 'inherit' });

// Чекаємо, поки сервер почне приймати з'єднання (до 20 с)
async function waitForServer() {
  for (let i = 0; i < 100; i++) {
    try {
      await fetch(BASE + '/', { signal: AbortSignal.timeout(500) });
      return;
    } catch {
      await new Promise((r) => setTimeout(r, 200));
    }
  }
  throw new Error('Сервер не піднявся за 20 секунд');
}

await waitForServer();

let passed = 0, failed = 0;

async function check(title, expected, run) {
  const status = await run();
  const ok = status === expected;
  ok ? passed++ : failed++;
  console.log(`${ok ? '  OK  ' : ' FAIL '} ${title}: очікувалось ${expected}, отримано ${status}`);
}

const get = (p) => fetch(BASE + p).then((r) => r.status);
const post = (body) =>
  fetch(BASE + '/api/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then((r) => r.status);

const valid = {
  name: 'Test User', email: 'test@example.com',
  subject: 'Lab 6', message: 'Local persistence test',
  phone: '+380 (68) 000-00-00',
};

console.log('\n--- Роздача статичних файлів ---');
await check('GET /', 200, () => get('/'));
await check('GET /styles.css', 200, () => get('/styles.css'));
await check('GET /script.js', 200, () => get('/script.js'));

console.log('\n--- POST /api/contact ---');
await check('коректні дані з phone', 201, () => post(valid));
await check('коректні дані без phone', 201, () => post({ ...valid, phone: undefined }));
await check('некоректний email', 400, () => post({ ...valid, email: 'not-an-email' }));
await check('порожнє name після trim', 400, () => post({ ...valid, name: '   ' }));
await check('відсутнє поле subject', 400, () => post({ ...valid, subject: undefined }));
await check('name довше за 60 символів', 400, () => post({ ...valid, name: 'a'.repeat(70) }));
await check('phone із літерами', 400, () => post({ ...valid, phone: 'abc123' }));
await check('phone довший за 30 символів', 400, () => post({ ...valid, phone: '+'.repeat(40) }));
await check('тіло не є об’єктом', 400, () => post(['array']));

console.log('\n--- Приватність даних ---');
await check('GET /data/feedback.jsonl', 404, () => get('/data/feedback.jsonl'));

const lines = (await readFile(DATA_FILE, 'utf8')).trim().split('\n');
console.log(`\nУ data/feedback.jsonl рядків: ${lines.length} (очікувалось 2 — лише успішні запити)`);
console.log(lines.map((l, i) => `  ${i + 1}. ${l}`).join('\n'));

console.log(`\nПідсумок: ${passed} пройдено, ${failed} провалено`);
srv.kill();
process.exit(failed ? 1 : 0);
