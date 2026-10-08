function Header() {
  return (
    <header id="top">
      <h1>Danylo Halai</h1>
      <p>Студент спеціальності «Кібербезпека та програмування», контент-мейкер і менеджер</p>

      <address>
        <ul>
          <li>Email: <a href="mailto:danylo.galai@gmail.com">danylo.galai@gmail.com</a></li>
          <li>Телефон: <a href="tel:+380686812966">+380 (68) 681-29-66</a></li>
          <li>Місто: Львів, Україна</li>
          <li>Водійські права: категорія B</li>
        </ul>
      </address>

      <nav>
        <h2>Навігація</h2>
        <ul>
          <li><a href="#profile">Профіль</a></li>
          <li><a href="#experience">Досвід роботи</a></li>
          <li><a href="#education">Освіта</a></li>
          <li><a href="#skills">Навички</a></li>
          <li><a href="#languages">Мови</a></li>
          <li><a href="#projects">Проєкти</a></li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;
