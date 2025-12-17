import React, { useState, useEffect } from "react";
import "./App.css";
import { apiCall, fetchProjects, fetchProjectDetails, saveProjectToDB } from "./api";

function App() {
  // --- VIEW STATE ---
  const [view, setView] = useState("dashboard"); // 'dashboard' or 'editor'
  const [projectList, setProjectList] = useState([]);
  
  // --- PROJECT STATE ---
  const [projectId, setProjectId] = useState(null); // Database ID
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [step, setStep] = useState(1);

  // --- STORY DATA ---
  const [ideas, setIdeas] = useState([]);
  const [selectedIdea, setSelectedIdea] = useState(null); 
  const [beats, setBeats] = useState([]);
  const [structure, setStructure] = useState(null);
  const [allScenes, setAllScenes] = useState({ hook: [], mid: [], end: [] });
  const [activeSection, setActiveSection] = useState("hook");
  const [dialogue, setDialogue] = useState([]);
  const [selectedSceneContent, setSelectedSceneContent] = useState(null);

  // --- 1. DASHBOARD LOGIC ---
  useEffect(() => {
    if (view === "dashboard") {
      loadProjects();
    }
  }, [view]);

  const loadProjects = async () => {
    setLoading(true);
    const data = await fetchProjects();
    if (data) setProjectList(data);
    setLoading(false);
  };

  const handleCreateNew = () => {
    // Clear everything for a fresh start
    setProjectId(null);
    setSelectedIdea(null);
    setIdeas([]);
    setBeats([]);
    setStructure(null);
    setAllScenes({ hook: [], mid: [], end: [] });
    setDialogue([]);
    setStep(1);
    setView("editor");
  };

  const handleLoadProject = async (id) => {
    setLoading(true);
    const project = await fetchProjectDetails(id);
    if (project) {
      setProjectId(project.id);
      
      // RESTORE STATE FROM JSON BLOB
      const data = project.story_data; 
      // Safe defaults in case data is missing
      setSelectedIdea(data.selected_idea || null);
      setIdeas(data.ideas || []);
      setBeats(data.beats || []);
      setStructure(data.structure || null);
      setAllScenes(data.all_scenes || { hook: [], mid: [], end: [] });
      setDialogue(data.dialogue || []);
      
      // Figure out which step to jump to
      if (data.dialogue?.length > 0) setStep(5);
      else if (data.all_scenes?.hook?.length > 0) setStep(4);
      else if (data.structure) setStep(3);
      else if (data.beats?.length > 0) setStep(2);
      else setStep(1);

      setView("editor");
    }
    setLoading(false);
  };

  // --- 2. SAVE LOGIC ---
  const handleSave = async () => {
    if (!selectedIdea) return alert("Generate an idea first!");
    setLoading(true);
    
    // Construct the JSON Blob (The "Story Bible")
    const storyState = {
      selected_idea: selectedIdea,
      ideas: ideas,
      beats: beats,
      structure: structure,
      all_scenes: allScenes,
      dialogue: dialogue
    };

    const res = await saveProjectToDB({
      project_id: projectId,
      title: selectedIdea.title,
      story_data: storyState
    });

    if (res) {
      setProjectId(res.project_id); // Update ID so future saves are Updates, not Creates
      alert("Project Saved!");
    }
    setLoading(false);
  };


  // --- 3. EXISTING AI GENERATORS ---
  const handleGenerateIdeas = async () => {
    setLoading(true);
    const payload = {
      topic: selectedIdea ? "" : "Sci-Fi Thriller", 
      feedback: feedback,
      current_ideas: selectedIdea || null, 
      current_generated_ideas: (!selectedIdea && ideas.length > 0) ? ideas : [] 
    };
    const res = await apiCall("/generate/ideas", payload);
    if (res) {
      setIdeas(res.ideas);
      setFeedback(""); 
      if (!selectedIdea) setSelectedIdea(null);
    }
    setLoading(false);
  };

  const handleGenerateBeats = async () => {
    if (!selectedIdea) return;
    setLoading(true);
    const res = await apiCall("/generate/beats", {
      title: selectedIdea.title,
      idea: selectedIdea.idea, 
      feedback: feedback,
      current_beats: beats.length > 0 ? beats : null
    });
    if (res) setBeats(res.beats);
    setLoading(false);
    setFeedback("");
  };

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

  const handleGenerateScenes = async () => {
    setLoading(true);
    const segment = structure[activeSection]; 
    if (!segment || segment.length === 0) {
      alert(`No structure found for ${activeSection}!`);
      setLoading(false); return;
    }
    const res = await apiCall("/generate/scenes", {
      title: selectedIdea.title,
      structure_segment: JSON.stringify(segment), 
      current_section_name: activeSection,        
      feedback: feedback,
      current_scenes: allScenes[activeSection].length > 0 ? allScenes[activeSection] : null
    });
    if (res) {
      setAllScenes(prev => ({ ...prev, [activeSection]: res.scenes }));
    }
    setLoading(false);
    setFeedback("");
  };

  const handleGenerateDialogue = async () => {
    if (!selectedSceneContent) return;
    setLoading(true);
    const res = await apiCall("/generate/dialogue", {
      scene_content: selectedSceneContent,
      characters: ["Hero", "Villain"],
      feedback: feedback,
      current_dialogue: dialogue.length > 0 ? dialogue : null
    });
    if (res) setDialogue(res.dialogue);
    setLoading(false);
    setFeedback("");
  };


  // --- RENDER ---
  if (view === "dashboard") {
    return (
      <div className="app-container">
        <header><h1>Story Forge Dashboard</h1></header>
        <main>
            <button className="lg-btn" onClick={handleCreateNew}>+ Create New Story</button>
            <div className="project-list">
              {loading && <p>Loading projects...</p>}
              {!loading && projectList.map(p => (
                 <div key={p.id} className="project-card" onClick={() => handleLoadProject(p.id)}>
                    <h3>{p.title}</h3>
                    <p>Last edited: {new Date(p.updated_at).toLocaleString()}</p>
                 </div>
              ))}
            </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="editor-header">
        <button onClick={() => setView("dashboard")}>&larr; Back</button>
        <h1>Story Forge: {selectedIdea?.title || "Untitled"}</h1>
        <button className="save-btn" onClick={handleSave} disabled={loading}>
            {loading ? "Saving..." : "💾 Save Project"}
        </button>
      </header>
      
      {/* STEPS NAVIGATION */}
      <div className="steps">
          {[1,2,3,4,5].map(n => (
              <button key={n} className={step === n ? "active" : ""} onClick={()=>setStep(n)}>Step {n}</button>
          ))}
      </div>

      <main>
        {/* STEP 1: IDEAS */}
        {step === 1 && (
          <div className="stage">
            <h2>Step 1: Brainstorm Ideas</h2>
            <div className="cards-container">
              {ideas.map((item, idx) => (
                <div key={idx} className={`card ${selectedIdea === item ? "selected" : ""}`}
                     onClick={() => setSelectedIdea(selectedIdea === item ? null : item)}>
                  <h3>{item.title}</h3>
                  <p>{item.idea}</p>
                </div>
              ))}
            </div>
            <div className="controls">
              <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="Topic or Feedback..." />
              <button onClick={handleGenerateIdeas} disabled={loading}>
                {selectedIdea ? "Refine Selected" : "Generate / Reroll"}
              </button>
              {selectedIdea && (
                <button className="next-btn" onClick={() => setStep(2)}>Next: Beats &rarr;</button>
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
              {beats.length > 0 && <button className="next-btn" onClick={() => setStep(3)}>Next &rarr;</button>}
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
              <button onClick={handleGenerateStructure} disabled={loading}>Generate Structure</button>
              {structure && <button className="next-btn" onClick={() => setStep(4)}>Next &rarr;</button>}
            </div>
          </div>
        )}

        {/* STEP 4: SCENES */}
        {step === 4 && (
          <div className="stage">
            <h2>Scenes</h2>
            <div className="tabs">
              {['hook', 'mid', 'end'].map(sec => (
                <button key={sec} className={activeSection === sec ? "tab active" : "tab"}
                        onClick={() => setActiveSection(sec)}>{sec.toUpperCase()}</button>
              ))}
            </div>
            <div className="list-view">
              {allScenes[activeSection].length === 0 ? <p>No scenes generated for {activeSection} yet.</p> :
                allScenes[activeSection].map((s, i) => (
                  <div key={i} className="list-item scene-item">
                    <div style={{flex: 1}}><strong>Scene {i+1}:</strong> {s}</div>
                    <button className="sm-btn" onClick={() => {
                      setSelectedSceneContent(s);
                      setDialogue([]); 
                      setStep(5);
                    }}>Write Dialogue &rarr;</button>
                  </div>
                ))
              }
            </div>
            <div className="controls">
              <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder={`Feedback for ${activeSection}...`} />
              <button onClick={handleGenerateScenes} disabled={loading}>Generate Scenes</button>
            </div>
          </div>
        )}

        {/* STEP 5: DIALOGUE */}
        {step === 5 && (
          <div className="stage">
            <h2>Dialogue Editor</h2>
            <button className="sm-btn" style={{marginBottom: '10px'}} onClick={() => setStep(4)}>&larr; Back to Scenes</button>
            <div className="context-box"><strong>Current Scene:</strong><p>{selectedSceneContent}</p></div>
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
               <input value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="Feedback..." />
               <button onClick={handleGenerateDialogue} disabled={loading}>
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