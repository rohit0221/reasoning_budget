import React, { useState, useEffect, useRef } from 'react';
import { Send, Zap, Brain, Check, Play, Clock, Terminal, Activity, Info, Bot, Calculator } from 'lucide-react';
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

    // Listen for custom "update" event just in case
    eventSource.addEventListener("update", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.step === "COMPLETE") {
          setFinalResult(data.final_payload);
          eventSource.close();
          setIsProcessing(false);
        } else {
          setSteps(prev => [...prev, data]);
        }
      } catch (e) { console.error(e); }
    });

    eventSource.addEventListener("error", (event) => {
      try {
        const errData = JSON.parse(event.data);
        alert(`Backend Error: ${errData.message}`);
      } catch { alert(`Backend Error: ${event.data}`); }
      eventSource.close();
      setIsProcessing(false);
    });

    eventSource.onerror = (err) => {
      if (eventSource.readyState === 2) {
        // Closed by server (normal or premature)
        if (isProcessing) console.warn("Stream closed.");
      } else {
        console.error("EventSource Error:", err);
        eventSource.close();
        setIsProcessing(false);
        alert("Connection Lost. Ensure Backend is running.");
      }
    };
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans selection:bg-blue-500/30">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* LEFT COLUMN: Input & Result */}
        <div className="space-y-8 h-fit sticky top-8">

          {/* Header */}
          <div className="bg-slate-900/50 backdrop-blur-xl rounded-3xl p-8 border border-slate-800 shadow-2xl">
            <h1 className="text-4xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-3 tracking-tight">
              Thinking-Budget
            </h1>
            <p className="text-slate-400 text-lg flex items-center gap-2">
              <Bot size={20} className="text-blue-400" />
              Adaptive Reasoning Control System
            </p>
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur-xl rounded-3xl p-8 border border-slate-800 shadow-2xl space-y-6">
            <div>
              <label className="block text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Your Question</label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-all placeholder:text-slate-700 resize-none h-32 text-lg"
                placeholder="Ex: What is 15% of 2500?"
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Importance Level</label>
              <div className="flex gap-3">
                {['low', 'normal', 'high'].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setImportance(level)}
                    className={`flex-1 py-4 px-4 rounded-xl border-2 transition-all font-bold capitalize flex items-center justify-center gap-2 text-sm
                      ${importance === level
                        ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-500/30 scale-105'
                        : 'bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700 hover:text-slate-200'
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
              className="w-full py-5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl font-bold text-lg text-white shadow-xl shadow-blue-900/20 hover:shadow-blue-600/40 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
            >
              {isProcessing ? (
                <>
                  <Activity className="animate-spin" /> initializing agents...
                </>
              ) : (
                <>
                  <Play className="fill-current" size={24} /> Start Simulation
                </>
              )}
            </button>
          </form>

          {/* Final Result Card */}
          <AnimatePresence>
            {finalResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="bg-emerald-950/30 backdrop-blur-xl rounded-3xl p-8 border border-emerald-500/30 shadow-2xl relative overflow-hidden group"
              >
                <div className="absolute top-0 right-0 p-40 bg-emerald-500/10 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none group-hover:bg-emerald-500/20 transition-all duration-1000" />

                <h2 className="text-emerald-400 font-bold text-sm uppercase tracking-widest mb-6 flex items-center gap-2 border-b border-emerald-500/20 pb-4">
                  <Check size={18} /> Final Answer
                </h2>

                <div className="text-5xl font-mono font-bold text-white mb-8 tracking-tighter">
                  {finalResult.answer}
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-slate-950/50 p-4 rounded-xl border border-emerald-900/50">
                    <span className="text-slate-400 block mb-1 text-xs uppercase tracking-wider">Total Tokens</span>
                    <span className="font-mono text-2xl font-bold text-emerald-300">{finalResult.usage.total_tokens}</span>
                  </div>
                  <div className="bg-slate-950/50 p-4 rounded-xl border border-blue-900/50">
                    <span className="text-slate-400 block mb-1 text-xs uppercase tracking-wider">Reasoning Tokens</span>
                    <span className="font-mono text-2xl font-bold text-blue-300">{finalResult.usage.reasoning_tokens}</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* RIGHT COLUMN: Process Visualization */}
        <div className="bg-slate-900/30 backdrop-blur-md rounded-3xl border border-slate-800 p-8 shadow-2xl flex flex-col h-[850px] relative overflow-hidden">
          {/* Background Grid */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

          <h2 className="text-xl font-bold text-slate-200 mb-8 flex items-center gap-3 z-10">
            <span className="relative flex h-3 w-3">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75 ${!isProcessing && 'hidden'}`}></span>
              <span className={`relative inline-flex rounded-full h-3 w-3 bg-blue-500 ${!isProcessing && 'bg-slate-600'}`}></span>
            </span>
            Live Agent Stream
          </h2>

          <div className="flex-1 overflow-y-auto space-y-8 pr-4 z-10 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent pb-20">
            <AnimatePresence mode="popLayout">
              {steps.map((step, idx) => {
                // SPECIAL RENDER FOR AGENT SWITCHING
                if (step.type === 'agent_action') {
                  const isController = step.agent === 'controller';
                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -50 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="mt-8 mb-4 border-t border-dashed border-slate-700 pt-8 first:mt-0 first:pt-0 first:border-0"
                    >
                      <div className={`p-4 rounded-2xl flex items-center gap-4 ${isController ? 'bg-cyan-950/30 border border-cyan-500/30' : 'bg-violet-950/30 border border-violet-500/30'}`}>
                        <div className={`p-3 rounded-xl ${isController ? 'bg-cyan-500 text-cyan-950' : 'bg-violet-500 text-white'}`}>
                          {isController ? <Calculator size={24} /> : <Brain size={24} />}
                        </div>
                        <div>
                          <h3 className={`font-bold text-lg ${isController ? 'text-cyan-300' : 'text-violet-300'}`}>
                            {isController ? 'AGENT 1: BUDGET CONTROLLER' : 'AGENT 2: REASONING ENGINE'}
                          </h3>
                          <p className="text-slate-400 text-sm">
                            {isController ? 'Analyzes difficulty & allocates resources' : 'Executes deep reasoning request'}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  );
                }

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="relative pl-8 border-l-2 border-slate-800 ml-4"
                  >
                    <div className={`absolute left-[-9px] top-2 w-4 h-4 rounded-full border-4 border-slate-900 shadow-xl
                      ${step.type === 'decision' ? 'bg-purple-500' :
                        step.type === 'logic_lookup' ? 'bg-blue-500' :
                          step.type === 'milestone' ? 'bg-green-500' :
                            step.type === 'alert' ? 'bg-yellow-500' : 'bg-slate-600'}`}
                    />

                    <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800 hover:border-slate-700 transition-colors shadow-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-bold text-slate-500 tracking-wider uppercase">{step.step.replace(/_/g, " ")}</span>
                        {step.timestamp && <span className="text-xs text-slate-600 font-mono">{new Date(step.timestamp * 1000).toLocaleTimeString().split(' ')[0]}</span>}
                      </div>

                      <p className="text-slate-200 font-medium text-lg leading-relaxed">
                        {step.message}
                      </p>

                      {/* render details if present */}
                      {step.details && (
                        <div className="mt-4 bg-slate-950/50 rounded-lg p-4 font-mono text-xs text-blue-300/90 border border-slate-800/50 overflow-x-auto">
                          {Object.entries(step.details).map(([k, v]) => (
                            <div key={k} className="flex gap-2 mb-1 last:mb-0">
                              <span className="text-slate-500">{k}:</span>
                              <span className="text-slate-300">{typeof v === 'object' ? JSON.stringify(v) : v}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* render milestone tags */}
                      {step.data && step.type === 'milestone' && (
                        <div className="mt-4 flex flex-wrap gap-2">
                          <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-xs font-bold border border-green-500/20">
                            {step.data.budget_label.toUpperCase()} BUDGET
                          </span>
                          <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-400 text-xs border border-slate-700">
                            {step.data.paths} Path(s)
                          </span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
            <div ref={bottomRef} className="pb-8" />

            {steps.length === 0 && !isProcessing && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-700 opacity-40 pointer-events-none">
                <Brain size={64} className="mb-4 text-slate-800" />
                <p className="text-lg">Waiting for simulation trigger...</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
