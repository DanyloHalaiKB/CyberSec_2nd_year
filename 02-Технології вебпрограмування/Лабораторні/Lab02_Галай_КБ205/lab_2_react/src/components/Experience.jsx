function Experience({ jobs }) {
  return (
    <section>
      <h2>Досвід роботи</h2>
      {jobs.map((job) => (
        <article key={job.id}>
          <h3>{job.title}</h3>
          <p>{job.period} · {job.location}</p>
          <ul>
            {job.points.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </article>
      ))}
    </section>
  );
}

export default Experience;
