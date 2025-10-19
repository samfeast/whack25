import "./App.css";
import { useState } from "react";
import cardMap from "./cardMap";
import handBorder from "./assets/border.svg";
import backOfCard from "./assets/back_of_card.svg";

const rankMap = {
  1: "Ace",
  2: "2",
  3: "3",
  4: "4",
  5: "5",
  6: "6",
  7: "7",
  8: "8",
  9: "9",
  10: "10",
  11: "Jack",
  12: "Queen",
  13: "King",
};

function App() {
  const [screen, setScreen] = useState("menu");

  return (
    <div className="App">
      <header className="App-header">
        {screen === "menu" && <MenuScreen setScreen={setScreen} />}
        {screen === "game" && <GameScreen />}
      </header>
    </div>
  );
}

function MenuScreen({ setScreen }) {
  const [name, setName] = useState("");

  const handleName = (type) => {
    if (!name.trim()) {
      alert("Please enter a name!");
      return;
    }
    if (type === "join") {
      setScreen("game");
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
        className="Name-Box"
        maxLength={12}
      />
      <button className="Join-Button" onClick={() => handleName("join")}>
        JOIN GAME
      </button>
    </>
  );
}

function GameScreen() {
  const [playerHand, setPlayerHand] = useState(["D1", "H10", "C11", "S3"]);
  const [stackSize, setStackSize] = useState(0);
  const [ownTurn, setOwnTurn] = useState(true);
  const [selectedCards, setSelectedCards] = useState([]);
  const [lastRank, setLastRank] = useState(0);
  const [selectedRank, setSelectedRank] = useState(0);

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
    setLastRank(selectedRank);
    setOwnTurn(true); // setOwnTurn(false); true for testing
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
      <CardStack stackSize={stackSize} />
      <ActionButton
        onPlaySelectedCards={handlePlaySelectedCards}
        ownTurn={ownTurn}
        setSelectedRank={setSelectedRank}
        lastRank={lastRank}
      />
    </div>
  );
}

// The player's hand of cards displayed in a fanned-out arc at the bottom of the screen
function CardHand({ hand, selectedCards, onCardClick }) {
  const angleRange = Math.min(60, (hand.length - 1) * 12);

  return (
    <div className="Card-Hand">
      {hand.map((cardKey, index) => {
        const isSelected = selectedCards.includes(cardKey);
        const circleRadius = isSelected ? 525 : 500;

        const angleDeg =
          hand.length !== 1
            ? (180 - angleRange) / 2 + (index * angleRange) / (hand.length - 1)
            : 90;

        const x = -75 + circleRadius * Math.cos((angleDeg * Math.PI) / 180);
        const y = 875 - circleRadius * Math.sin((angleDeg * Math.PI) / 180);
        return (
          <img
            key={index}
            src={cardMap[cardKey]}
            className={isSelected ? "Card-Selected" : "Card"}
            style={{
              "--card-rotation": `${90 - angleDeg}deg`,
              "--card-x": `${x}px`,
              "--card-y": `${y}px`,
            }}
            onClick={() => onCardClick(cardKey)}
            alt=""
          />
        );
      })}
      <img src={handBorder} className="Hand-Border" alt=""></img>
    </div>
  ); // Also render a wooden border svg around the hand
}

// The pile of cards being added to in the center of the table
function CardStack({ stackSize }) {
  const rotationOffset = [
    -67, 0, 37, -20, 58, -35, -60, 39, -42, 11, 53, 70, 34, 27, -33, 31, -26,
    23, -59, 35, -70, 18, -19, 2, 48, 44, -25, -73, -15, -11,
  ];

  // Render the top N cards in the stack (values too large degrade performance)
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
      {visibleCards.map((rotation, i) => (
        <img
          key={i}
          className="Stack-Card"
          src={backOfCard}
          style={{
            "--card-rotation": `${rotation}deg`,
          }}
          alt=""
        />
      ))}
    </div>
  );
}

// The "Call Cheat" and "Play Selected Cards" buttons
function ActionButton({
  onPlaySelectedCards,
  ownTurn,
  setSelectedRank,
  lastRank,
}) {
  const handleCallCheat = () => {
    alert("Cheat called!");
    // Access fer.txt and send to WS
  };

  const options =
    lastRank === 0
      ? Object.keys(rankMap).map(Number)
      : [
          (lastRank - 1) % 13 === 0 ? 13 : (lastRank - 1) % 13,
          lastRank,
          (lastRank + 1) % 13 === 0 ? 13 : (lastRank + 1) % 13,
        ];

  const handleChange = (event) => {
    setSelectedRank(Number(event.target.value));
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-end",
      }}
    >
      <button
        className="Action-Button"
        onClick={handleCallCheat}
        style={{
          backgroundColor: "#7d0a14",
        }}
      >
        CALL CHEAT
      </button>
      <button
        className="Action-Button"
        disabled={!ownTurn}
        onClick={onPlaySelectedCards}
        style={{
          backgroundColor: ownTurn ? "#0a477d" : "#585858",
        }}
      >
        PLAY SELECTED CARDS
      </button>
      <select
        className="Action-Button"
        onChange={handleChange}
        style={{
          backgroundColor: ownTurn ? "#035752" : "#585858",
          textAlign: "center",
        }}
      >
        <option value="">Select a rank</option>
        {options.map((rank) => (
          <option key={rank} value={rank}>
            {"Claim to play " + rankMap[rank]}
          </option>
        ))}
      </select>
    </div>
  );
}

export default App;
