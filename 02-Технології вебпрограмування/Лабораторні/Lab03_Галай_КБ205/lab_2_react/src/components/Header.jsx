function Header() {
  return (
    <header id="top" className="bg-linear-to-br from-amber-900 via-amber-800 to-orange-700 p-6 text-white sm:p-10">
      <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">Danylo Halai</h1>
      <p className="mt-3 max-w-2xl text-lg text-amber-100">Студент спеціальності «Кібербезпека та програмування», контент-мейкер і менеджер</p>

      <address className="mt-6 not-italic">
        <ul className="grid gap-x-8 gap-y-1 text-sm text-amber-50 sm:grid-cols-2">
          <li>Email: <a className="font-medium underline-offset-4 hover:underline" href="mailto:danylo.galai@gmail.com">danylo.galai@gmail.com</a></li>
          <li>Телефон: <a className="font-medium underline-offset-4 hover:underline" href="tel:+380686812966">+380 (68) 681-29-66</a></li>
          <li>Місто: Львів, Україна</li>
          <li>Водійські права: категорія B</li>
        </ul>
      </address>

      <nav className="mt-6">
        <h2 className="sr-only">Навігація</h2>
        <ul className="flex flex-wrap gap-2">
          <li><a className="block rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-white hover:text-amber-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" href="#profile">Профіль</a></li>
          <li><a className="block rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-white hover:text-amber-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" href="#experience">Досвід роботи</a></li>
          <li><a className="block rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-white hover:text-amber-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" href="#education">Освіта</a></li>
          <li><a className="block rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-white hover:text-amber-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" href="#skills">Навички</a></li>
          <li><a className="block rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-white hover:text-amber-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" href="#languages">Мови</a></li>
          <li><a className="block rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-white hover:text-amber-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" href="#projects">Проєкти</a></li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;
