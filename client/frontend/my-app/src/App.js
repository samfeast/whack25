import "./App.css";
import { useEffect, useState } from "react";
import cardMap from "./cardMap";
import handBorder from "./assets/border.svg";
import backOfCard from "./assets/back_of_card.svg";
import { useWebSocket, WebSocketProvider } from "./WSProvider";

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
        <WebSocketProvider>
          {screen === "menu" && <MenuScreen setScreen={setScreen} />}
          {screen === "waiting" && <WaitingScreen setScreen={setScreen} />}
          {screen === "game" && <GameScreen />}
        </WebSocketProvider>
      </header>
    </div>
  );
}

function MenuScreen({ setScreen }) {
  const ws = useWebSocket();

  const [name, setName] = useState("");

  const handleName = (type) => {
    if (!name.trim()) {
      alert("Please enter a name!");
      return;
    }
    if (type === "waiting") {
      ws.current.send(name);
      setScreen("waiting");
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
      <button className="Join-Button" onClick={() => handleName("waiting")}>
        JOIN GAME
      </button>
    </>
  );
}

function WaitingScreen({ setScreen }) {
  const ws = useWebSocket();

  const handleReady = (type) => {
    if (type === "game") {
      ws.current.send("ready");
      setScreen("game");
      return;
    }
  };

  return (
    <button className="Ready-Button" onClick={() => handleReady("game")}>
      Ready?
    </button>
  );
}
function GameScreen() {
  const [playerHand, setPlayerHand] = useState(["D4"]);
  const [stackSize, setStackSize] = useState(0);
  const [ownTurn, setOwnTurn] = useState(true);
  const [lastRank, setLastRank] = useState(0);
  const [playerInfo, setPlayerInfo] = useState([]);

  const [selectedCards, setSelectedCards] = useState([]);

  const ws = useWebSocket();

  useEffect(() => {
    if (!ws?.current) return;

    const handleMessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.hand) setPlayerHand(data.hand);
      if (typeof data["stack-size"] === "number")
        setStackSize(data["stack-size"]);
      if (typeof data["own-turn"] === "boolean") setOwnTurn(data["own-turn"]);
      if (typeof data.current_rank === "number") setLastRank(data.current_rank);
      if (Array.isArray(data.player_info)) setPlayerInfo(data.player_info);
    };

    ws.current.addEventListener("message", handleMessage);

    return () => {
      ws.current.removeEventListener("message", handleMessage);
    };
  }, [ws]);

  const handleCardClick = (cardKey) => {
    setSelectedCards((prev) =>
      prev.includes(cardKey)
        ? prev.filter((c) => c !== cardKey)
        : [...prev, cardKey]
    );
  };

  const handlePlaySelectedCards = async () => {
    if (selectedCards.length === 0) {
      alert("No cards selected!");
      return;
    }

    try {
      const response = await fetch(`/fer.txt?ts=${Date.now()}`);
      const text = await response.text();

      ws.current.send(JSON.stringify({ discard: selectedCards, data: text }));
    } catch (err) {
      console.error("Error reading file:", err);
    }

    setLastRank((prev) => (prev + 1 > 13 ? 1 : prev + 1));
    setOwnTurn(false); // setOwnTurn(false); true for testing
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
      />
      <PlayerDisplay playerInfo={playerInfo} />
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
function ActionButton({ onPlaySelectedCards, ownTurn }) {
  const ws = useWebSocket();

  const handleCallCheat = async () => {
    try {
      const response = await fetch(`/fer.txt?ts=${Date.now()}`);
      const text = await response.text();

      ws.current.send(JSON.stringify({ callout: true, data: text }));
    } catch (err) {
      console.error("Error reading file:", err);
    }
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
        CALL CHEAT!
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
    </div>
  );
}

function PlayerDisplay({ playerInfo }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
      }}
    >
      {playerInfo.map((player, index) => (
        <div key={index} className="Player-Display">
          <p>
            {player.name}: {player.cards} cards. {player.message}
          </p>
        </div>
      ))}
    </div>
  );
}

export default App;
