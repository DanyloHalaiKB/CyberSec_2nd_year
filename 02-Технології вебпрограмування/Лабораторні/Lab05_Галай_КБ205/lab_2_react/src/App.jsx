import { useEffect, useState } from 'react';
import Header from './components/Header';
import Profile from './components/Profile';
import Experience from './components/Experience';
import Education from './components/Education';
import Skills from './components/Skills';
import Languages from './components/Languages';
import Projects from './components/Projects';
import Reviews from './components/Reviews';
import ContactForm from './components/ContactForm';
import ThemeToggle from './components/ThemeToggle';
import Footer from './components/Footer';
import { cv } from './data/cv';

const DAY_START = 7;   // 07:00
const DAY_END = 21;    // 21:00

/** Денна тема з 07:00 до 21:00, нічна — в усі інші години. */
function themeByTime() {
  const hours = new Date().getHours();
  return hours >= DAY_START && hours < DAY_END ? 'light' : 'dark';
}

function App() {
  // Початкове значення обчислюється один раз (ліниво) під час першого рендеру
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || themeByTime());

  // Побічний ефект: синхронізуємо стан React із DOM і localStorage.
  // Залежність [theme] => ефект спрацьовує при КОЖНІЙ зміні теми.
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));

  return (
    <div className="min-h-screen bg-slate-100 font-display text-ink transition-colors dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6">

        <div className="relative">
          <Header name={cv.name} role={cv.role} contacts={cv.contacts} />
          <div className="absolute right-6 top-6">
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <main className="flex flex-col gap-6">
            <Profile paragraphs={cv.profile} />
            <Experience jobs={cv.experience} />
            <Education items={cv.education} />
            <Projects items={cv.projects} />
            <Reviews />
          </main>

          <aside className="flex flex-col gap-6">
            <Skills groups={cv.skills} />
            <Languages items={cv.languages} />
          </aside>
        </div>

        <Footer contacts={cv.contacts} />
      </div>

      {/* Модальне вікно рендериться поверх усього через fixed inset-0 */}
      <ContactForm />
    </div>
  );
}

export default App;
