function Education() {
  return (
    <section id="education" className="scroll-mt-6">
      <h2 className="mb-4 border-b-2 border-amber-200 pb-2 text-2xl font-bold text-amber-900">Освіта</h2>
      <article className="rounded-xl border border-l-4 border-slate-200 border-l-amber-600 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
        <h3 className="text-lg font-semibold text-slate-900">Бакалавр, «Кібербезпека та програмування»</h3>
        <p className="mt-1">
          <a className="font-medium text-amber-700 underline-offset-4 hover:underline" href="https://lpnu.ua" target="_blank" rel="noopener noreferrer">
            Національний університет «Львівська політехніка»
          </a>
        </p>
        <p className="text-sm text-slate-500"><time dateTime="2025">2025</time> – дотепер, Львів, Україна</p>
        <ul className="mt-3 list-disc space-y-1.5 pl-5 marker:text-amber-600">
          <li>Основні дисципліни: дискретна математика, об'єктно-орієнтоване програмування,
              інформаційна безпека, вища математика.</li>
          <li>Академічний фокус: практичне застосування абстракції та успадкування в C#,
              оптимізація коду, розробка алгоритмів.</li>
        </ul>
      </article>
    </section>
  );
}

export default Education;
