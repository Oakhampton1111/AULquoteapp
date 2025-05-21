import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.services.llm.model import WarehouseLLM
from warehouse_quote_app.app.services.business.quote_service import QuoteService, QuoteRequest, QuoteResponse
from warehouse_quote_app.app.services.business.rate_calculator import ServiceDimensions
from warehouse_quote_app.app.services.business.container_calculator import PackingMaterials
from warehouse_quote_app.app.schemas.chat import Message as ChatMessage
from warehouse_quote_app.app.schemas.conversation import ChatSession, QuoteContext, CurrentQuoteInfo
from warehouse_quote_app.app.services.crm.base import BaseCRMService # Import CRM Service
from warehouse_quote_app.app.schemas.crm import CRMCustomerCreate, CRMQuoteCreate # Import CRM Schemas
from warehouse_quote_app.app import models # For models.User type hint
import logging # For logging

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, crm_service: BaseCRMService, db: Optional[AsyncSession] = None): # Added crm_service, made db optional
        self.llm = WarehouseLLM()
        self.sessions: Dict[str, ChatSession] = {}
        self.quote_service = QuoteService() 
        self.crm_service = crm_service # Store CRM service instance
        # self.db = db # db is not used by current QuoteService or this ChatService directly

    async def create_session(self, user_id: int) -> str: # user_id is app user_id
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        initial_prompt_context = {"context": "New session started."}
        system_greeting = await self.llm.generate_response(
            input_text="",
            template_key="general",
            context=initial_prompt_context
        )

        self.sessions[session_id] = ChatSession(
            id=session_id,
            user_id=user_id,
            messages=[ChatMessage(sender="assistant", content=system_greeting, timestamp=datetime.now(), message_id=str(uuid.uuid4()))],
            context=QuoteContext(collected_info={}, current_quote=None, offered_discounts={}),
            created_at=datetime.now()
        )
        return session_id

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.sessions.get(session_id)

    async def add_message_to_session(self, session: ChatSession, role: str, content: str):
        # 'role' from LLM prompt is 'user' or 'assistant', maps to ChatMessage.sender
        session.messages.append(ChatMessage(sender=role, content=content, timestamp=datetime.now(), message_id=str(uuid.uuid4())))

    def _parse_boolean(self, value: Any, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 'y']
        return default

    def _parse_optional_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_optional_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _transform_llm_to_quote_request_args(
        self, 
        llm_extracted_data: Dict[str, Any],
        current_session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforms nested LLM extracted data and current session data into a flat dictionary 
        suitable for QuoteRequest dataclass instantiation.
        LLM data takes precedence for fields it provides.
        """
        
        # Start with current session data as a base
        merged_data = current_session_data.copy()
        # Update with LLM extracted data, LLM data is king for what it provides
        merged_data.update(llm_extracted_data)

        # Initialize args with default values from QuoteRequest or None
        args = {
            "services": [],
            "dimensions": None,
            "storage_type": None,
            "duration_weeks": None,
            "quantity": None,
            "has_dangerous_goods": False,
            "customer_type": None,
            "company_name": None,
            "transport_type": None,
            "from_postcode": None,
            "to_postcode": None,
            "from_suburb": None,
            "to_suburb": None,
            "container_size": None, # For transport of containers
            "duration_hours": None,
            "vehicle_type": None,
            "return_journey": True, # Default in QuoteRequest
            "container_type": None, # For container rental
            "packing_materials": None,
            "loading_assistance": False,
        }
        
        # Update with merged_data, applying transformations
        service_type_str = merged_data.get("service_type")
        if service_type_str and isinstance(service_type_str, str):
            args["services"] = [s.strip() for s in service_type_str.lower().split(",")]

        # General requirements (can be on QuoteRequest or handled separately)
        general_reqs = merged_data.get("general_requirements", {})
        args["customer_type"] = merged_data.get("customer_type", general_reqs.get("customer_type", args["customer_type"])) # Example: customer_type might be top-level or in general_reqs
        args["company_name"] = merged_data.get("company_name", general_reqs.get("company_name", args["company_name"]))
        # customer_notes can be used for additional context or specific QuoteRequest fields if mapped.

        # Storage details
        storage_details = merged_data.get("storage_details", {})
        if storage_details:
            dim_data = storage_details.get("dimensions")
            if isinstance(dim_data, dict):
                try:
                    args["dimensions"] = ServiceDimensions(
                        length=Decimal(dim_data.get("length", 0)),
                        width=Decimal(dim_data.get("width", 0)),
                        height=Decimal(dim_data.get("height", 0))
                    )
                except (TypeError, ValueError): # Handle if conversion fails
                    args["dimensions"] = None 
            args["storage_type"] = storage_details.get("storage_type", args["storage_type"])
            args["duration_weeks"] = self._parse_optional_int(storage_details.get("duration_weeks", args["duration_weeks"]))
            args["quantity"] = self._parse_optional_int(storage_details.get("quantity", args["quantity"]))
            args["has_dangerous_goods"] = self._parse_boolean(storage_details.get("has_dangerous_goods", args["has_dangerous_goods"]))

        # Transport details
        transport_details = merged_data.get("transport_details", {})
        if transport_details:
            args["transport_type"] = transport_details.get("transport_type", args["transport_type"])
            args["from_postcode"] = transport_details.get("from_postcode", args["from_postcode"])
            args["to_postcode"] = transport_details.get("to_postcode", args["to_postcode"])
            args["from_suburb"] = transport_details.get("from_suburb", args["from_suburb"]) # Not in QuoteRequest directly
            args["to_suburb"] = transport_details.get("to_suburb", args["to_suburb"]) # Not in QuoteRequest directly
            args["container_size"] = transport_details.get("container_size_for_transport", args["container_size"]) # Map to QuoteRequest.container_size
            args["duration_hours"] = self._parse_optional_float(transport_details.get("duration_hours", args["duration_hours"]))
            args["vehicle_type"] = transport_details.get("vehicle_type", args["vehicle_type"])
            args["return_journey"] = self._parse_boolean(transport_details.get("return_journey", args["return_journey"]))
            # Update has_dangerous_goods if transport specifies it
            if "is_dangerous_goods" in transport_details: # LLM prompt uses "is_dangerous_goods"
                 args["has_dangerous_goods"] = args["has_dangerous_goods"] or self._parse_boolean(transport_details.get("is_dangerous_goods"))

        # Container details (for container rental)
        container_details = merged_data.get("container_details", {})
        if container_details:
            args["container_type"] = container_details.get("container_type", args["container_type"]) # This is QuoteRequest.container_type
            # The QuoteRequest.container_size is typically for *transporting* a container.
            # If LLM uses container_size for rental, ensure it maps to container_type or a specific field.
            # For now, assuming container_type from LLM maps to QuoteRequest.container_type.
            args["duration_weeks"] = self._parse_optional_int(container_details.get("duration_weeks", args["duration_weeks"])) # Overwrites if also in storage
            
            pm_data = container_details.get("packing_materials") # LLM prompt has packing_materials_required (boolean)
            if self._parse_boolean(container_details.get("packing_materials_required")):
                 # This needs mapping to PackingMaterials dataclass if it's complex
                 # For now, assuming a simple boolean or a placeholder if PackingMaterials is complex
                 args["packing_materials"] = PackingMaterials(enabled=True) # Example, adjust as per PackingMaterials definition
            else:
                 args["packing_materials"] = PackingMaterials(enabled=False)

            args["loading_assistance"] = self._parse_boolean(container_details.get("loading_assistance_required", args["loading_assistance"]))
            if "has_dangerous_goods" in container_details:
                 args["has_dangerous_goods"] = args["has_dangerous_goods"] or self._parse_boolean(container_details.get("has_dangerous_goods"))

        # Clean out None values if QuoteRequest fields don't have Optional type and no default
        # However, QuoteRequest fields are mostly Optional or have defaults.
        final_args = {k: v for k, v in args.items() if v is not None or k in QuoteRequest.__annotations__}

        return final_args


    async def process_message(
        self, 
        session_id: str, 
        user_content: str, 
        current_user: models.User # Added current_user
    ) -> Dict[str, Any]:
        session = await self.get_session(session_id)
        if not session:
            return {"error": "Session not found", "response": "Session not found. Please start a new session."}

        await self.add_message_to_session(session, "user", user_content)
        conversation_history = "\n".join([f"{msg.sender}: {msg.content}" for msg in session.messages[-10:]])
        
        extraction_context = {"conversation": conversation_history}
        extracted_json_str = await self.llm.generate_response(
            input_text=user_content,
            template_key="rate_extraction",
            context=extraction_context
        )

        llm_extracted_data = {}
        try:
            json_start = extracted_json_str.find('{')
            json_end = extracted_json_str.rfind('}') + 1
            if json_start != -1 and json_end != -1 and json_start < json_end:
                json_candidate = extracted_json_str[json_start:json_end]
                llm_extracted_data = json.loads(json_candidate)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from rate_extraction: {extracted_json_str}")

        # Transform and update collected_info
        # Pass current session.context.collected_info to preserve existing data not overwritten by LLM
        transformed_request_args = self._transform_llm_to_quote_request_args(llm_extracted_data, session.context.collected_info)
        session.context.collected_info = transformed_request_args # Store transformed data

        # Instantiate QuoteRequest
        # Ensure all required fields for QuoteRequest are present or have defaults
        # For example, 'services' must be a list. If not provided by LLM, default to empty or handle.
        if not session.context.collected_info.get("services"):
             session.context.collected_info["services"] = [] # Default if not found

        # Filter for args actually in QuoteRequest to prevent passing unexpected args
        valid_qr_fields = QuoteRequest.__annotations__.keys()
        filtered_qr_args = {k: v for k, v in session.context.collected_info.items() if k in valid_qr_fields}


        # Handle specific types like ServiceDimensions and PackingMaterials if they are not being constructed properly
        # This is a simplified example; actual construction might be more complex
        if 'dimensions' in filtered_qr_args and isinstance(filtered_qr_args['dimensions'], dict):
            dim_dict = filtered_qr_args['dimensions']
            try:
                filtered_qr_args['dimensions'] = ServiceDimensions(
                    length=Decimal(dim_dict.get('length',0)), 
                    width=Decimal(dim_dict.get('width',0)), 
                    height=Decimal(dim_dict.get('height',0))
                )
            except: # Fallback if parsing fails
                filtered_qr_args['dimensions'] = None
        
        if 'packing_materials' in filtered_qr_args and isinstance(filtered_qr_args['packing_materials'], dict):
             pm_dict = filtered_qr_args['packing_materials']
             filtered_qr_args['packing_materials'] = PackingMaterials(enabled=pm_dict.get('enabled', False)) # Example


        quote_request_instance = QuoteRequest(**filtered_qr_args)
        
        # Call QuoteService (synchronous)
        quote_response: QuoteResponse = self.quote_service.process_quote_request(quote_request_instance)

        assistant_response_text = ""
        session.context.current_quote = None # Reset current quote

        if quote_response.line_items and quote_response.total_amount > Decimal('0.0'):
            summary_context = {
                "quote_details": {
                    "line_items": quote_response.line_items,
                    "total_amount": str(quote_response.total_amount), # Convert Decimal to string for JSON
                    "messages": quote_response.messages,
                    "follow_up_questions": quote_response.follow_up_questions
                }
            }
            assistant_response_text = await self.llm.generate_response(
                input_text="", # Prompt is self-contained
                template_key="quote_summary",
                context=summary_context
            )
            session.context.current_quote = CurrentQuoteInfo(
                line_items=quote_response.line_items,
                total_amount=str(quote_response.total_amount),
                messages=quote_response.messages,
                follow_up_questions=quote_response.follow_up_questions
            )

            # --- CRM Quote Sync ---
            if session.context.current_quote and current_user:
                crm_customer_id = None
                # Try to get crm_id from user model (if we decide to store it there)
                # if hasattr(current_user, 'crm_id') and current_user.crm_id:
                #    crm_customer_id = current_user.crm_id
                
                if not crm_customer_id: # If not on user model or not found
                    crm_customer = await self.crm_service.get_customer_by_email(email=current_user.email)
                    if crm_customer:
                        crm_customer_id = crm_customer.crm_id
                    else:
                        # Create customer in CRM if not found
                        logger.info(f"Customer {current_user.email} not found in CRM by email, creating...")
                        new_crm_customer_data = CRMCustomerCreate(
                            email=current_user.email,
                            first_name=current_user.first_name,
                            last_name=current_user.last_name,
                            phone=current_user.phone,
                            company_name=current_user.company_name,
                            app_user_id=current_user.id
                        )
                        crm_customer_id = await self.crm_service.create_or_update_customer(customer_data=new_crm_customer_data)
                        if crm_customer_id:
                            logger.info(f"Customer {current_user.email} created in CRM with ID: {crm_customer_id}")
                        else:
                            logger.error(f"Failed to create customer {current_user.email} in CRM for quote linking.")
                
                if crm_customer_id:
                    # Generate a temporary app_quote_id
                    # In a real system, this ID would come from a persisted quote record in the app's DB
                    temp_app_quote_id_str = f"{session.id}_{len(session.messages)}" 
                    # Attempt to convert to int, or use string if schema allows
                    try:
                        temp_app_quote_id = int(datetime.now().timestamp()) # Or a hash, or just use string if schema allows
                    except ValueError: # Fallback if conversion is an issue, though timestamp should be fine
                        temp_app_quote_id = hash(temp_app_quote_id_str) & 0xffffffff # Example hash to int


                    crm_quote_data = CRMQuoteCreate(
                        app_quote_id=temp_app_quote_id, # Using timestamp for pseudo-uniqueness
                        total_amount=Decimal(session.context.current_quote.total_amount),
                        service_type=session.context.collected_info.get('service_type', 'unknown'),
                        status="presented_to_user", # Or "draft", "summarized"
                        created_at=datetime.now(),
                        line_items=session.context.current_quote.line_items
                        # valid_until can be set if applicable
                    )
                    try:
                        crm_quote_id = await self.crm_service.link_quote_to_customer(
                            crm_customer_id=crm_customer_id,
                            quote_data=crm_quote_data
                        )
                        if crm_quote_id:
                            logger.info(f"Quote (App ID: {temp_app_quote_id}) linked to CRM Customer ID {crm_customer_id}. CRM Quote ID: {crm_quote_id}")
                        else:
                            logger.warning(f"Failed to link quote (App ID: {temp_app_quote_id}) to CRM Customer ID {crm_customer_id}.")
                    except Exception as e:
                        logger.error(f"Error linking quote to CRM for customer {crm_customer_id}: {e}", exc_info=True)
                else:
                    logger.warning(f"Could not obtain CRM Customer ID for user {current_user.email}. Quote not synced to CRM.")
            # --- End CRM Quote Sync ---

        elif quote_response.missing_information:
            clarification_context = {
                "missing_fields_list": ", ".join(quote_response.missing_information),
                "last_user_message": user_content,
            }
            assistant_response_text = await self.llm.generate_response(
                input_text="", 
                template_key="clarification_request",
                context=clarification_context
            )
        elif extracted_json_str.strip() and not extracted_json_str.strip().startswith("{"):
            assistant_response_text = extracted_json_str
        else:
            general_context = {
                "context": json.dumps(session.context.collected_info),
                "history": conversation_history
            }
            assistant_response_text = await self.llm.generate_response(
                input_text=user_content,
                template_key="general",
                context=general_context
            )

        await self.add_message_to_session(session, "assistant", assistant_response_text)

        return {
            "session_id": session_id,
            "response": assistant_response_text,
            "quote": session.context.current_quote.model_dump() if session.context.current_quote else None,
            "collected_info": session.context.collected_info,
            "missing_information": quote_response.missing_information,
            "service_type_provided": session.context.collected_info.get("service_type") is not None # service_type is string, not list
        }

    async def update_session_context(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        session = await self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Assume updates are already in the transformed QuoteRequest-compatible format
        session.context.collected_info.update(updates)
        
        valid_qr_fields = QuoteRequest.__annotations__.keys()
        filtered_qr_args = {k: v for k, v in session.context.collected_info.items() if k in valid_qr_fields}
        if not filtered_qr_args.get("services"): # Ensure services list exists
            filtered_qr_args["services"] = []

        if 'dimensions' in filtered_qr_args and isinstance(filtered_qr_args['dimensions'], dict):
            dim_dict = filtered_qr_args['dimensions']
            try:
                filtered_qr_args['dimensions'] = ServiceDimensions(length=Decimal(dim_dict.get('length',0)), width=Decimal(dim_dict.get('width',0)), height=Decimal(dim_dict.get('height',0)))
            except:
                filtered_qr_args['dimensions'] = None
        
        if 'packing_materials' in filtered_qr_args and isinstance(filtered_qr_args['packing_materials'], dict):
             pm_dict = filtered_qr_args['packing_materials']
             filtered_qr_args['packing_materials'] = PackingMaterials(enabled=pm_dict.get('enabled', False))


        quote_request_instance = QuoteRequest(**filtered_qr_args)
        quote_response: QuoteResponse = self.quote_service.process_quote_request(quote_request_instance)
        
        if quote_response.line_items and quote_response.total_amount > Decimal('0.0'):
            session.context.current_quote = CurrentQuoteInfo(
                line_items=quote_response.line_items,
                total_amount=str(quote_response.total_amount),
                messages=quote_response.messages,
                follow_up_questions=quote_response.follow_up_questions
            )
        else:
            session.context.current_quote = None # Clear if quote no longer valid
            
        return {
            "session_id": session_id,
            "quote": session.context.current_quote.model_dump() if session.context.current_quote else None,
            "collected_info": session.context.collected_info,
            "missing_information": quote_response.missing_information
        }
