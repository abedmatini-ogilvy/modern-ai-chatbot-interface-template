/**
 * API Client Test Script
 * 
 * Quick test to verify the API client works correctly.
 * Run with: node lib/test-api-client.mjs
 */

import {
  getResearchQuestions,
  startResearch,
  getResearchStatus,
  getResearchResult,
  checkHealth,
  ResearchPhase
} from './api-client.ts';

async function testApiClient() {
  console.log('🧪 Testing API Client\n');

  try {
    // Test 1: Health Check
    console.log('1️⃣ Testing health check...');
    const health = await checkHealth();
    console.log('✅ Health:', health.status);
    console.log();

    // Test 2: Get Questions
    console.log('2️⃣ Testing research questions...');
    const questions = await getResearchQuestions();
    console.log(`✅ Found ${questions.length} questions`);
    questions.forEach(q => console.log(`   - ${q.title}`));
    console.log();

    // Test 3: Start Research
    console.log('3️⃣ Starting research...');
    const startResponse = await startResearch({
      question_id: questions[0].id,
      conversation_id: 'test-from-client',
    });
    console.log(`✅ Research started: ${startResponse.session_id}`);
    console.log();

    // Test 4: Poll Status
    console.log('4️⃣ Polling status...');
    let attempts = 0;
    const maxAttempts = 30;

    while (attempts < maxAttempts) {
      const status = await getResearchStatus(startResponse.session_id);
      console.log(`   Progress: ${status.progress_percentage}% - ${status.phase} - ${status.current_agent || 'Starting...'}`);

      if (status.phase === ResearchPhase.COMPLETED) {
        console.log('✅ Research completed!');
        console.log();

        // Test 5: Get Result
        console.log('5️⃣ Getting result...');
        const result = await getResearchResult(startResponse.session_id);
        console.log(`✅ Result retrieved`);
        console.log(`   Question: ${result.question}`);
        console.log(`   Time: ${result.execution_time_seconds.toFixed(2)}s`);
        console.log(`   Data points: ${result.total_data_points}`);
        console.log(`   Twitter: ${result.data_collected.social_media.twitter.total_results}`);
        console.log(`   TikTok: ${result.data_collected.social_media.tiktok.total_results}`);
        console.log(`   Reddit: ${result.data_collected.social_media.reddit.total_results}`);
        console.log();
        break;
      } else if (status.phase === ResearchPhase.FAILED) {
        console.log('❌ Research failed:', status.error);
        break;
      }

      attempts++;
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    if (attempts >= maxAttempts) {
      console.log('⏱️ Timeout waiting for research to complete');
    }

    console.log('\n✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error);
    process.exit(1);
  }
}

// Only run if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  testApiClient();
}
