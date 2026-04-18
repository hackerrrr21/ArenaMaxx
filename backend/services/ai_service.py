import os
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
from .monitoring import log_event

# 1. Define Tools for the AI
# These functions allow Gemini to "act" in the stadium environment.

check_seat_declaration = FunctionDeclaration(
    name="check_seat_availability",
    description="Check if a specific seat or section is available for booking",
    parameters={
        "type": "object",
        "properties": {
            "section": {"type": "string", "description": "The stadium section (e.g., North, VIP)"},
            "row": {"type": "string", "description": "The row letter"},
            "seat_number": {"type": "integer", "description": "The seat number"}
        },
        "required": ["section"]
    }
)

get_wait_time_declaration = FunctionDeclaration(
    name="get_facility_wait_time",
    description="Get real-time wait times for washrooms or concessions",
    parameters={
        "type": "object",
        "properties": {
            "facility_type": {"type": "string", "enum": ["washroom", "food", "entrance"]},
            "block": {"type": "string", "description": "The stadium block/zone"}
        },
        "required": ["facility_type"]
    }
)

stadium_tools = Tool(
    function_declarations=[check_seat_declaration, get_wait_time_declaration]
)

class AIService:
    """
    Agentic AI Concierge powered by Google Vertex AI.
    Implements Function Calling to bridge Generative AI with stadium systems.
    """
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'arenamaxx')
        self.location = 'us-central1'
        self.model_name = "gemini-1.5-flash-002"
        self._init_vertex()

    def _init_vertex(self):
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(
                self.model_name,
                system_instruction="You are Maxx, the ArenaMaxx Stadium Concierge. You help fans with navigation, food, and seating. Be proactive and helpful. Use your tools to provide accurate live data."
            )
        except Exception as e:
            self.model = None
            log_event(f"Vertex AI Init Failed: {e}", severity='WARNING')

    def process_chat(self, user_id, message):
        """
        Handles user chat with automated tool calling.
        """
        if not self.model:
            return "Concierge is offline. Please check back later."

        chat = self.model.start_chat()
        
        try:
            # First response from model (may contain tool call)
            response = chat.send_message(message, tools=[stadium_tools])
            
            # Extract function calls
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    # Handle Tool Call
                    result = self._dispatch_tool(part.function_call)
                    
                    # Return result to model for final interpretation
                    response = chat.send_message(
                        Part.from_function_response(
                            name=part.function_call.name,
                            response={"content": result}
                        )
                    )
            
            return response.text
        except Exception as e:
            log_event(f"Chat processing error: {e}", severity='ERROR')
            return "I'm having trouble connecting to stadium services. How else can I help?"

    def _dispatch_tool(self, function_call):
        """
        Executes the backend logic requested by the AI.
        """
        name = function_call.name
        args = dict(function_call.args)
        
        if name == "check_seat_availability":
            # Mock logic linked to future Repository
            return f"Section {args.get('section')} has 15% availability in Row A."
        
        if name == "get_facility_wait_time":
            # Mock logic linked to Simulation engine
            return f"The {args.get('facility_type')} wait time in {args.get('block', 'your area')} is currently 4 minutes."
        
        return "Service temporarily unavailable."

# Singleton
ai_service = AIService()
