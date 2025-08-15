import requests
import json

url = "http://127.0.0.1:5000/plagiarism/upload"
file_path = r"C:\Users\infin\Documents\CDAC_TU\CheckPLG1\plagarism\uploads\2506.22659v1.pdf"

try:
    print("Uploading PDF and starting ArXiv integration...")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        # Increase timeout to handle longer processing times
        response = requests.post(url, files=files, timeout=600)  # 10 minute timeout
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 50)
            print("UPLOAD AND PROCESSING SUCCESSFUL")
            print("=" * 50)
            print(f"File: {result.get('message', 'Unknown')}")
            print(f"Sections: {result.get('sections_count', 0)}")
            print(f"Keywords: {result.get('keyword_results_count', 0)}")
            
            # ArXiv results
            arxiv = result.get('arxiv_collection', {})
            print("\nArXiv Collection Results:")
            print(f"   Success: {arxiv.get('success', False)}")
            print(f"   Papers Found: {arxiv.get('papers_found', 0)}")
            print(f"   Papers Downloaded: {arxiv.get('papers_downloaded', 0)}")
            print(f"   Query Used: {arxiv.get('query_used', 'N/A')}")
            print(f"   Storage: {arxiv.get('storage_paths', {}).get('pdfs_dir', 'N/A')}")
            
            # Web results
            web = result.get('web_collection', {})
            print("\nWeb Collection Results:")
            print(f"   Success: {web.get('success', False)}")
            print(f"   Chunks Processed: {web.get('chunks_processed', 0)}")
            print(f"   URLs Found: {web.get('urls_found', 0)}")
            print(f"   Content Extracted: {web.get('content_extracted', 0)}")
            print(f"   Total Words: {web.get('total_word_count', 0)}")
            
            print("\nFiles Created:")
            print(f"   - {result.get('chunks_json', 'N/A')}")
            print(f"   - {result.get('keywords_json', 'N/A')}")
            print("   - scraped_data/arxiv/pdfs/ (ArXiv papers)")
            print("   - scraped_data/arxiv/metadata/ (Paper metadata)")
            print("   - scraped_data/web/content/ (Web content)")
            print("   - scraped_data/web/metadata/ (Web metadata)")
            
            print("=" * 50)
            
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
except requests.exceptions.Timeout:
    print("Request timed out - PDF processing took too long (>10 minutes)")
    print("Try with a smaller PDF or increase the timeout")
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
    print("Make sure the Flask server is running at http://127.0.0.1:5000")
except Exception as e:
    print(f"Unexpected error: {e}")