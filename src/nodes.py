from colorama import Fore, Style
from .agents import Agents
from tools.gmail_tools import GmailToolsClass
from .state import GraphState, Email

class Nodes:
    def __int__(self):
        self.agents = Agents()
        self.gmail_tools = GmailToolsClass()

    def load_inbox_emails(self,state: GraphState) -> GraphState:
        """Load new emails rom gmail and updates the state"""
        print(Fore.YELLOW+"Loading new email... \n"+Style.RESET_ALL)
        recent_emails = self.gmail_tools.fetch_unanswered_emails()
        emails = [Email(**email) for email in recent_emails]
        return {"emails": emails}
    
    def check_new_emails(self, state: GraphState) -> str:
        """Checks if there are new emails to process."""
        if len(state['emails']) == 0:
            print(Fore.RED + "No new emails" + Style.RESET_ALL)
            return "empty"
        else:
            print(Fore.GREEN + "New emails to process" + Style.RESET_ALL)
            return "process"
        
    def is_email_inbox_empty(self, state: GraphState) -> GraphState:
        return state

    def categorize_email(self, state: GraphState) -> GraphState:
        """Categorizes the current email using the categorize_email agent."""
        print(Fore.YELLOW + "Checking email category...\n" + Style.RESET_ALL)
        
        # Get the last email
        current_email = state["emails"][-1]
        result = self.agents.categorize_mail.invoke({"email": current_email.body})
        print(Fore.MAGENTA + f"Email category: {result.category.value}" + Style.RESET_ALL)
        
        return {
            "email_category": result.category.value,
            "current_email": current_email
        }
    
    def route_email_based_on_category(self, state: GraphState) -> GraphState:
        email_category = state['email_category']
        if email_category == "product_enquiry":
            return "product related"
        elif email_category == "unrelated":
            return "unrelated"
        else:
            return "customer_review"
        
    def construerct_rag_queries(self, state: GraphState) -> GraphState:
        email = state['current_email'].body
        rag_querries = self.agents.generating_querry.invoke({email:email})
        return {'rag_queries':rag_querries.querries}
    
    def retrive_from_rag(self, state: GraphState) -> GraphState:
        for querry in state['rag_queries']:
            ans = self.agents.generate_rag_answer.invoke(querry)
            final_ans += querry + '\n' + ans + '\n\n' 
        return {'retrived_document':final_ans}

    def write_draft_email(self, state: GraphState) -> GraphState:
        inputs = (
            f'# **EMAIL CATEGORY:** {state["email_category"]}\n\n'
            f'# **EMAIL CONTENT:**\n{state["current_email"].body}\n\n'
            f'# **INFORMATION:**\n{state["retrieved_documents"]}' # Empty for feedback or complaint
        )  
        writter_messages = state.get('writter_messages',[])
        
        draft_result = self.agents.email_writer.invoke(
            {
                "email_information" : inputs,
                "history" : writter_messages
            }
        )     
        email = draft_result.email
        trials = state.get('trials',0)
        writter_messages.append(f"**Draft {trials}:**\n{email}")
        return {
            'generated_email':email,
            'trials':trials,
            'writter_messages':writter_messages
        }
        
    def verify_generated_email(self, state: GraphState) -> GraphState:
        """Verifies the generated email using the proofreader agent."""
        print(Fore.YELLOW + "Verifying generated email...\n" + Style.RESET_ALL)
        review = self.agents.email_proofreader.invoke({
            "initial_email": state["current_email"].body,
            "generated_email": state["generated_email"],
        })

        writer_messages = state.get('writer_messages', [])
        writer_messages.append(f"**Proofreader Feedback:**\n{review.feedback}")

        return {
            "sendable": review.send,
            "writer_messages": writer_messages
        }
    
    def must_rewrite(self, state: GraphState) -> str:
        """Determines if the email needs to be rewritten based on the review and trial count."""
        email_sendable = state["sendable"]
        if email_sendable:
            print(Fore.GREEN + "Email is good, ready to be sent!!!" + Style.RESET_ALL)
            state["emails"].pop()
            state["writer_messages"] = []
            return "send"
        elif state["trials"] >= 3:
            print(Fore.RED + "Email is not good, we reached max trials must stop!!!" + Style.RESET_ALL)
            state["emails"].pop()
            state["writer_messages"] = []
            return "stop"
        else:
            print(Fore.RED + "Email is not good, must rewrite it..." + Style.RESET_ALL)
            return "rewrite"
        
    def create_draft_response(self, state: GraphState) -> GraphState:
        """Creates a draft response in Gmail."""
        print(Fore.YELLOW + "Creating draft email...\n" + Style.RESET_ALL)
        self.gmail_tools.create_draft_reply(state["current_email"], state["generated_email"])
        
        return {"retrieved_documents": "", "trials": 0}

    def send_email_response(self, state: GraphState) -> GraphState:
        """Sends the email response directly using Gmail."""
        print(Fore.YELLOW + "Sending email...\n" + Style.RESET_ALL)
        self.gmail_tools.send_reply(state["current_email"], state["generated_email"])
        
        return {"retrieved_documents": "", "trials": 0}
    
    def skip_unrelated_email(self, state):
        """Skip unrelated email and remove from emails list."""
        print("Skipping unrelated email...\n")
        state["emails"].pop()
        return state
    
    