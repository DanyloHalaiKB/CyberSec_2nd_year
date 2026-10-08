function Skills() {
  return (
    <section id="skills" className="scroll-mt-6">
      <h2 className="mb-4 border-b-2 border-amber-200 pb-2 text-2xl font-bold text-amber-900">Навички</h2>

      <div className="grid gap-4 md:grid-cols-3">
        <section className="rounded-xl border border-t-4 border-slate-200 border-t-amber-600 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
          <h3 className="mb-3 text-base font-semibold uppercase tracking-wide text-amber-800">Комп'ютерні та ІТ-навички</h3>
          <ul className="list-disc space-y-1.5 pl-5 text-sm marker:text-amber-600">
            <li>C#, Python, C++, SQL</li>
            <li>Бекенд-розробка, написання макросів і скриптів</li>
            <li>Об'єктно-орієнтоване програмування (ООП)</li>
            <li>Інтеграція ШІ у робочі процеси</li>
            <li>Дискретна та вища математика</li>
          </ul>
        </section>

        <section className="rounded-xl border border-t-4 border-slate-200 border-t-orange-500 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
          <h3 className="mb-3 text-base font-semibold uppercase tracking-wide text-orange-800">Креативні навички</h3>
          <ul className="list-disc space-y-1.5 pl-5 text-sm marker:text-orange-500">
            <li>Adobe Lightroom Classic</li>
            <li>Adobe Photoshop</li>
            <li>CapCut</li>
            <li>DaVinci Resolve</li>
          </ul>
        </section>

        <section className="rounded-xl border border-t-4 border-slate-200 border-t-yellow-500 bg-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
          <h3 className="mb-3 text-base font-semibold uppercase tracking-wide text-yellow-800">Технічні дослідження</h3>
          <ul className="list-disc space-y-1.5 pl-5 text-sm marker:text-yellow-500">
            <li>Автоматизація систем</li>
            <li>Фінансові технології (основи криптоарбітражу)</li>
            <li>Діагностика апаратного забезпечення</li>
            <li>Складні специфікації автомобільної інженерії (європейські платформи)</li>
          </ul>
        </section>
      </div>
    </section>
  );
}

export default Skills;
