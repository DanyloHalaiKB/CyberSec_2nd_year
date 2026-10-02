function Experience({ jobs }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-700">
      <h2 className="mb-4 border-b border-slate-200 pb-2 text-xl font-semibold text-brand dark:border-slate-700">
        Досвід роботи
      </h2>

      <div className="flex flex-col gap-5">
        {jobs.map((job) => (
          <article
            key={job.id}
            className="border-l-2 border-brand-soft pl-4 transition hover:border-brand"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="font-semibold text-ink">{job.title}</h3>
              <p className="text-sm text-slate-500">
                {job.period} · {job.location}
              </p>
            </div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-slate-700 marker:text-brand dark:text-slate-300">
              {job.points.map((point, i) => (
                <li key={i}>{point}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Experience;
