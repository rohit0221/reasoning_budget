import React, { useState, useEffect, useRef } from 'react';
import { Send, Zap, Brain, Check, Play, Clock, Terminal, Activity, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = "http://localhost:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [importance, setImportance] = useState("normal");
  const [steps, setSteps] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [finalResult, setFinalResult] = useState(null);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [steps]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsProcessing(true);
    setSteps([]);
    setFinalResult(null);

    const eventSource = new EventSource(`${API_URL}/stream?question=${encodeURIComponent(question)}&importance=${importance}`);

    eventSource.onmessage = (event) => {
      console.log("Received 'message' event:", event.data);
      try {
        const data = JSON.parse(event.data);
        if (data.step === "COMPLETE") {
          setFinalResult(data.final_payload);
          eventSource.close();
          setIsProcessing(false);
        } else {
          setSteps(prev => [...prev, data]);
        }
      } catch (e) {
        console.error("Failed to parse message data:", e);
      }
    };

    eventSource.addEventListener("update", (event) => {
      console.log("Received 'update' event:", event.data);
      try {
        const data = JSON.parse(event.data);
        if (data.step === "COMPLETE") {
          setFinalResult(data.final_payload);
          eventSource.close();
          setIsProcessing(false);
        } else {
          setSteps(prev => [...prev, data]);
        }
      } catch (e) {
        console.error("Failed to parse update data:", e);
      }
    });

    eventSource.addEventListener("error", (event) => {
      console.error("Backend sent 'error' event:", event.data);
      try {
        const errData = JSON.parse(event.data);
        alert(`Backend Error: ${errData.message || event.data}`);
      } catch {
        alert(`Backend Error: ${event.data}`);
      }
      eventSource.close();
      setIsProcessing(false);
    });

    eventSource.onopen = () => {
      console.log("Connection opened via EventSource");
    };

    eventSource.onerror = (err) => {
      console.log("EventSource.onerror triggered. ReadyState:", eventSource.readyState);

      if (eventSource.readyState === 2) {
        // CLOSED
        console.log("Stream closed by server.");
        if (isProcessing) {
          console.warn("Stream closed but processing was not marked complete. This might be a premature closure.");
        }
      } else if (eventSource.readyState === 0) { // CONNECTING
        console.log("Stream lost connection, trying to reconnect...");
        eventSource.close();
        setIsProcessing(false);
        alert("Connection lost. Check backend logs.");
      } else {
        console.error("Unknown EventSource error:", err);
        eventSource.close();
        setIsProcessing(false);
        alert("Network Error! Check browser console.");
      }
    };
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* LEFT COLUMN: Input & Result */}
        <div className="space-y-8">

          {/* Header */}
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700 shadow-xl">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-2">
              Thinking-Budget Controller
            </h1>
            <p className="text-slate-400">
              Adaptive reasoning agent powered by GPT-5-nano.
            </p>
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700 shadow-xl space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Question</label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-4 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all placeholder:text-slate-600 resize-none h-32"
                placeholder="Ex: What is 15% of 2500?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Importance Level</label>
              <div className="flex gap-4">
                {['low', 'normal', 'high'].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setImportance(level)}
                    className={`flex-1 py-3 px-4 rounded-xl border transition-all font-medium capitalize flex items-center justify-center gap-2
                      ${importance === level
                        ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20'
                        : 'bg-slate-900/50 border-slate-700 text-slate-400 hover:bg-slate-800'
                      }`}
                  >
                    {level === 'high' && <Zap size={16} className="text-yellow-400 fill-yellow-400" />}
                    {level}
                  </button>
                ))}
              </div>
            </div>

            <button
              disabled={isProcessing}
              type="submit"
              className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-bold text-lg shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <>
                  <Activity className="animate-spin" /> Processing...
                </>
              ) : (
                <>
                  <Play className="fill-current" size={20} /> Run Simulation
                </>
              )}
            </button>
          </form>

          {/* Final Result Card */}
          <AnimatePresence>
            {finalResult && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-emerald-900/20 backdrop-blur-lg rounded-2xl p-6 border border-emerald-500/30 shadow-2xl relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-32 bg-emerald-500/10 blur-[100px] rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none" />

                <h2 className="text-emerald-400 font-bold text-sm uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Check size={18} /> Final Answer
                </h2>

                <div className="text-4xl font-mono font-bold text-white mb-6">
                  {finalResult.answer}
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                    <span className="text-slate-400 block mb-1">Total Tokens</span>
                    <span className="font-mono text-emerald-300">{finalResult.usage.total_tokens}</span>
                  </div>
                  <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                    <span className="text-slate-400 block mb-1">Reasoning Tokens</span>
                    <span className="font-mono text-blue-300">{finalResult.usage.reasoning_tokens}</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* RIGHT COLUMN: Process Visualization */}
        <div className="bg-slate-800/30 backdrop-blur-md rounded-2xl border border-slate-700/50 p-6 shadow-2xl flex flex-col h-[800px]">
          <h2 className="text-xl font-bold text-slate-200 mb-6 flex items-center gap-2">
            <Activity className="text-blue-400" />
            Live Execution Stream
          </h2>

          <div className="flex-1 overflow-y-auto space-y-6 pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
            <AnimatePresence mode="popLayout">
              {steps.map((step, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20, scale: 0.95 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  className="relative pl-8 border-l-2 border-slate-700"
                >
                  <div className={`absolute left-[-9px] top-0 w-4 h-4 rounded-full border-4 border-slate-800 
                    ${step.type === 'agent_action' ? 'bg-blue-500' :
                      step.type === 'decision' ? 'bg-purple-500' :
                        step.type === 'alert' ? 'bg-yellow-500' :
                          step.type === 'success' ? 'bg-emerald-500' : 'bg-slate-500'}`}
                  />

                  <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-700/50 hover:border-slate-600 transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-mono text-slate-500">{step.step}</span>
                      {step.timestamp && <span className="text-xs text-slate-600 flex items-center gap-1"><Clock size={10} /> {new Date(step.timestamp * 1000).toLocaleTimeString()}</span>}
                    </div>

                    <p className={`text-sm font-medium ${step.type === 'success' ? 'text-emerald-300' : 'text-slate-200'}`}>
                      {step.message}
                    </p>

                    {/* render details if present */}
                    {step.details && (
                      <div className="mt-3 bg-slate-950/50 rounded p-3 overflow-x-auto border border-slate-800">
                        <pre className="text-xs text-blue-300 font-mono">
                          {JSON.stringify(step.details, null, 2)}
                        </pre>
                      </div>
                    )}
                    {step.data && (
                      <div className="mt-3 bg-purple-900/10 rounded p-3 border border-purple-500/20">
                        <pre className="text-xs text-purple-300 font-mono">
                          {JSON.stringify(step.data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={bottomRef} />

            {steps.length === 0 && !isProcessing && (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-50">
                <Brain size={48} className="mb-4" />
                <p>Waiting for query...</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
