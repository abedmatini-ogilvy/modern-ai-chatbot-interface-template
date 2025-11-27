"""
Test script for Research Service

This script tests the research service independently before integrating
it into the FastAPI endpoints.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.research_service import ResearchService
from models.research_models import ProgressUpdate

async def test_research_service():
    """Test the research service with mock data"""
    print("="*60)
    print("Testing Research Service")
    print("="*60)
    
    # Create service instance
    service = ResearchService()
    
    # Test 1: Get pre-configured questions
    print("\n1. Testing get_research_questions()...")
    questions = service.get_research_questions()
    print(f"   ✅ Found {len(questions)} pre-configured questions")
    for q in questions:
        print(f"      - {q['title']}")
    
    # Test 2: Get specific question
    print("\n2. Testing get_research_question()...")
    question = service.get_research_question("gen_z_nigeria")
    if question:
        print(f"   ✅ Retrieved: {question['title']}")
        print(f"      Question: {question['question'][:80]}...")
    
    # Test 3: Conduct research with progress updates
    print("\n3. Testing conduct_research() with mock data...")
    print("   This will take ~15-20 seconds with mock API delays...\n")
    
    progress_updates = []
    
    def progress_callback(update: ProgressUpdate):
        """Callback to track progress"""
        print(f"   [{update.timestamp.strftime('%H:%M:%S')}] {update.message}")
        progress_updates.append(update)
    
    # Run research
    result = await service.conduct_research(
        question="What are the emerging trends in African e-commerce?",
        search_query="African e-commerce trends 2024",
        session_id="test_session_123",
        progress_callback=progress_callback,
        max_results=30
    )
    
    # Display results
    print("\n" + "="*60)
    print("Research Results Summary")
    print("="*60)
    print(f"Session ID: {result.session_id}")
    print(f"Phase: {result.phase}")
    print(f"Execution Time: {result.execution_time_seconds:.2f}s")
    print(f"Total Data Points: {result.total_data_points}")
    print(f"Failed APIs: {result.failed_apis if result.failed_apis else 'None'}")
    print(f"Progress Updates: {len(result.progress_updates)}")
    
    if result.error:
        print(f"\n❌ Error: {result.error}")
    else:
        print("\n✅ Research completed successfully!")
        
        if result.executive_summary:
            print(f"\nExecutive Summary (first 200 chars):")
            print(f"{result.executive_summary[:200]}...")
        
        if result.key_findings:
            print(f"\nKey Findings ({len(result.key_findings)} items):")
            for i, finding in enumerate(result.key_findings[:3], 1):
                print(f"  {i}. {finding[:100]}...")
        
        if result.report:
            print(f"\nFull Report Length: {len(result.report)} characters")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_research_service())
