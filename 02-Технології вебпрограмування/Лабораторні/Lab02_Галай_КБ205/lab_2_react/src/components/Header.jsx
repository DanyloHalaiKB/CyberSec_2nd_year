// Компонент шапки. Дані приходять через props: name, role, contacts.
function Header({ name, role, contacts }) {
  return (
    <header>
      <h1>{name}</h1>
      <p>{role}</p>
      <address>
        <ul>
          <li>Email: <a href={`mailto:${contacts.email}`}>{contacts.email}</a></li>
          <li>Телефон: <a href={`tel:${contacts.phoneHref}`}>{contacts.phone}</a></li>
          <li>Місто: {contacts.city}</li>
          <li>Водійські права: {contacts.license}</li>
        </ul>
      </address>
    </header>
  );
}

export default Header;
