import { useEffect, useState } from 'react';

// Номер варіанта = номер поста в JSONPlaceholder
const VARIANT = 7;
const API_URL = `https://jsonplaceholder.typicode.com/posts/${VARIANT}/comments`;

function Reviews() {
  // useState зберігає дані МІЖ рендерами. Звичайна змінна обнулилася б
  // при кожному перемальовуванні компонента, і список зник би.
  const [comments, setComments] = useState([]);
  const [status, setStatus] = useState('loading'); // loading | ready | error
  const [error, setError] = useState('');

  // Порожній масив залежностей => ефект виконається РІВНО ОДИН раз при монтуванні.
  useEffect(() => {
    // ignore захищає від оновлення стану вже демонтованого компонента
    let ignore = false;

    async function fetchComments() {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        if (ignore) return;

        setComments(data);      // порядок отримання зберігаємо, не сортуємо
        setStatus('ready');
      } catch (err) {
        if (ignore) return;
        setError(err.message);
        setStatus('error');
      }
    }

    fetchComments();

    return () => {
      ignore = true;            // функція очищення
    };
  }, []);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <h2 className="mb-2 border-b border-slate-200 pb-2 text-xl font-semibold text-brand dark:border-slate-700">
        Відгуки попередніх роботодавців
      </h2>
      <p className="mb-4 text-sm text-slate-500">
        Джерело: <code className="rounded bg-brand-soft px-1 dark:bg-slate-800">posts/{VARIANT}/comments</code>
      </p>

      {/* Умовний рендеринг через оператор && та тернарний оператор */}
      {status === 'loading' && (
        <p className="text-slate-500">Завантаження відгуків…</p>
      )}

      {status === 'error' && (
        <p className="text-red-600">Не вдалося завантажити відгуки: {error}</p>
      )}

      {status === 'ready' && (
        <div className="grid gap-4 md:grid-cols-2">
          {comments.map((comment, index) => (
            <article
              key={comment.id}
              className="rounded-xl border border-slate-200 p-4 transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700"
            >
              <h3 className="text-sm font-semibold text-brand">
                {index + 1}. {comment.name}
              </h3>
              <a
                href={`mailto:${comment.email}`}
                className="text-xs text-slate-500 underline-offset-2 hover:underline"
              >
                {comment.email}
              </a>
              <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">
                {comment.body}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default Reviews;
