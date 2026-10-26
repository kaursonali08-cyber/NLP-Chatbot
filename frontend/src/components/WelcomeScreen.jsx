import { Sparkles } from 'lucide-react';
const prompts=['Explain machine learning.','Help me learn Python.','What is natural language processing?','Tell me something interesting.'];
export default function WelcomeScreen({onPrompt}) { return <section className="welcome"><div className="welcome-icon"><Sparkles size={30}/></div><h1>Welcome to ConversaAI</h1><p>Your intelligent NLP-powered conversational assistant.</p><div className="prompts">{prompts.map(p=><button key={p} onClick={()=>onPrompt(p)}>{p}</button>)}</div></section> }
