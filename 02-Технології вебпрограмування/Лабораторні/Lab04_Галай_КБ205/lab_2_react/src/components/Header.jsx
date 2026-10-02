function Header({ name, role, contacts }) {
  return (
    <header className="bg-brand text-white px-6 py-8 rounded-2xl shadow-lg sm:px-10">
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{name}</h1>
      <p className="mt-2 max-w-2xl text-brand-soft sm:text-lg">{role}</p>

      <address className="mt-5 flex flex-wrap gap-x-6 gap-y-2 text-sm not-italic">
        <a
          href={`mailto:${contacts.email}`}
          className="underline decoration-white/40 underline-offset-4 transition hover:decoration-white"
        >
          ✉ {contacts.email}
        </a>
        <a
          href={`tel:${contacts.phoneHref}`}
          className="underline decoration-white/40 underline-offset-4 transition hover:decoration-white"
        >
          ☎ {contacts.phone}
        </a>
        <span>📍 {contacts.city}</span>
        <span>🚗 {contacts.license}</span>
      </address>
    </header>
  );
}

export default Header;
