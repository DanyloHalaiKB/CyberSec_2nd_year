import Header from './components/Header';
import Profile from './components/Profile';
import Experience from './components/Experience';
import Education from './components/Education';
import Skills from './components/Skills';
import Languages from './components/Languages';
import Projects from './components/Projects';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-slate-100 px-3 py-6 font-sans text-slate-800 sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-slate-200">
        <Header />
        <main className="space-y-10 p-6 sm:p-10">
          <Profile />
          <Experience />
          <Education />
          <Skills />
          <Languages />
          <Projects />
        </main>
        <Footer />
      </div>
    </div>
  );
}

export default App;
