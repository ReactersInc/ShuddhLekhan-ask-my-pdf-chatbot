import os
from services.parse_pdf import extract_text_from_pdf

class TaskRouter:
    def __init__(self):
        # Optimized thresholds for free tier
        self.agentic_threshold = 5000   # characters - use agentic for medium+ docs
        self.max_agentic_size = 30000   # characters - very large docs use standard to avoid too many chunks
        self.min_chunks_threshold = 2  # Only use agentic if it will create 2+ chunks
    
    def should_use_agentic(self, filename: str) -> bool:
        """Determine if we should use agentic processing"""
        try:
            # Extract content to check size
            pdf_path = os.path.join('uploads', filename)
            content = extract_text_from_pdf(pdf_path)
            
            if not content:
                return False
            
            content_size = len(content)
            print(f"Content size for {filename}: {content_size} characters")
            
            # Calculate potential chunks to see if agentic is worth it
            estimated_chunks = max(1, content_size // 4000)  # Using chunk_size of 4000
            
            # Use agentic only if:
            # 1. Content is large enough to benefit from chunking
            # 2. Not too large to cause too many API calls
            # 3. Will create at least 2 chunks for specialized processing
            if (self.agentic_threshold <= content_size <= self.max_agentic_size and 
                estimated_chunks >= self.min_chunks_threshold):
                print(f"Using agentic processing for {filename} (estimated {estimated_chunks} chunks)")
                return True
            else:
                if content_size < self.agentic_threshold:
                    print(f"Using standard processing for {filename} (too small for chunking)")
                else:
                    print(f"Using standard processing for {filename} (too large, would create {estimated_chunks} chunks)")
                return False
                
        except Exception as e:
            print(f"Error determining processing method: {e}")
            return False  # Default to standard processing
    
    def get_task_function(self, use_agentic: bool):
        """Return appropriate task function"""
        if use_agentic:
            from pdf_tasks import process_pdf_task_agentic
            return process_pdf_task_agentic
        else:
            from pdf_tasks import process_pdf_task
            return process_pdf_task
