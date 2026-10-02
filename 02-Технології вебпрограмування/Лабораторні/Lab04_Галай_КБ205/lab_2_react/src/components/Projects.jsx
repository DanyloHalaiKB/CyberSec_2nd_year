function Projects({ items }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-700">
      <h2 className="mb-4 border-b border-slate-200 pb-2 text-xl font-semibold text-brand dark:border-slate-700">
        Самостійні проєкти
      </h2>

      <div className="grid gap-5 md:grid-cols-2">
        {items.map((project) => (
          <article
            key={project.id}
            className="rounded-xl border border-slate-200 p-4 transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700"
          >
            <h3 className="font-semibold text-ink">{project.title}</h3>
            <p className="text-sm text-slate-500">{project.period}</p>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700 marker:text-brand dark:text-slate-300">
              {project.points.map((point, i) => (
                <li key={i}>{point}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Projects;
