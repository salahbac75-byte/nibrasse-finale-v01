import pandas as pd
import sys
import os
import time
from app.services.rag import rag_pipeline

# Add project root to path
sys.path.append(os.getcwd())

def evaluate_dataset(input_file='golden_dataset_test.csv', output_file='test_results.csv'):
    print(f"Loading dataset from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return

    results = []
    
    print(f"Starting evaluation of {len(df)} questions...")
    
    for index, row in df.iterrows():
        question = row['question']
        ground_truth = row['ground_truth']
        question_type = row['question_type']
        
        print(f"\nProcessing Q{index+1}/{len(df)}: {question}")
        
        start_time = time.time()
        try:
            # Add a simple retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = rag_pipeline(question)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"  Retry {attempt+1}/{max_retries} due to error: {e}")
                    time.sleep(2)
            
            generated_answer = response['answer']
            
            # Extract source titles if available
            sources = []
            if 'metadatas' in response:
                for meta in response['metadatas']:
                    if meta and 'filename' in meta:
                        sources.append(meta['filename'])
            
            sources_str = ", ".join(sources)

            # Extract retrieved context text
            retrieved_contexts = response.get('context', [])
            contexts_str = " ||| ".join(retrieved_contexts)
            
        except Exception as e:
            print(f"Error processing question: {e}")
            generated_answer = f"ERROR: {str(e)}"
            sources_str = ""
            contexts_str = ""
            
        elapsed_time = time.time() - start_time
        
        results.append({
            'question': question,
            'ground_truth': ground_truth,
            'generated_answer': generated_answer,
            'sources': sources_str,
            'retrieved_context': contexts_str,
            'question_type': question_type,
            'time_taken': round(elapsed_time, 2)
        })
        
        # Optional: Add a small delay to avoid hitting rate limits too hard
        time.sleep(1)

    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Save to CSV
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nEvaluation complete. Results saved to {output_file}")

if __name__ == "__main__":
    evaluate_dataset()
