function Languages({ items }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-brand">
        Мови
      </h2>
      <ul className="divide-y divide-slate-100">
        {items.map((lang) => (
          <li key={lang.id} className="flex justify-between py-1.5 text-sm">
            <span className="text-ink">{lang.name}</span>
            <span className="text-slate-500">{lang.level}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default Languages;
