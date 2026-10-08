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
    <div>
      <Header />
      <main>
        <Profile />
        <Experience />
        <Education />
        <Skills />
        <Languages />
        <Projects />
      </main>
      <Footer />
    </div>
  );
}

export default App;
