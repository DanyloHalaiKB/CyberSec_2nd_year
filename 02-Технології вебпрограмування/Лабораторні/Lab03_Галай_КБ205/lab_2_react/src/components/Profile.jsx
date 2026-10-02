function Profile({ paragraphs }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 border-b border-slate-200 pb-2 text-xl font-semibold text-brand">
        Профіль
      </h2>
      {paragraphs.map((text, i) => (
        <p key={i} className="mb-3 text-slate-700 last:mb-0">
          {text}
        </p>
      ))}
    </section>
  );
}

export default Profile;
