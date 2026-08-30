import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.agents.tools import lore_rag_tool

load_dotenv()

# We will use the cheaper/faster model for evaluation as well, or the larger one if accuracy is paramount.
# We'll use the larger model for evaluation to ensure high fidelity reasoning.
EVAL_MODEL = os.getenv("LLM_MODEL_LARGE", "openai/gpt-oss-120b")

llm = ChatGroq(model=EVAL_MODEL, temperature=0)

EVAL_PROMPT = """You are an expert lore-consistency evaluator. 
Your task is to compare a Generated Script against the official Lorebook (Context) and determine if the script hallucinates any details or contradicts the lore.

<Lorebook Context>
{context}
</Lorebook Context>

<Generated Script>
{script}
</Generated Script>

Evaluate the script for hallucinations. A hallucination is when the script invents character traits, background facts, or technological details not present in the lorebook, OR when it directly contradicts the lorebook.
(Note: Dialogue itself is not a hallucination, it is expected to be generated. Hallucinations are factual lore inaccuracies).

Return a JSON object with two fields:
1. "score": A float between 0.0 and 1.0, where 1.0 means PERFECT consistency (no hallucinations) and 0.0 means SEVERE hallucinations.
2. "reasoning": A brief explanation of your score, pointing out any specific hallucinations if they exist.

Respond ONLY with valid JSON. Do not include markdown formatting or extra text.
"""

def run_evaluation():
    # 1. Retrieve the actual lore context from Qdrant for our test characters
    print("Retrieving lore context from Qdrant...")
    lore_aris = lore_rag_tool.invoke("Dr. Aris")
    lore_vance = lore_rag_tool.invoke("Captain Vance")
    context = f"--- Dr. Aris ---\n{lore_aris}\n\n--- Captain Vance ---\n{lore_vance}"
    
    # 2. Define a generated script to evaluate. 
    # This is a sample output of what our agent actually generates.
    sample_script = {
        "lines": [
            {"speaker": "NARRATOR", "text": "Dr. Aris examined the core, his eyes scanning the intricate mechanisms with meticulous care.", "emotion": "focused"},
            {"speaker": "NARRATOR", "text": "Captain Vance stormed into the area, his face flushed with fury as he prepared to confront the situation.", "emotion": "angry"}
        ]
    }
    script_str = json.dumps(sample_script, indent=2)
    
    print("\nRunning Evaluator LLM...")
    prompt = PromptTemplate.from_template(EVAL_PROMPT)
    chain = prompt | llm
    
    response = chain.invoke({"context": context, "script": script_str})
    
    try:
        # Parse the JSON response
        result = json.loads(response.content)
        print("\n=== Evaluation Results ===")
        print(f"Score: {result.get('score')}")
        print(f"Reasoning: {result.get('reasoning')}")
    except json.JSONDecodeError:
        print("\nFailed to parse LLM response as JSON:")
        print(response.content)

if __name__ == "__main__":
    run_evaluation()
