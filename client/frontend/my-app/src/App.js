import "./App.css";
import { useState } from "react";
import cardMap from "./cardMap";
import handBorder from "./assets/border.svg";

function App() {
  const [screen, setScreen] = useState("menu");

  function enterGame(code) {
    alert("Entering game with code: " + code);
    setScreen("game");
  }

  return (
    <div className="App">
      <header className="App-header">
        {screen === "menu" && (
          <MenuScreen setScreen={setScreen} enterGame={enterGame} />
        )}
        {screen === "join" && (
          <JoinScreen onBack={() => setScreen("menu")} enterGame={enterGame} />
        )}
        {screen === "game" && <GameScreen />}
      </header>
    </div>
  );
}

function MenuScreen({ setScreen, enterGame }) {
  const [name, setName] = useState("");

  const handleName = (type) => {
    if (!name.trim()) {
      alert("Please enter a name!");
      return;
    }
    if (type === "start") {
      const code = makeGameCode(4);
      enterGame(code);
      return;
    }
    if (type === "join") {
      setScreen("join");
      return;
    }
  };

  return (
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
        <button className="Game-Button" onClick={() => handleName("start")}>
          START GAME
        </button>
        <button className="Game-Button" onClick={() => handleName("join")}>
          JOIN GAME
        </button>
      </div>
    </>
  );
}

function JoinScreen({ onBack, enterGame }) {
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

    enterGame(code);
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

function GameScreen() {
  const playerHand = ["C1", "D8", "H12", "H4", "S11", "D3", "C10"];
  const stackSize = 5;

  return (
    <div className="Game-Screen">
      <CardHand hand={playerHand} />
      <CardStack stackSize={stackSize} />
    </div>
  );
}

function CardHand({ hand }) {
  const [selectedCards, setSelectedCards] = useState([]);
  const handLength = hand.length;
  const angleRange = 60;

  const handleCardClick = (cardKey) => {
    setSelectedCards(
      (prev) =>
        prev.includes(cardKey)
          ? prev.filter((c) => c !== cardKey) // unclick if already clicked
          : [...prev, cardKey] // add if not clicked
    );
  };

  return (
    <div className="Card-Hand">
      {hand.map((cardKey, index) => {
        const isSelected = selectedCards.includes(cardKey);
        const circleRadius = isSelected ? 525 : 500;
        const angle =
          (Math.PI * (90 - angleRange / 2)) / 180 +
          index * ((Math.PI * angleRange) / 180 / (handLength - 1));
        const relativeAngle = -((angle - Math.PI / 2) * 180) / Math.PI;
        const x = -75 + circleRadius * Math.cos(angle);
        const y = 875 - circleRadius * Math.sin(angle);
        return (
          <img
            key={index}
            src={cardMap[cardKey]}
            alt={cardKey}
            className={isSelected ? "Card-Selected" : "Card"}
            style={{
              "--card-rotation": `${relativeAngle}deg`,
              "--card-x": `${x}px`,
              "--card-y": `${y}px`,
            }}
            onClick={() => handleCardClick(cardKey)}
          />
        );
      })}
      <img src={handBorder} alt="border" className="Hand-Border"></img>
    </div>
  );
}

function CardStack({ stackSize }) {
  return <div className="Card-Stack"></div>;
}

function validateGameCode(gameCode) {
  return true;
}

function makeGameCode(length) {
  var result = "";
  var characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  var charactersLength = characters.length;
  for (var i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

function getHand() {
  // hardcoded
  return ["D1", "H10", "C11"];
}

export default App;
