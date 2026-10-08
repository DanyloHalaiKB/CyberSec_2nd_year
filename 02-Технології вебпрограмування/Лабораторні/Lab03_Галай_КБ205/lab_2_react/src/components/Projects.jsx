function Projects() {
  return (
    <section id="projects" className="scroll-mt-6">
      <h2 className="mb-4 border-b-2 border-violet-200 pb-2 text-2xl font-bold text-violet-900">Самостійні технічні та програмні проєкти</h2>

      <article className="mb-4 rounded-xl border border-l-4 border-slate-200 border-l-violet-600 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
        <h3 className="text-lg font-semibold text-slate-900">Розробка ПЗ — самостійні технічні дослідження</h3>
        <p className="mt-1 text-sm text-slate-500"><time dateTime="2026-01">Січень 2026</time> – дотепер</p>
        <ul className="mt-3 list-disc space-y-1.5 pl-5 marker:text-violet-600">
          <li>Розробка та оптимізація бекенд-логіки для складних застосунків на C#.</li>
          <li>Проєктування автоматизованих фінансових процесів: технічні вимоги для
              P2P-криптоарбітражу та розрахунку спреду через Telegram-ботів.</li>
          <li>Аналіз і структурування SQL-баз даних із фокусом на безпеці даних.</li>
        </ul>
      </article>

      <article className="rounded-xl border border-l-4 border-slate-200 border-l-violet-600 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
        <h3 className="text-lg font-semibold text-slate-900">Адміністрування проєкту — інфраструктурна пропозиція для кампусу</h3>
        <p className="mt-1 text-sm text-slate-500"><time dateTime="2026-02">Лютий 2026</time></p>
        <ul className="mt-3 list-disc space-y-1.5 pl-5 marker:text-violet-600">
          <li>Опрацювання муніципальних та академічних адміністративних процедур для
              підготовки пропозиції щодо комерційної інфраструктури на території кампусу.</li>
          <li>Практичний досвід роботи з системою закупівель Prozorro: правові та
              процедурні вимоги для локального бізнесу.</li>
        </ul>
      </article>
    </section>
  );
}

export default Projects;
