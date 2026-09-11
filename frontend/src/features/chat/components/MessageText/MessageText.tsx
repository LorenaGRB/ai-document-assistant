import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MessageTextProps {
  text: string;
}

export default function MessageText({ text }: MessageTextProps) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {text}
    </ReactMarkdown>
  );
}