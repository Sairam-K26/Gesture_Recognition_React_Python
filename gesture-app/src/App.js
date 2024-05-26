import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [fingerCount, setFingerCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      axios.get('http://127.0.0.1:5000/finger_count')
        .then(response => {
          setFingerCount(response.data.finger_count);
        })
        .catch(error => {
          console.error('There was an error fetching the finger count!', error);
        });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Finger Count: {fingerCount}</h1>
        <img src="http://127.0.0.1:5000/video_feed" alt="Video Feed" />
      </header>
    </div>
  );
}

export default App;
