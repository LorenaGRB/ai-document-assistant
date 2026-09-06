import "./App.css";
import Sidebar from "./components/Sidebar/Sidebar";
import ChatHeader from "./features/chat/components/ChatHeader/ChatHeader";
import ChatThread from "./features/chat/components/ChatThread/ChatThread";
import Telemetry from "./features/chat/components/Telemetry/Telemetry";
import ChatInput from "./features/chat/components/ChatInput/ChatInput";
import { useChatStream } from "./features/chat/hooks/useChatStream";
import { mockSources, mockMessages } from "./data/mockData";

export default function App() {
  const { input, setInput, messages, openCitation, handleSend, toggleCitation } =
    useChatStream(mockMessages);

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
