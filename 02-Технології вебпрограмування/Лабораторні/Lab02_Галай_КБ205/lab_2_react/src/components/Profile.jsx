// Компонент профілю: масив абзаців перетворюється на <p> через .map().
function Profile({ paragraphs }) {
  return (
    <section>
      <h2>Профіль</h2>
      {paragraphs.map((text, i) => (
        <p key={i}>{text}</p>
      ))}
    </section>
  );
}

export default Profile;
