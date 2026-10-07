import { useEffect, useState } from 'react';

const STORAGE_KEY = 'systemInfo';

function Footer({ contacts }) {
  const [info, setInfo] = useState({});

  // useEffect із порожнім масивом залежностей = componentDidMount:
  // код виконується ОДИН раз після монтування компонента, коли
  // об'єкти navigator і screen вже точно доступні.
  useEffect(() => {
    const data = {
      'User Agent': navigator.userAgent,
      'Платформа': navigator.platform,
      'Мова': navigator.language,
      'Ядер процесора': navigator.hardwareConcurrency ?? 'невідомо',
      'Онлайн': navigator.onLine ? 'так' : 'ні',
      'Екран': `${screen.width}×${screen.height}`,
      'Часовий пояс': Intl.DateTimeFormat().resolvedOptions().timeZone,
      'Збережено': new Date().toLocaleString('uk-UA'),
    };

    // localStorage зберігає лише рядки → серіалізуємо об'єкт
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));

    // і одразу читаємо назад — щоб у JSX потрапили саме збережені дані
    setInfo(JSON.parse(localStorage.getItem(STORAGE_KEY)));
  }, []);

  const year = new Date().getFullYear();

  return (
    <footer className="rounded-2xl bg-ink px-6 py-6 text-slate-300">
      <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
        <a href={`mailto:${contacts.email}`} className="transition hover:text-white">
          {contacts.email}
        </a>
        <a href={`tel:${contacts.phoneHref}`} className="transition hover:text-white">
          {contacts.phone}
        </a>
      </div>

      <section className="mt-4 rounded-xl border border-dashed border-slate-600 p-4">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-slate-400">
          Системна інформація (з localStorage)
        </h2>
        <dl className="grid grid-cols-[minmax(110px,180px)_1fr] gap-x-4 gap-y-1 text-xs">
          {Object.entries(info).map(([key, value]) => (
            <div key={key} className="contents">
              <dt className="font-semibold text-slate-400">{key}</dt>
              <dd className="break-words text-slate-300">{String(value)}</dd>
            </div>
          ))}
        </dl>
      </section>

      <p className="mt-3 text-xs text-slate-500">
        © {year} Danylo Halai · Лабораторна робота №5
      </p>
    </footer>
  );
}

export default Footer;
