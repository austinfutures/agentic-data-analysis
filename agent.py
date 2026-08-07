"""
Agentic Data Analysis Loop
A sophisticated agent that accepts high-level data analysis queries and autonomously
executes them with Gemini and Pandas.
"""

import os
import json
import pandas as pd
import traceback
from typing import Optional
from google import genai

class DataAnalysisAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """Initialize the data analysis agent with Google Gemini."""
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable or api_key parameter is required.")
            
        self.client = genai.Client(api_key=key)
        # Using a widely supported Flash model ID
        self.model = model
        self.dataframe: Optional[pd.DataFrame] = None
        self.execution_history: list[dict] = []
        self.error_logs: list[dict] = []
        
    def load_data(self, data_source: str | pd.DataFrame) -> None:
        """Load data from CSV file or accept a pandas DataFrame."""
        if isinstance(data_source, pd.DataFrame):
            self.dataframe = data_source.copy()
        else:
            self.dataframe = pd.read_csv(data_source)
        print(f"✓ Loaded data with shape: {self.dataframe.shape}")
        print(f"✓ Columns: {list(self.dataframe.columns)}\n")
        
    def _build_system_prompt(self) -> str:
        """Build the system prompt with dataframe context."""
        return f"""You are an expert data analyst assistant. Your job is to help users analyze data using Python and Pandas.

CURRENT DATAFRAME INFO:
- Shape: {self.dataframe.shape}
- Columns: {list(self.dataframe.columns)}
- Data types: {self.dataframe.dtypes.to_dict()}
- First few rows:
{self.dataframe.head().to_string()}

EXECUTION RULES:
1. You will receive a data analysis query from the user
2. Break it down into clear, logical steps
3. Generate ONLY valid Python code that uses Pandas to accomplish the task
4. Wrap your Python code in <code> tags
5. The code will be executed with: df = self.dataframe (the current DataFrame)
6. Your code should print results and assign important results to 'result' variable
7. If there's an error, you'll receive the traceback and must provide corrected code
8. Be concise - write efficient Pandas code, not verbose explanations in code comments

IMPORTANT:
- Do NOT import pandas or numpy - they're already available as pd and np
- Do NOT read or write files - work only with the in-memory DataFrame
- Do NOT use display() - use print() for output
- All output must be via print() statements
"""

    def execute_query(self, user_query: str, max_iterations: int = 3) -> str:
        """Execute a data analysis query with self-correction capability."""
        if self.dataframe is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        print(f"Query: {user_query}\n")
        print("=" * 60)
        
        # Build prompt history manually for Gemini
        conversation_history = f"User Query: {user_query}\n"
        
        for iteration in range(max_iterations):
            code = ""  # Pre-initialize variable so exception logging won't fail
            try:
                full_prompt = f"{self._build_system_prompt()}\n\n{conversation_history}"
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                )
                
                assistant_message = response.text
                
                if "<code>" not in assistant_message:
                    return f"Agent response (iteration {iteration + 1}):\n{assistant_message}"
                
                code_start = assistant_message.find("<code>") + 6
                code_end = assistant_message.find("</code>")
                code = assistant_message[code_start:code_end].strip()
                
                if code.startswith("python"):
                    code = code[6:]
                code = code.strip()
                
                print(f"Iteration {iteration + 1} - Executing code:")
                print("-" * 60)
                print(code)
                print("-" * 60)
                
                local_scope = {
                    'df': self.dataframe,
                    'pd': pd,
                    'np': __import__('numpy')
                }
                exec(code, local_scope)
                
                execution_entry = {
                    'iteration': iteration + 1,
                    'code': code,
                    'status': 'success'
                }
                self.execution_history.append(execution_entry)
                
                print(f"\n✓ Code executed successfully!\n")
                return "Analysis complete"
                
            except Exception as e:
                error_trace = traceback.format_exc()
                print(f"✗ Error on iteration {iteration + 1}:")
                print(error_trace)
                
                error_entry = {
                    'iteration': iteration + 1,
                    'error': str(e),
                    'traceback': error_trace
                }
                self.error_logs.append(error_entry)
                
                conversation_history += f"\nAttempted Code:\n{code}\nExecution Error:\n{error_trace}\nPlease fix the code and try again.\n"
                
                if iteration == max_iterations - 1:
                    return f"Failed after {max_iterations} attempts. Last error:\n{error_trace}"
                    
        return "Query processing complete"

    def get_context_summary(self) -> dict:
        """Return summary of execution context."""
        return {
            'total_executions': len(self.execution_history),
            'total_errors': len(self.error_logs),
            'dataframe_shape': self.dataframe.shape if self.dataframe is not None else None,
            'execution_history': self.execution_history,
            'error_history': self.error_logs
        }

    def interactive_session(self) -> None:
        """Start an interactive query session."""
        print("🤖 Data Analysis Agent - Interactive Mode (Powered by Gemini)")
        print("=" * 60)
        print(f"Loaded data: {self.dataframe.shape[0]} rows × {self.dataframe.shape[1]} columns")
        print("Type 'quit' to exit, 'info' for dataframe info, 'history' to see execution history\n")
        
        while True:
            user_input = input("📊 Your query: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'info':
                print(self.dataframe.info())
                continue
            elif user_input.lower() == 'history':
                summary = self.get_context_summary()
                print(json.dumps(summary, indent=2, default=str))
                continue
            elif not user_input:
                continue
            
            result = self.execute_query(user_input)
            print(f"Result: {result}\n")
