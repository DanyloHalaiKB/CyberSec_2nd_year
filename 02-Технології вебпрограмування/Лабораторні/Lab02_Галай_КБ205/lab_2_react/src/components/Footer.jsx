function Footer({ contacts }) {
  const year = new Date().getFullYear();

  return (
    <footer>
      <h2>Контакти</h2>
      <p>
        <a href={`mailto:${contacts.email}`}>{contacts.email}</a>
        {' · '}
        <a href={`tel:${contacts.phoneHref}`}>{contacts.phone}</a>
      </p>
      <p><small>&copy; {year} Danylo Halai. Лабораторна робота №2.</small></p>
    </footer>
  );
}

export default Footer;
