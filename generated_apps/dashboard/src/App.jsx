import { useState } from 'react';
import './index.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="App">
      <header>
        <h1>Dashboard</h1>
        <ul className="nav">
          <li key="home">Home</li> <li key="about">About</li>
        </ul>
      </header>
      <main>
        <h2>Welcome</h2>
        <p>This React app was generated from the brain's learned reactjs knowledge.</p>
        <p>Features: auth, charts</p>
        <button onClick={() => setCount((c) => c + 1)}>Count: {{count}}</button>
      </main>
    </div>
  );
}

export default App;
