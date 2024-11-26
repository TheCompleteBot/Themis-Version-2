# app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Import existing schemas and models
from app.models.schemas import (
    ContractRequirements,
    ContractResponse,
    UserCreate,
    Token,
    User as UserSchema
)
from app.core.security import security  # Correctly import the security instance
from app.agents.user_interface_agent import UserInterfaceAgent
from app.agents.retriever_agent import RetrieverAgent
from app.agents.drafting_agent import DraftingAgent
from app.agents.correction_agent import CorrectionAgent
from app.agents.jurisdiction_agent import JurisdictionCustomizationAgent
from langgraph.graph import Graph, END
from app.dependencies import get_db
from app.models.user import User
from app.core.logger import logger
from app.core.rate_limit import limiter

# Import models for Chat and Message
from app.models.chat import Chat
from app.models.message import Message
from app.models.contract import Contract, ContractType

# Import OpenAI client
from app.core.openai_client import generate_chat_response

# Initialize APIRouter once
router = APIRouter()

# Initialize agents once
ui_agent = UserInterfaceAgent()
retriever_agent = RetrieverAgent()
drafting_agent = DraftingAgent()
correction_agent = CorrectionAgent()
jurisdiction_agent = JurisdictionCustomizationAgent()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# -----------------------------------
# 1. Authentication Endpoints
# -----------------------------------

@router.post("/auth/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = security.get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = security.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Log the incoming login request
        logger.info(f"Login attempt for username: {form_data.username}")
        
        # Query the user from the database
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            logger.warning(f"User '{form_data.username}' not found in database.")
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Verify the password
        if not security.verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid password for user '{form_data.username}'.")
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        # Create the access token
        access_token = security.create_access_token(data={"sub": user.username})
        logger.info(f"Access token successfully created for user '{form_data.username}'.")

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        # Log unexpected errors for debugging
        logger.error(f"Unexpected error during login for user '{form_data.username}': {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your login request.")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = security.decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# -----------------------------------
# 2. Contract Generation Endpoint
# -----------------------------------

@router.post("/contracts/generate", response_model=ContractResponse)
@limiter.limit("5/minute")
@router.post("/contracts/generate", response_model=ContractResponse)
@limiter.limit("5/minute")
async def generate_contract(
    request: Request,
    requirements: ContractRequirements,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"User '{current_user.username}' initiated contract generation.")
        # Initialize state
        state = {
            "user_inputs": requirements.dict(),
            "legal_references": [],
            "contract_draft": "",
            "corrected_draft": "",
            "final_contract": "",
            "error": None,
            "completed": False
        }

        # Workflow logic (unchanged from your original code)
        def collect_user_inputs(state):
            # Print incoming state for debugging
            print("Original User Input State:", state)

            # Hardcode the `details` section
            state["user_inputs"]["details"] = {
   "prompt": """Please generate a legally binding contract. Include proper signature blocks as follows:

1. For PARTY 1:
  - Signature line
  - Printed name
  - Title/Position
  - Date
  - Company seal placement
  - Beneficiary details 
  - Witness signature and details

2. For PARTY 2:
  - Signature line
  - Printed name
  - Title/Position  
  - Date
  - Company seal placement
  - Beneficiary details
  - Witness signature and details

3. Additional Requirements:
  - Add notary section if required by jurisdiction
  - Include all relevant legal citations and references
  - Ensure compliance with local laws
  - Add page numbers in 'Page X of Y' format
  - Include version control
  - Use proper legal margins and formatting

Please maintain highest standards of legal accuracy and enforceability while generating the contract.""",

   "signature_block": "Include standard legal signature blocks with proper spacing and formatting for all parties involved"
}

            # Print updated state for debugging
            print("Updated User Input State with Hardcoded Details:", state)

            return state

        def retrieve_legal_references(state):
            logger.debug(f"User inputs before legal reference search: {state.get('user_inputs')}")
            if not state["user_inputs"]:
                logger.error("User inputs are None or invalid.")
            else:
                logger.debug(f"User inputs keys: {state['user_inputs'].keys()}")
            state["legal_references"] = retriever_agent.search_legal_reference(state["user_inputs"])
            logger.debug(f"Legal references retrieved: {state['legal_references']}")
            logger.debug(f"Legal reference search input: {state.get('user_inputs')}")
            logger.debug(f"Contract draft type before correction: {type(state['contract_draft'])}")

            return state
            
        def generate_initial_draft(state):
            state["contract_draft"] = drafting_agent.create_initial_draft(
                contract_type=state["user_inputs"]["contract_type"],
                requirements=state["user_inputs"],
                legal_refs=state["legal_references"]
            )
            logger.debug(f"Contract draft type before correction: {type(state['contract_draft'])}")

            return state

        def correct_draft(state):
            state["corrected_draft"] = correction_agent.correct_draft(state["contract_draft"])
            return state

        def customize_jurisdiction(state):
            customized = jurisdiction_agent.customize_for_jurisdiction(
                {'content': state["corrected_draft"], 'metadata': {}},
                state["user_inputs"].get('jurisdiction', 'Default Jurisdiction'),
                state["user_inputs"].get('additional_jurisdictions', []),
                requirements={'translate': False}
            )
            state["final_contract"] = customized['content'] if isinstance(customized, dict) else customized
            return state

        def should_continue(state):
            return "continue" if not state.get("error") else END

        # Workflow graph (unchanged)
        workflow = Graph()
        workflow.add_node("collect_inputs", collect_user_inputs)
        workflow.add_node("retrieve_references", retrieve_legal_references)
        workflow.add_node("generate_draft", generate_initial_draft)
        workflow.add_node("correct_draft", correct_draft)
        workflow.add_node("customize_jurisdiction", customize_jurisdiction)
        workflow.set_entry_point("collect_inputs")
        workflow.add_conditional_edges("collect_inputs", should_continue, {"continue": "retrieve_references", END: END})
        workflow.add_conditional_edges("retrieve_references", should_continue, {"continue": "generate_draft", END: END})
        workflow.add_conditional_edges("generate_draft", should_continue, {"continue": "correct_draft", END: END})
        workflow.add_conditional_edges("correct_draft", should_continue, {"continue": "customize_jurisdiction", END: END})
        workflow.add_conditional_edges("customize_jurisdiction", should_continue, {"continue": END, END: END})
        compiled_workflow = workflow.compile()

        # Execute workflow
        final_state = compiled_workflow.invoke(state)

        if final_state.get("error"):
            logger.error(f"Error during contract generation for user '{current_user.username}': {final_state['error']}")
            return ContractResponse(error=final_state["error"], completed=False)
        
        # Generate PDF
        pdf_path = ui_agent.display_final_contract(final_state["final_contract"])
        final_state["completed"] = True
        final_state["pdf_file"] = pdf_path

        # Save contract details to the database and retrieve its ID
        try:
            new_contract = Contract(
                content=final_state["final_contract"],
                user_id=current_user.id,
                title=ContractType(requirements.contract_type),  # Convert Enum to String
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(new_contract)
            print("Hellow Details of the Contracxt ; ",new_contract.content)
            db.commit()
            db.refresh(new_contract)
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database error while saving contract: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Error saving contract to database")

        logger.info(f"Contract generation completed for user '{current_user.username}', contract ID: {new_contract.id}.")
        
        # Return the response with the contract ID included
        return ContractResponse(
            final_contract=final_state["final_contract"],
            pdf_file=final_state.get("pdf_file"),
            completed=final_state["completed"],
            id=new_contract.id  # Add the contract ID here
        )

    except Exception as e:
        db.rollback()  # Ensure rollback in case of unexpected errors
        logger.error(f"Unexpected error for user '{current_user.username}': {str(e)}")
        return ContractResponse(error=str(e), completed=False)
# -----------------------------------
# 3. Chatbot Functionality
# -----------------------------------

# 3.1. Define Pydantic Schemas for Chat
class ChatRequest(BaseModel):
    contract_id: int
    message: str

class ChatResponse(BaseModel):
    response: str

class MessageSchema(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None

class ChatHistorySchema(BaseModel):
    chat_id: int
    messages: List[MessageSchema]

# 3.2. Chatbot Endpoint
@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Adjust rate limit as needed
def chat(
    request: Request,  # Added Request parameter for rate limiting
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle chat messages about a specific contract.
    """
    try:
        # Fetch the contract
        contract = db.query(Contract).filter(Contract.id == chat_request.contract_id, Contract.user_id == current_user.id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found.")
        
        # Fetch or create a chat session
        chat = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.contract_id == chat_request.contract_id).first()
        if not chat:
            chat = Chat(user_id=current_user.id, contract_id=chat_request.contract_id)
            db.add(chat)
            db.commit()
            db.refresh(chat)
        
        # Fetch conversation history
        conversation = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.timestamp).all()
        conversation_history = [{"sender": msg.sender, "content": msg.content} for msg in conversation]
        
        # Save user message
        user_message = Message(chat_id=chat.id, sender="user", content=chat_request.message)
        db.add(user_message)
        db.commit()
        
        # Generate AI response
        ai_response = generate_chat_response(chat_request.message, conversation_history)
        
        # Save AI response
        bot_message = Message(chat_id=chat.id, sender="bot", content=ai_response)
        db.add(bot_message)
        db.commit()
        
        return ChatResponse(response=ai_response)
    
    except Exception as e:
        logger.error(f"Error during chat for user '{current_user.username}': {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

# 3.3. Chat History Endpoint
@router.get("/chat/history/{contract_id}", response_model=ChatHistorySchema)
@limiter.limit("10/minute")  # Adjust rate limit as needed
def get_chat_history(
    request: Request,  # Added Request parameter for rate limiting
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve chat history for a specific contract.
    """
    try:
        chat = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.contract_id == contract_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat history not found.")
        
        messages = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.timestamp).all()
        messages_schema = [
            MessageSchema(sender=msg.sender, content=msg.content, timestamp=msg.timestamp.isoformat())
            for msg in messages
        ]
        
        return ChatHistorySchema(chat_id=chat.id, messages=messages_schema)
    
    except Exception as e:
        logger.error(f"Error fetching chat history for user '{current_user.username}': {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving chat history.")
