function Languages() {
  return (
    <section id="languages" className="scroll-mt-6">
      <h2 className="mb-4 border-b-2 border-violet-200 pb-2 text-2xl font-bold text-violet-900">Мови</h2>
      <ul className="flex flex-wrap gap-3">
        <li className="rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm transition hover:scale-105 hover:border-violet-400">Українська — рідна</li>
        <li className="rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm transition hover:scale-105 hover:border-violet-400">Англійська — B2–C1</li>
        <li className="rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm transition hover:scale-105 hover:border-violet-400">Німецька — A1</li>
      </ul>
    </section>
  );
}

export default Languages;
