import "./App.css";
import { useState } from "react";
import cardMap from "./cardMap";
import handBorder from "./assets/border.svg";
import backOfCard from "./assets/back_of_card.svg";

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
  const [playerHand, setPlayerHand] = useState(["D1", "H10", "C11", "S3"]);
  const [stackSize, setStackSize] = useState(0);
  const [ownTurn, setOwnTurn] = useState(true);
  const [baseCard, setBaseCard] = useState("D5");

  const [selectedCards, setSelectedCards] = useState([]);

  const handleCardClick = (cardKey) => {
    setSelectedCards((prev) =>
      prev.includes(cardKey)
        ? prev.filter((c) => c !== cardKey)
        : [...prev, cardKey]
    );
  };

  const handlePlaySelectedCards = () => {
    if (selectedCards.length === 0) {
      alert("No cards selected!");
      return;
    }
    alert(`Playing selected cards: ${selectedCards.join(", ")}`);
    setOwnTurn(false);
    setStackSize((prev) => prev + selectedCards.length);
    const selectedSet = new Set(selectedCards);
    setPlayerHand((prev) => prev.filter((c) => !selectedSet.has(c)));
    setSelectedCards([]);
  };

  return (
    <div className="Game-Screen">
      <CardHand
        hand={playerHand}
        selectedCards={selectedCards}
        onCardClick={handleCardClick}
      />
      <CardStack stackSize={stackSize} baseCard={baseCard} />
      <ActionButton
        onPlaySelectedCards={handlePlaySelectedCards}
        ownTurn={ownTurn}
      />
    </div>
  );
}

function CardHand({ hand, selectedCards, onCardClick }) {
  const handLength = hand.length;
  const angleRange = Math.min(60, (handLength - 1) * 12);

  return (
    <div className="Card-Hand">
      {hand.map((cardKey, index) => {
        const isSelected = selectedCards.includes(cardKey);
        const circleRadius = isSelected ? 525 : 500;
        const angleDeg =
          handLength != 1
            ? (180 - angleRange) / 2 + (index * angleRange) / (handLength - 1)
            : 90;
        const x = -75 + circleRadius * Math.cos((angleDeg * Math.PI) / 180);
        const y = 875 - circleRadius * Math.sin((angleDeg * Math.PI) / 180);
        return (
          <img
            key={index}
            src={cardMap[cardKey]}
            alt={cardKey}
            className={isSelected ? "Card-Selected" : "Card"}
            style={{
              "--card-rotation": `${90 - angleDeg}deg`,
              "--card-x": `${x}px`,
              "--card-y": `${y}px`,
            }}
            onClick={() => onCardClick(cardKey)}
          />
        );
      })}
      <img src={handBorder} alt="border" className="Hand-Border"></img>
    </div>
  );
}

function CardStack({ stackSize, baseCard }) {
  const rotationOffset = [
    -67, 0, 37, -20, 58, -35, -60, 39, -42, 11, 53, 70, 34, 27, -33, 31, -26,
    23, -59, 35, -70, 18, -19, 2, 48, 44, -25, -73, -15, -11,
  ];

  const maxVisible = 4;

  const startIndex =
    stackSize <= maxVisible
      ? 0
      : (stackSize - maxVisible) % rotationOffset.length;

  const visibleCards = Array.from({
    length: Math.min(stackSize, maxVisible),
  }).map((_, i) => {
    const rotationIndex = (startIndex + i) % rotationOffset.length;
    return rotationOffset[rotationIndex];
  });

  return (
    <div>
      <img
        className="Stack-Card"
        src={cardMap[baseCard]}
        alt="base card"
        style={{
          "--card-rotation": `0deg`,
        }}
      />
      {visibleCards.map((rotation, i) => (
        <img
          key={i}
          className="Stack-Card"
          src={backOfCard}
          alt="card back"
          style={{
            "--card-rotation": `${rotation}deg`,
          }}
        />
      ))}
    </div>
  );
}

function ActionButton({ onPlaySelectedCards, ownTurn }) {
  const handleCallCheat = () => {
    alert("Cheat called!");
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "flex-end",
        flexDirection: "column",
        alignItems: "flex-end",
      }}
    >
      <button
        className="Game-Button"
        onClick={handleCallCheat}
        style={{
          marginTop: "20px",
          marginRight: "20px",
          width: "250px",
          backgroundColor: "#7d0a14",
          color: "white",
          borderColor: "white",
          borderWidth: "2px",
          borderStyle: "solid",
        }}
      >
        CALL CHEAT
      </button>
      <button
        className="Game-Button"
        disabled={!ownTurn}
        onClick={onPlaySelectedCards}
        style={{
          marginTop: "20px",
          marginRight: "20px",
          width: "250px",
          backgroundColor: ownTurn ? "#0a477d" : "#585858",
          color: "white",
          borderColor: "white",
          borderWidth: "2px",
          borderStyle: "solid",
        }}
      >
        PLAY SELECTED CARDS
      </button>
    </div>
  );
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

export default App;
