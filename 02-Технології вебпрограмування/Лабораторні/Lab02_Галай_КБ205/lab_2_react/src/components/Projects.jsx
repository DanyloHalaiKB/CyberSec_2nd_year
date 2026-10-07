function Projects({ items }) {
  return (
    <section>
      <h2>Самостійні технічні та програмні проєкти</h2>
      {items.map((project) => (
        <article key={project.id}>
          <h3>{project.title}</h3>
          <p>{project.period}</p>
          <ul>
            {project.points.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </article>
      ))}
    </section>
  );
}

export default Projects;
