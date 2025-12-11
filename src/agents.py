from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from .structure_outputs import *
from .prompts import *
from dotenv import load_dotenv

load_dotenv()

class Agents:
    def __init__(self):       
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite')
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
            )
        vectorstore = Chroma(persist_directory='db',embedding_function=embeddings)
        retriver = vectorstore.as_retriever(search_kwargs={"k":3})
        email_category_prompt = PromptTemplate(
            template=CATEGORIZE_EMAIL_PROMPT,
            input_variables=['email']
        )
        self.categorize_mail = (
            email_category_prompt |
            llm.with_structured_output(CategorizeEmailOutput)
        )
        generate_querry_prompt = PromptTemplate(
            template = GENERATE_QUERRY_PROMPT,
            input_variables=['email']
        )
        self.generating_querry = (
            generate_querry_prompt |
            llm.with_structured_output(RagQuerries)
        )
        
        qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_PROMPT)
        self.generate_rag_answer = (
            {"context":retriver,"quetion":RunnablePassthrough()}
            | qa_prompt
            | llm
            | StrOutputParser()
        )
        
        # writting email for the customer
        email_writer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",EMAIL_WRITER_PROMPT),
                MessagesPlaceholder("history")
                ("human","{email_information}")
            ]
        )
        
        self.email_writer = (
            email_writer_prompt 
            | llm.with_structured_output(EmailWritter)
        )
        
        proofreader_prompt = PromptTemplate(
            template=EMAIL_PROOFREADER_PROMPT, 
            input_variables=["initial_email", "generated_email"]
        )
        self.email_proofreader = (
            proofreader_prompt | 
            llm.with_structured_output(ProofReaderOutput) 
        )
        
        
        
        
        
        

