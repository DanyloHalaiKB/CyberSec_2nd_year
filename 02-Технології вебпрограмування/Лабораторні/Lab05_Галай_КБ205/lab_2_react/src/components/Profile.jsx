function Profile({ paragraphs }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-700">
      <h2 className="mb-4 border-b border-slate-200 pb-2 text-xl font-semibold text-brand dark:border-slate-700">
        Профіль
      </h2>
      {paragraphs.map((text, i) => (
        <p key={i} className="mb-3 text-slate-700 last:mb-0 dark:text-slate-300">
          {text}
        </p>
      ))}
    </section>
  );
}

export default Profile;
