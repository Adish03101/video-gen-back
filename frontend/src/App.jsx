import React, { useState } from "react";
import "./App.css";
import { apiCall } from "./api";

function App() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState("");

  // --- DATA STATE ---
  const [ideas, setIdeas] = useState([]);
  const [selectedIdea, setSelectedIdea] = useState(null); // { title: "", idea: "" }
  
  const [beats, setBeats] = useState([]);
  const [structure, setStructure] = useState(null); // { hook: [], mid: [], end: [] }
  
  // SCENES: stored by section so we don't lose them when switching tabs
  const [allScenes, setAllScenes] = useState({ hook: [], mid: [], end: [] });
  const [activeSection, setActiveSection] = useState("hook"); // 'hook', 'mid', 'end'
  
  // DIALOGUE
  const [selectedSceneContent, setSelectedSceneContent] = useState(null);
  const [dialogue, setDialogue] = useState([]);

  // ==========================
  // STEP 1: IDEAS
  // ==========================
  const handleGenerateIdeas = async () => {
    setLoading(true);
    const payload = {
      topic: selectedIdea ? "" : "Sci-Fi Thriller", // Default topic if empty
      feedback: feedback,
      // If editing, send the selected idea
      current_ideas: selectedIdea || null, 
      // If rerolling, send previous list
      current_generated_ideas: (!selectedIdea && ideas.length > 0) ? ideas : [] 
    };

    const res = await apiCall("/generate/ideas", payload);
    if (res) {
      setIdeas(res.ideas);
      setFeedback(""); 
      // Only clear selection if we are rerolling (not editing specific)
      if (!selectedIdea) setSelectedIdea(null);
    }
    setLoading(false);
  };

  // ==========================
  // STEP 2: BEATS
  // ==========================
  const handleGenerateBeats = async () => {
    if (!selectedIdea) return;
    setLoading(true);
    
    const res = await apiCall("/generate/beats", {
      title: selectedIdea.title,
      idea: selectedIdea.idea, // Uses the 'idea' key
      feedback: feedback,
      current_beats: beats.length > 0 ? beats : null
    });

    if (res) setBeats(res.beats);
    setLoading(false);
    setFeedback("");
  };

  // ==========================
  // STEP 3: STRUCTURE
  // ==========================
  const handleGenerateStructure = async () => {
    setLoading(true);
    const res = await apiCall("/generate/structure", {
      title: selectedIdea.title,
      beats: beats,
      feedback: feedback,
      current_structure: structure
    });
    if (res) setStructure(res.structure);
    setLoading(false);
    setFeedback("");
  };

  // ==========================
  // STEP 4: SCENES (With Tabs)
  // ==========================
  const handleGenerateScenes = async () => {
    setLoading(true);
    
    // 1. Get the structure segment for the active tab (Hook/Mid/End)
    const segment = structure[activeSection]; 
    if (!segment || segment.length === 0) {
      alert(`No structure found for ${activeSection}! Generate structure first.`);
      setLoading(false);
      return;
    }

    // 2. Call API
    const res = await apiCall("/generate/scenes", {
      title: selectedIdea.title,
      structure_segment: JSON.stringify(segment), // Pass the list as text
      current_section_name: activeSection,        // Tell Backend which part this is
      feedback: feedback,
      current_scenes: allScenes[activeSection].length > 0 ? allScenes[activeSection] : null
    });
    
    // 3. Save result into the specific tab bucket
    if (res) {
      setAllScenes(prev => ({
        ...prev,
        [activeSection]: res.scenes
      }));
    }
    setLoading(false);
    setFeedback("");
  };

  // ==========================
  // STEP 5: DIALOGUE
  // ==========================
  const handleGenerateDialogue = async () => {
    if (!selectedSceneContent) return;
    setLoading(true);

    const res = await apiCall("/generate/dialogue", {
      scene_content: selectedSceneContent,
      characters: ["Hero", "Villain"], // Hardcoded for prototype
      feedback: feedback,
      current_dialogue: dialogue.length > 0 ? dialogue : null
    });

    if (res) setDialogue(res.dialogue);
    setLoading(false);
    setFeedback("");
  };

  // --- RENDER ---
  return (
    <div className="app-container">
      <header>
        <h1>Story Forge AI</h1>
        <div className="steps">
          <button className={step === 1 ? "active" : ""} onClick={()=>setStep(1)}>1. Ideas</button>
          <button className={step === 2 ? "active" : ""} onClick={()=>setStep(2)}>2. Beats</button>
          <button className={step === 3 ? "active" : ""} onClick={()=>setStep(3)}>3. Structure</button>
          <button className={step === 4 ? "active" : ""} onClick={()=>setStep(4)}>4. Scenes</button>
          <button className={step === 5 ? "active" : ""} onClick={()=>setStep(5)}>5. Dialogue</button>
        </div>
      </header>

      <main>
        {/* STEP 1: IDEAS */}
        {step === 1 && (
          <div className="stage">
            <h2>Step 1: Brainstorm Ideas</h2>
            
            {/* Input only visible if no idea selected yet (optional, or keep always) */}
            <div className="input-group">
               {/* Hidden for cleaner UI if selecting, but you can keep it */}
            </div>

            <div className="cards-container">
              {ideas.map((item, idx) => (
                <div 
                  key={idx} 
                  className={`card ${selectedIdea === item ? "selected" : ""}`}
                  onClick={() => setSelectedIdea(selectedIdea === item ? null : item)}
                >
                  <h3>{item.title}</h3>
                  <p>{item.idea}</p>
                </div>
              ))}
            </div>

            <div className="controls">
              <input 
                value={feedback} 
                onChange={e => setFeedback(e.target.value)} 
                placeholder="Topic or Feedback..." 
              />
              
              {/* Generate / Refine Button */}
              <button onClick={handleGenerateIdeas} disabled={loading}>
                {selectedIdea ? "Refine Selected" : "Generate / Reroll"}
              </button>
              
              {/* NEXT BUTTON: Only shows if an Idea is Selected */}
              {selectedIdea && (
                <button className="next-btn" onClick={() => setStep(2)}>
                  Next: Beats &rarr;
                </button>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: BEATS */}
        {step === 2 && (
          <div className="stage">
            <h2>Story Beats</h2>
            <div className="list-view">
              {beats.map((b, i) => <div key={i} className="list-item"><strong>{i+1}.</strong> {b}</div>)}
            </div>
            <div className="controls">
              <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="Feedback..." />
              <button onClick={handleGenerateBeats} disabled={loading}>
                  {beats.length > 0 ? "Regenerate / Fix" : "Generate Beats"}
              </button>
              
              {beats.length > 0 && (
                <button className="next-btn" onClick={() => setStep(3)}>Next: Structure &rarr;</button>
              )}
            </div>
          </div>
        )}

        {/* STEP 3: STRUCTURE */}
        {step === 3 && (
          <div className="stage">
            <h2>Structure</h2>
            <div className="columns">
              <div className="col"><h3>Hook</h3>{structure?.hook?.map((s, i) => <p key={i}>- {s}</p>)}</div>
              <div className="col"><h3>Mid</h3>{structure?.mid?.map((s, i) => <p key={i}>- {s}</p>)}</div>
              <div className="col"><h3>End</h3>{structure?.end?.map((s, i) => <p key={i}>- {s}</p>)}</div>
            </div>
            <div className="controls">
              <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="Feedback..." />
              <button onClick={handleGenerateStructure} disabled={loading}>
                  {structure ? "Refine Structure" : "Generate Structure"}
              </button>
              
              {structure && (
                <button className="next-btn" onClick={() => setStep(4)}>Next: Scenes &rarr;</button>
              )}
            </div>
          </div>
        )}

        {/* STEP 4: SCENES */}
        {step === 4 && (
          <div className="stage">
            <h2>Scenes</h2>
            
            {/* TABS */}
            <div className="tabs">
              {['hook', 'mid', 'end'].map(sec => (
                <button 
                  key={sec} 
                  className={activeSection === sec ? "tab active" : "tab"}
                  onClick={() => setActiveSection(sec)}
                >
                  {sec.toUpperCase()}
                </button>
              ))}
            </div>

            <div className="list-view">
              {allScenes[activeSection].length === 0 ? <p>No scenes generated for {activeSection} yet.</p> :
                allScenes[activeSection].map((s, i) => (
                  <div key={i} className="list-item scene-item">
                    <div style={{flex: 1}}><strong>Scene {i+1}:</strong> {s}</div>
                    <button className="sm-btn" onClick={() => {
                      setSelectedSceneContent(s);
                      setStep(5);
                    }}>Write Dialogue &rarr;</button>
                  </div>
                ))
              }
            </div>
            <div className="controls">
              <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder={`Feedback for ${activeSection} scenes...`} />
              <button onClick={handleGenerateScenes} disabled={loading}>
                 Generate {activeSection.toUpperCase()} Scenes
              </button>
            </div>
          </div>
        )}

        {/* STEP 5: DIALOGUE */}
        {step === 5 && (
          <div className="stage">
            <h2>Dialogue Editor</h2>
            <button className="sm-btn" style={{marginBottom: '10px'}} onClick={() => setStep(4)}>&larr; Back to Scenes</button>
            
            <div className="context-box">
              <strong>Current Scene Context:</strong>
              <p>{selectedSceneContent || "No scene selected."}</p>
            </div>

            <div className="script-view">
              {dialogue.map((line, i) => (
                <div key={i} className="script-line">
                  <strong className="char-name">{line.character}</strong>
                  {line.parenthetical && <span className="parenthetical"> ({line.parenthetical})</span>}
                  <p className="dialogue-text">{line.text}</p>
                </div>
              ))}
            </div>

            <div className="controls">
               <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="Feedback (e.g. 'Make it funnier')..." />
               <button onClick={handleGenerateDialogue} disabled={loading || !selectedSceneContent}>
                 {dialogue.length > 0 ? "Refine Dialogue" : "Write Script"}
               </button>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;