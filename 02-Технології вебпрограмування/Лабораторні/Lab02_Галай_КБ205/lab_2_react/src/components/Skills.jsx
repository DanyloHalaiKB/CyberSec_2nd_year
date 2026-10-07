function Skills({ groups }) {
  return (
    <section>
      <h2>Навички</h2>
      {groups.map((group) => (
        <section key={group.id}>
          <h3>{group.group}</h3>
          <ul>
            {group.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ))}
    </section>
  );
}

export default Skills;
