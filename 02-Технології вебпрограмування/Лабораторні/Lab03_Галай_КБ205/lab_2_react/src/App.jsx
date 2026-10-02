import Header from './components/Header';
import Profile from './components/Profile';
import Experience from './components/Experience';
import Education from './components/Education';
import Skills from './components/Skills';
import Languages from './components/Languages';
import Projects from './components/Projects';
import Footer from './components/Footer';
import { cv } from './data/cv';

function App() {
  return (
    <div className="min-h-screen bg-slate-100 font-display text-ink">
      <div className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6">
        <Header name={cv.name} role={cv.role} contacts={cv.contacts} />

        {/* Адаптивна сітка: одна колонка на мобільному, дві — від lg */}
        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <main className="flex flex-col gap-6">
            <Profile paragraphs={cv.profile} />
            <Experience jobs={cv.experience} />
            <Education items={cv.education} />
            <Projects items={cv.projects} />
          </main>

          <aside className="flex flex-col gap-6">
            <Skills groups={cv.skills} />
            <Languages items={cv.languages} />
          </aside>
        </div>

        <Footer contacts={cv.contacts} />
      </div>
    </div>
  );
}

export default App;
