import { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function App() {
  const [listening, setListening] = useState(false);
  const [messages, setMessages] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [isSpeaking, setIsSpeaking] = useState(false);
  const chatRef = useRef(null);

  const recognitionRef = useRef(null);
  const isRecognizingRef = useRef(false);

  useEffect(() => {
    const recognition = new window.webkitSpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    recognition.onstart = () => {
      isRecognizingRef.current = true;
    };

    recognition.onerror = (event) => {
      console.log("Speech error:", event.error);
      isRecognizingRef.current = false;
    };

    recognition.onend = () => {
      isRecognizingRef.current = false;
    };

    recognition.onresult = async (event) => {
      recognition.stop();

      const text = event.results[event.results.length - 1][0].transcript;

      setMessages((prev) => [...prev, { sender: "user", text }]);

      try {
        // const res = await axios.post("http://127.0.0.1:8000/chat", {
        const res = await axios.post("https://mantri-ai.onrender.com/chat", {
          message: text,
        });

        const reply =
          res.data?.choices?.[0]?.message?.content ||
          "Sorry, something went wrong.";

        setMessages((prev) => [...prev, { sender: "ai", text: reply }]);

        // speak(humanize(reply));
        speak(reply);
      } catch (err) {
        console.error(err);
      }
    };

    recognitionRef.current = recognition;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listening]);

  // const humanize = (text) => {
  //   return text.replace(/\./g, "... ").replace(/,/g, ", ");
  // };

  const startListening = () => {
    window.speechSynthesis.cancel();
    setListening(true);

    isRecognizingRef.current = false; // force reset
    recognitionRef.current.start();
  };

  const speak = (text) => {
    setIsSpeaking(true);

    const speech = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();

    const hindiVoice = voices.find((v) => v.lang === "hi-IN");
    const englishVoice = voices.find((v) => v.lang === "en-IN");

    speech.voice = hindiVoice || englishVoice || voices[0];
    speech.lang = hindiVoice ? "hi-IN" : "en-IN";

    speech.rate = 0.9;
    speech.pitch = 1.1;

    speech.onend = () => {
      setIsSpeaking(false);

      // 🎤 Restart listening AFTER AI finishes
      if (listening) {
        isRecognizingRef.current = false; // force reset
        recognitionRef.current.start();
      }
    };

    window.speechSynthesis.speak(speech);
  };

  return (
    <div
      style={{
        height: "100vh",
        overflow: "hidden",
        background: "linear-gradient(135deg, #0f172a, #020617)",
        color: "white",
        display: "flex",
        flexDirection: "column",
        fontFamily: "Arial, sans-serif",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "20px",
          borderBottom: "1px solid #1e293b",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1 style={{ fontSize: "22px" }}>
          🎤 Mantri AI : Your AI advisor for every thought
        </h1>
        <button
          onClick={startListening}
          style={{
            padding: "10px 18px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer",
            background: listening ? "#22c55e" : "#2563eb",
            color: "white",
            fontWeight: "bold",
          }}
        >
          {listening ? "Listening..." : "Start Talking"}
        </button>
        <button
          onClick={() => {
            window.speechSynthesis.cancel(); // stop AI
            setIsSpeaking(false);

            // restart listening instantly
            isRecognizingRef.current = false;
            recognitionRef.current.start();
          }}
          style={{
            padding: "10px 18px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer",
            background: "#ef4444",
            color: "white",
            fontWeight: "bold",
          }}
        >
          Interrupt
        </button>
      </div>

      {/* Chat Area */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "20px",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: "700px",
            height: "100%",
            maxHeight: "75vh",
            background: "rgba(15, 23, 42, 0.8)",
            border: "1px solid #1e293b",
            borderRadius: "20px",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 0 40px rgba(0,0,0,0.6)",
          }}
        >
          {/* Messages */}
          <div
            ref={chatRef}
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            {messages.length === 0 && (
              <p style={{ textAlign: "center", color: "#94a3b8" }}>
                Start speaking to begin conversation...
              </p>
            )}

            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  justifyContent:
                    msg.sender === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "70%",
                    padding: "10px 14px",
                    borderRadius: "15px",
                    background: msg.sender === "user" ? "#2563eb" : "#334155",
                  }}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div
            style={{
              padding: "10px",
              borderTop: "1px solid #1e293b",
              textAlign: "center",
              fontSize: "12px",
              color: "#94a3b8",
            }}
          >
            Real-time Voice Conversation • AI Powered
          </div>
        </div>
      </div>
    </div>
  );
}
