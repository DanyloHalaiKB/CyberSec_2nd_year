function Footer() {
  return (
    <footer className="bg-slate-900 p-6 text-sm text-slate-300 sm:px-10">
      <h2 className="mb-2 text-base font-semibold text-white">Контакти</h2>
      <p>
        <a className="text-violet-300 underline-offset-4 hover:text-white hover:underline" href="mailto:danylo.galai@gmail.com">danylo.galai@gmail.com</a> ·{' '}
        <a className="text-violet-300 underline-offset-4 hover:text-white hover:underline" href="tel:+380686812966">+380 (68) 681-29-66</a>
      </p>
      <p className="mt-2"><small className="text-slate-400">&copy; 2026 Danylo Halai. Лабораторна робота №3, НУ «Львівська політехніка».</small></p>
      <p className="mt-2"><a className="font-medium text-violet-300 hover:text-white" href="#top">Нагору ↑</a></p>
    </footer>
  );
}

export default Footer;
