from global_models import get_embedding_model, get_llm_model
from services.parse_pdf import extract_text_from_pdf
from services.indexer import index_pdf_text
from services.summarize_service import summarize_from_indexed_pdf
from services.agentic_summarizer import AgenticSummarizer
from extensions import celery
import os

@celery.task(rate_limit="15/m")
def process_pdf_task(filename, filepath, base_name ,relative_path=None):
    try:
        embedding_model = get_embedding_model()
        llm_model = get_llm_model()

        text = extract_text_from_pdf(filepath)
        index_pdf_text(base_name, text, embedding_model=embedding_model)
        summary = summarize_from_indexed_pdf(base_name, embedding_model=embedding_model, llm_model=llm_model)


        # Determining the output path for summary
        if relative_path:
            # Replace '.pdf' with '.txt' and mirror the location path inside the summaries directory
            summary_rel_path = os.path.splitext(relative_path)[0] + ".txt"
            summary_path = os.path.join("summaries", summary_rel_path)
        
        else:
            # Fallback to flat summary
            summary_path = os.path.join("summaries", base_name + ".txt")

        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        
        with open(summary_path, "w") as f:
            f.write(summary)

        return {
            "status": "completed",
            "filename": filename,
            "summary_path": summary_path,
            "summary_text": summary
        }
    except Exception as e:
        return {"status": "error", "filename": filename, "error": str(e)}

@celery.task(rate_limit="15/m", bind=True)
def process_pdf_task_agentic(self, filename, filepath, base_name, relative_path=None):
    """Fast agentic PDF processing with fallback to standard processing"""
    try:
        print(f"Starting agentic processing for {filename}")
        
        # Update task status
        self.update_state(
            state="PROGRESS", 
            meta={"status": "Initializing agentic processing...", "progress": 10}
        )
        
        # Extract text from PDF
        text = extract_text_from_pdf(filepath)
        
        if not text or len(text.strip()) < 100:
            return {
                "status": "error",
                "filename": filename,
                "error": "Could not extract sufficient text from PDF"
            }
        
        # Update status
        self.update_state(
            state="PROGRESS", 
            meta={"status": "Dividing content into chunks...", "progress": 20}
        )
        
        # Initialize agentic summarizer
        summarizer = AgenticSummarizer()
        
        # Update status
        self.update_state(
            state="PROGRESS", 
            meta={"status": "Processing chunks with specialized agents...", "progress": 30}
        )
        
        # Try agentic summarization with fallback
        try:
            result = summarizer.fast_summarize(text, filename)
            summary = result["summary"]
            processing_method = "agentic"
            chunks_processed = result["chunks_processed"]
            processing_time = result["processing_time"]
            
        except Exception as agentic_error:
            # If agentic fails due to rate limits, fall back to standard
            if "429" in str(agentic_error) or "quota" in str(agentic_error).lower():
                print(f"Agentic processing failed due to rate limits, falling back to standard for {filename}")
                
                self.update_state(
                    state="PROGRESS", 
                    meta={"status": "Rate limited, falling back to standard processing...", "progress": 40}
                )
                
                # Use standard summarization
                from services.summarize_service import summarize_from_indexed_pdf
                embedding_model = get_embedding_model()
                llm_model = get_llm_model()
                
                index_pdf_text(base_name, text, embedding_model=embedding_model)
                summary = summarize_from_indexed_pdf(base_name, embedding_model=embedding_model, llm_model=llm_model)
                processing_method = "standard_fallback"
                chunks_processed = 1
                processing_time = None
            else:
                raise agentic_error
        
        # Update status
        self.update_state(
            state="PROGRESS", 
            meta={"status": "Indexing for QA...", "progress": 70}
        )
        
        # Index for QA functionality if not already done
        if processing_method == "agentic":
            embedding_model = get_embedding_model()
            index_pdf_text(base_name, text, embedding_model=embedding_model)
        
        # Update status
        self.update_state(
            state="PROGRESS", 
            meta={"status": "Saving summary...", "progress": 90}
        )
        
        # Determining the output path for summary
        if relative_path:
            summary_rel_path = os.path.splitext(relative_path)[0] + ".txt"
            summary_path = os.path.join("summaries", summary_rel_path)
        else:
            summary_path = os.path.join("summaries", base_name + ".txt")

        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        
        # Save summary with proper encoding
        with open(summary_path, "w", encoding='utf-8') as f:
            f.write(summary)

        return {
            "status": "completed",
            "filename": filename,
            "summary_path": summary_path,
            "summary_text": summary,
            "processing_method": processing_method,
            "chunks_processed": chunks_processed,
            "processing_time": processing_time
        }
        
    except Exception as e:
        print(f"Error in agentic task: {str(e)}")
        return {
            "status": "error", 
            "filename": filename, 
            "error": str(e)
        }
