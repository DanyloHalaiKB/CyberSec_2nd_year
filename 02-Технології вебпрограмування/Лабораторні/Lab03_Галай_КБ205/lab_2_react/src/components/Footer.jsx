function Footer({ contacts }) {
  const year = new Date().getFullYear();

  return (
    <footer className="rounded-2xl bg-ink px-6 py-6 text-slate-300">
      <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
        <a href={`mailto:${contacts.email}`} className="transition hover:text-white">
          {contacts.email}
        </a>
        <a href={`tel:${contacts.phoneHref}`} className="transition hover:text-white">
          {contacts.phone}
        </a>
      </div>
      <p className="mt-3 text-xs text-slate-500">
        © {year} Danylo Halai · Лабораторна робота №3
      </p>
    </footer>
  );
}

export default Footer;
