import "./App.css";
import Sidebar from "./components/Sidebar/Sidebar";
import ChatHeader from "./features/chat/components/ChatHeader/ChatHeader";
import ChatThread from "./features/chat/components/ChatThread/ChatThread";
import Telemetry from "./features/chat/components/Telemetry/Telemetry";
import ChatInput from "./features/chat/components/ChatInput/ChatInput";
import { useChatStream } from "./features/chat/hooks/useChatStream";
import { useSources } from "./features/chat/hooks/useSources";

export default function App() {
  const { input, setInput, messages, openCitation, handleSend, toggleCitation } =
    useChatStream([]);
  const { sources, addSource } = useSources();

  return (
    <div className="app">
      <Sidebar sources={sources} onAddSource={addSource} />

      <div className="main">
        <ChatHeader title="ai-document-assistant" />

        <ChatThread
          messages={messages}
          openCitation={openCitation}
          onToggleCitation={toggleCitation}
        />

        <div className="footer">
          <Telemetry />
          <ChatInput value={input} onChange={setInput} onSend={handleSend} />
        </div>
      </div>
    </div>
  );
}
