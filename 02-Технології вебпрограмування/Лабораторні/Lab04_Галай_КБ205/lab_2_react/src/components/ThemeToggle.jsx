// Кнопка ручного перемикання теми. Стан приходить із App через props,
// а зміна передається вгору через функцію зворотного виклику onToggle —
// це стандартний спосіб передачі даних "знизу вгору" в React.
function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={isDark}
      className="inline-flex items-center gap-2 rounded-full border border-white/30 px-3 py-1 text-sm text-white transition hover:bg-white/15"
    >
      <span>{isDark ? '☀' : '🌙'}</span>
      <span>{isDark ? 'Денна тема' : 'Нічна тема'}</span>
    </button>
  );
}

export default ThemeToggle;
