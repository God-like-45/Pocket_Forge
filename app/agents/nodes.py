from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.state import AgentState
from app.agents.llm import director_llm, scriptwriter_llm, reviewer_llm
from app.agents.tools import lore_rag_tool
from app.schemas.script import Script

def director_node(state: AgentState) -> AgentState:
    """Analyzes the text and breaks down who is speaking."""
    
    sys_msg = SystemMessage(
        content=(
            "You are a Director. Read the chapter text and identify all characters who appear or speak. "
            "Output a brief summary of the scene and a list of characters present."
        )
    )
    
    human_msg = HumanMessage(content=f"Chapter Text:\n{state['chapter_text']}")
    
    response = director_llm.invoke([sys_msg, human_msg])
    
    # We always return a dict that will be merged into the state
    return {"director_breakdown": response.content, "revision_count": state.get("revision_count", 0)}

def scriptwriter_node(state: AgentState) -> AgentState:
    """Writes the script using the Lore RAG tool and structured output."""
    
    # Bind the tool to the LLM so it can query Qdrant
    llm_with_tools = scriptwriter_llm.bind_tools([lore_rag_tool])
    
    # We want structured output for the final script
    structured_llm = scriptwriter_llm.with_structured_output(Script)
    
    sys_msg = SystemMessage(
        content=(
            "You are a Script Writer adapting a novel chapter into an audio drama script.\n"
            "You must format your response exactly matching the provided JSON schema.\n"
            "First, use the `lore_rag_tool` to look up any character mentioned in the Director's breakdown "
            "to ensure their personality and voice tone are accurate in your script.\n"
            "Translate all narrative text into 'NARRATOR' lines, and dialogue into character lines.\n"
            "Include an appropriate emotional tone for each line."
        )
    )
    
    # Include previous feedback if any
    feedback_text = f"\n\nReviewer Feedback to incorporate:\n{state.get('feedback', '')}" if state.get('feedback') else ""
    
    human_msg = HumanMessage(
        content=(
            f"Director Breakdown:\n{state['director_breakdown']}\n\n"
            f"Chapter Text:\n{state['chapter_text']}"
            f"{feedback_text}"
        )
    )
    
    # First, let the LLM use tools if needed (a simple manual implementation instead of a full ToolNode for now,
    # or we can use Langchain's built-in tool calling capabilities.)
    # Note: To keep the graph simple and predictable for this phase, we'll invoke the tool manually if the LLM requests it,
    # or we can just let it generate the script.
    # Actually, a better approach for structured output WITH tools is an AgentExecutor or just letting it run.
    # For simplicity, we'll prompt it to use tools, but since we are using `with_structured_output`, 
    # it might conflict with standard tool calling.
    
    # We'll split it: 
    # 1. Ask LLM to gather lore (using tools)
    # 2. Ask LLM to generate script
    
    gather_sys = SystemMessage(content="You are an assistant gathering character lore. Use the lore_rag_tool to look up characters.")
    gather_resp = llm_with_tools.invoke([gather_sys, human_msg])
    
    lore_context = ""
    if gather_resp.tool_calls:
        # For each tool call, execute it
        for tool_call in gather_resp.tool_calls:
            if tool_call['name'] == 'lore_rag_tool':
                char_name = tool_call['args'].get('character_name', '')
                if char_name:
                    lore_result = lore_rag_tool.invoke({"character_name": char_name})
                    lore_context += f"\nLore for {char_name}:\n{lore_result}\n"
    
    # Now generate the script with the lore context
    script_sys = SystemMessage(
        content=(
            "You are a Script Writer adapting a novel chapter into an audio drama script.\n"
            "You must format your response exactly matching the provided JSON schema.\n"
            "Translate all narrative text into 'NARRATOR' lines, and dialogue into character lines.\n"
            "Include an appropriate emotional tone for each line. "
            "Select an overall `bgm_track` for the scene ('tense', 'action', or 'calm') based on the general mood.\n"
            "If a specific sound effect occurs exactly at the start of a line (e.g., an alarm blaring, a door opening, an explosion), set the `sfx` field to a simple string like 'alarm', 'door', 'laser', or 'explosion'. Otherwise, omit it.\n"
            "Use the provided Character Lore to ensure accuracy."
        )
    )
    
    script_human = HumanMessage(
        content=(
            f"Character Lore:\n{lore_context}\n\n"
            f"Director Breakdown:\n{state['director_breakdown']}\n\n"
            f"Chapter Text:\n{state['chapter_text']}"
            f"{feedback_text}"
        )
    )
    
    final_script = structured_llm.invoke([script_sys, script_human])
    
    return {"script": final_script}

def reviewer_node(state: AgentState) -> AgentState:
    """Reviews the script for formatting and completeness."""
    
    script = state.get('script')
    if not script or not script.lines:
        return {"feedback": "The script is empty. Please generate a full script.", "revision_count": state.get("revision_count", 0) + 1}
        
    sys_msg = SystemMessage(
        content=(
            "You are a Script Reviewer. Review the provided JSON script.\n"
            "Check for: \n"
            "1. Proper use of 'NARRATOR' for non-dialogue.\n"
            "2. Ensure emotions are descriptive.\n"
            "3. Ensure no dialogue is lost from the original text.\n"
            "If it looks good, reply exactly with the word 'PASS'.\n"
            "Otherwise, provide specific feedback on what needs to be fixed."
        )
    )
    
    script_str = "\n".join([f"[{line.speaker} - {line.emotion}] {line.text}" for line in script.lines])
    
    human_msg = HumanMessage(
        content=f"Original Text:\n{state['chapter_text']}\n\nGenerated Script:\n{script_str}"
    )
    
    response = reviewer_llm.invoke([sys_msg, human_msg])
    
    if response.content.strip() == "PASS":
        return {"feedback": "PASS"}
    else:
        return {"feedback": response.content, "revision_count": state.get("revision_count", 0) + 1}
