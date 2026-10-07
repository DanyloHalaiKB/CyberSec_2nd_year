function Education({ items }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-700">
      <h2 className="mb-4 border-b border-slate-200 pb-2 text-xl font-semibold text-brand dark:border-slate-700">
        Освіта
      </h2>

      {items.map((item) => (
        <article key={item.id} className="border-l-2 border-brand-soft pl-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="font-semibold text-ink">{item.degree}</h3>
            <p className="text-sm text-slate-500">
              {item.period} · {item.location}
            </p>
          </div>
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-1 inline-block text-brand underline underline-offset-4 hover:text-brand/70"
          >
            {item.school} ↗
          </a>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-slate-700 marker:text-brand dark:text-slate-300">
            {item.points.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </article>
      ))}
    </section>
  );
}

export default Education;
