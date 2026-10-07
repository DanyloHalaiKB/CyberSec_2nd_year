function Languages({ items }) {
  return (
    <section>
      <h2>Мови</h2>
      <ul>
        {items.map((lang) => (
          <li key={lang.id}>{lang.name} — {lang.level}</li>
        ))}
      </ul>
    </section>
  );
}

export default Languages;
