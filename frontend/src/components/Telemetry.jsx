export default function Telemetry({ ttft, tokens, cost }) {
  return (
    <div className="telemetry">
      <span>TTFT <b>{ttft}</b></span>
      <span>tokens <b>{tokens}</b></span>
      <span>cost <b>{cost}</b></span>
    </div>
  );
}
