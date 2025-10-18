import "./App.css";
import { useState } from "react";

function App() {
  const [screen, setScreen] = useState("menu");
  const [name, setName] = useState("");

  const handleName = (type) => {
    if (!name.trim()) {
      alert("Please enter a name!");
      return;
    }
    if (type === "create") {
      createGame();
      return;
    }
    if (type === "join") {
      console.log("HERe");
      setScreen("join");
      return;
    }
  };

  const createGame = () => {
    alert(`Creating game for player: ${name}`);
  };

  return (
    <div className="App">
      <header className="App-header">
        {screen === "menu" && (
          <>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              className="Text-Box"
              maxLength={12}
            />
            <div className="Button-Group">
              <button
                className="Game-Button"
                onClick={() => handleName("create")}
              >
                CREATE GAME
              </button>
              <button
                className="Game-Button"
                onClick={() => handleName("join")}
              >
                JOIN GAME
              </button>
            </div>
          </>
        )}

        {screen === "join" && <JoinGame onBack={() => setScreen("menu")} />}
      </header>
    </div>
  );
}

function JoinGame({ onBack }) {
  const [code, setCode] = useState("");

  const handleJoin = () => {
    if (!code.trim()) {
      alert("Please enter a game code!");
      return;
    }
    const isValid = validateGameCode(code);
    if (!isValid) {
      alert("Invalid game code!");
      return;
    }

    alert("Joining game with code: " + code);
  };

  return (
    <div className="Join-Screen">
      <input
        type="text"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Game Code"
        className="Text-Box"
        maxLength={4}
      />
      <div className="Button-Group">
        <button className="Game-Button" onClick={handleJoin}>
          JOIN
        </button>
        <button className="Game-Button" onClick={onBack}>
          BACK
        </button>
      </div>
    </div>
  );
}

function validateGameCode(gameCode) {
  return false;
}

export default App;
