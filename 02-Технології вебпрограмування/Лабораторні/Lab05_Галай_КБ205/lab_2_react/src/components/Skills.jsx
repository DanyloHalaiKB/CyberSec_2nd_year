function Skills({ groups }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-brand-soft p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-widest text-brand">
        Навички
      </h2>

      <div className="flex flex-col gap-4">
        {groups.map((group) => (
          <div key={group.id}>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              {group.group}
            </h3>
            <ul className="flex flex-wrap gap-2">
              {group.items.map((item) => (
                <li
                  key={item}
                  className="rounded-md border border-slate-300 bg-white px-2 py-0.5 text-xs transition hover:border-brand hover:bg-brand hover:text-white dark:bg-slate-900 dark:border-slate-600"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Skills;
