function Experience() {
  return (
    <section id="experience" className="scroll-mt-6">
      <h2 className="mb-4 border-b-2 border-violet-200 pb-2 text-2xl font-bold text-violet-900">Досвід роботи</h2>

      <article className="mb-4 rounded-xl border border-l-4 border-slate-200 border-l-violet-600 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
        <h3 className="text-lg font-semibold text-slate-900">Менеджер — продаж автомобілів та контент-менеджмент</h3>
        <p className="mt-1 text-sm text-slate-500"><time dateTime="2023">2023</time> – дотепер, Львів, Україна</p>
        <ul className="mt-3 list-disc space-y-1.5 pl-5 marker:text-violet-600">
          <li>Ведення повного циклу продажу автомобілів на майданчику із застосуванням
              глибоких знань автомобільної інженерії та європейських платформ.</li>
          <li>Керування створенням контенту та стратегіями цифрового маркетингу:
              виробництво мультимедійного контенту для показу автопарку й підвищення
              залученості покупців.</li>
        </ul>
      </article>

      <article className="mb-4 rounded-xl border border-l-4 border-slate-200 border-l-violet-600 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
        <h3 className="text-lg font-semibold text-slate-900">Фотограф та спеціаліст із цифрових медіа</h3>
        <p className="mt-1 text-sm text-slate-500"><time dateTime="2022-10">Жовтень 2022</time> – дотепер, Львів, Україна</p>
        <ul className="mt-3 list-disc space-y-1.5 pl-5 marker:text-violet-600">
          <li>Професійні фотопослуги на фрилансі понад 3,5 роки: корпоративна та
              lifestyle-зйомка для десятків клієнтів.</li>
          <li>Зйомка у високій роздільності на професійних бездзеркальних системах
              Lumix DC-G97H та Sony A7 II.</li>
          <li>Постобробка, кольорокорекція та оптимізація експорту в DaVinci Resolve.</li>
        </ul>
      </article>
    </section>
  );
}

export default Experience;
