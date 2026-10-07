import { useEffect, useState } from 'react';

const MODAL_DELAY_MS = 60_000; // 1 хвилина

// УВАГА: перед здачею замінити на реальний ендпойнт із formspree.io
const FORMSPREE_ENDPOINT = 'https://formspree.io/f/ВАШ_ЕНДПОЙНТ';

function ContactForm() {
  const [isOpen, setIsOpen] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // Таймер відкриття. Ефект виконується один раз; у функції очищення
  // обов'язково знімаємо таймер, інакше після демонтування компонента
  // React спробує оновити стан неіснуючого компонента.
  useEffect(() => {
    const timerId = setTimeout(() => setIsOpen(true), MODAL_DELAY_MS);
    return () => clearTimeout(timerId);
  }, []);

  // Закриття клавішею Escape
  useEffect(() => {
    if (!isOpen) return;

    const onKeyDown = (event) => {
      if (event.key === 'Escape') close();
    };

    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [isOpen]);

  function close() {
    setIsOpen(false);
    // dismissed не дає таймеру відкрити вікно повторно в цій сесії
    setDismissed(true);
  }

  // Умовний рендеринг: якщо isOpen хибне — не рендериться нічого
  if (!isOpen || dismissed) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center p-4">
      <div
        className="absolute inset-0 bg-black/60"
        onClick={close}
        aria-hidden="true"
      />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="contact-title"
        className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900"
      >
        <button
          type="button"
          onClick={close}
          aria-label="Закрити"
          className="absolute right-3 top-3 h-8 w-8 rounded-full text-xl leading-none text-slate-400 transition hover:bg-brand-soft hover:text-brand dark:hover:bg-slate-800"
        >
          &times;
        </button>

        <h2 id="contact-title" className="text-xl font-semibold text-brand">
          Зворотний зв'язок
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Маєте питання чи пропозицію щодо співпраці? Напишіть мені.
        </p>

        <form action={FORMSPREE_ENDPOINT} method="POST" className="mt-4 flex flex-col gap-3">
          <Field id="name" label="Ім'я *" type="text" required placeholder="Данило" />
          <Field id="email" label="Email *" type="email" required placeholder="you@example.com" />
          <Field id="phone" label="Номер телефону" type="tel" placeholder="+380 (68) 000-00-00" />

          <div>
            <label htmlFor="message" className="mb-1 block text-sm font-semibold">
              Повідомлення *
            </label>
            <textarea
              id="message"
              name="message"
              rows={4}
              required
              maxLength={1000}
              placeholder="Ваше повідомлення…"
              className="w-full resize-y rounded-md border border-slate-300 p-2 text-sm focus:border-brand focus:outline-2 focus:outline-brand dark:border-slate-600 dark:bg-slate-800"
            />
          </div>

          <button
            type="submit"
            className="rounded-md bg-brand px-4 py-2 font-semibold text-white transition hover:bg-brand/85"
          >
            Надіслати
          </button>
        </form>
      </div>
    </div>
  );
}

// Дрібний допоміжний компонент, щоб не дублювати розмітку полів
function Field({ id, label, type, required = false, placeholder }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-semibold">
        {label}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        required={required}
        placeholder={placeholder}
        maxLength={120}
        className="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-brand focus:outline-2 focus:outline-brand dark:border-slate-600 dark:bg-slate-800"
      />
    </div>
  );
}

export default ContactForm;
