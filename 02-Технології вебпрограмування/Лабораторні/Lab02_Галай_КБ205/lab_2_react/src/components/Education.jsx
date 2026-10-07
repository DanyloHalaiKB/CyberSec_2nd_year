function Education({ items }) {
  return (
    <section>
      <h2>Освіта</h2>
      {items.map((item) => (
        <article key={item.id}>
          <h3>{item.degree}</h3>
          <p>
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              {item.school}
            </a>
          </p>
          <p>{item.period} · {item.location}</p>
          <ul>
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
