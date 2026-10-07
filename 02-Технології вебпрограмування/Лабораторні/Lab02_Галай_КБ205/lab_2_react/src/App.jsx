import Header from './components/Header';
import Profile from './components/Profile';
import Experience from './components/Experience';
import Education from './components/Education';
import Skills from './components/Skills';
import Languages from './components/Languages';
import Projects from './components/Projects';
import Footer from './components/Footer';
import { cv } from './data/cv';

// App — кореневий компонент. Він не містить розмітки резюме,
// а лише збирає дочірні компоненти і передає їм дані через props.
function App() {
  return (
    <div>
      <Header name={cv.name} role={cv.role} contacts={cv.contacts} />
      <main>
        <Profile paragraphs={cv.profile} />
        <Experience jobs={cv.experience} />
        <Education items={cv.education} />
        <Skills groups={cv.skills} />
        <Languages items={cv.languages} />
        <Projects items={cv.projects} />
      </main>
      <Footer contacts={cv.contacts} />
    </div>
  );
}

export default App;
