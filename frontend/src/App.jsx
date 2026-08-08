import { useState } from "react";
import "./App.css";
import Sidebar from "./components/Sidebar";
import ChatHeader from "./components/ChatHeader";
import ChatThread from "./components/ChatThread";
import Telemetry from "./components/Telemetry";
import ChatInput from "./components/ChatInput";
import { mockSources, mockMessages } from "./data/mockData";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(mockMessages);
  const [openCitation, setOpenCitation] = useState(null);

  function handleSend() {
    if (!input.trim()) return;
    setMessages((m) => [...m, { id: Date.now(), role: "user", text: input }]);
    setInput("");
  }

  function toggleCitation(n) {
    setOpenCitation((current) => (current === n ? null : n));
  }

  return (
    <div className="app">
      <Sidebar sources={mockSources} />

      <div className="main">
        <ChatHeader title="ai-document-assistant" />

        <ChatThread
          messages={messages}
          openCitation={openCitation}
          onToggleCitation={toggleCitation}
        />

        <div className="footer">
          <Telemetry ttft="340ms" tokens="1.2k" cost="$0.004" />
          <ChatInput value={input} onChange={setInput} onSend={handleSend} />
        </div>
      </div>
    </div>
  );
}
