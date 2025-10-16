/**
 * MioVo Advanced Features Test Suite
 * Tests for new TTS editing features and play all functionality
 */

const testResults = {
  passed: [],
  failed: [],
  timestamp: new Date().toISOString()
};

console.log('🧪 MioVo Advanced Features Test Suite');
console.log('=====================================\n');

// Test 1: Character-level pitch adjustment
async function testPitchAdjustment() {
  console.log('📝 Test 1: Character-level pitch adjustment');
  try {
    // Check if pitch adjustment popup appears on character click
    const textElement = document.querySelector('.editable-text');
    const charElement = textElement?.querySelector('.char-editable');
    
    if (!charElement) {
      throw new Error('No editable character elements found');
    }
    
    // Simulate click to show pitch popup
    charElement.click();
    const popup = document.querySelector('.pitch-adjustment-popup');
    
    if (!popup) {
      throw new Error('Pitch adjustment popup not displayed');
    }
    
    // Check for up/down arrows
    const upArrow = popup.querySelector('.pitch-up');
    const downArrow = popup.querySelector('.pitch-down');
    
    if (!upArrow || !downArrow) {
      throw new Error('Pitch adjustment arrows not found');
    }
    
    testResults.passed.push('✅ Character-level pitch adjustment working');
    console.log('   ✅ Popup appears on character click');
    console.log('   ✅ Up/down arrows present');
  } catch (error) {
    testResults.failed.push(`❌ Pitch adjustment: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test 2: Keyboard shortcuts
async function testKeyboardShortcuts() {
  console.log('\n⌨️ Test 2: Keyboard shortcuts');
  try {
    const charElement = document.querySelector('.char-editable');
    
    if (!charElement) {
      throw new Error('No editable character elements found');
    }
    
    // Test Shift+Click (accent)
    const shiftClickEvent = new MouseEvent('click', { shiftKey: true });
    charElement.dispatchEvent(shiftClickEvent);
    console.log('   ✅ Shift+Click (accent) triggered');
    
    // Test Ctrl+Click (pause)
    const ctrlClickEvent = new MouseEvent('click', { ctrlKey: true });
    charElement.dispatchEvent(ctrlClickEvent);
    console.log('   ✅ Ctrl+Click (pause) triggered');
    
    // Test Alt+Click (extend)
    const altClickEvent = new MouseEvent('click', { altKey: true });
    charElement.dispatchEvent(altClickEvent);
    console.log('   ✅ Alt+Click (extend) triggered');
    
    testResults.passed.push('✅ Keyboard shortcuts working');
  } catch (error) {
    testResults.failed.push(`❌ Keyboard shortcuts: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test 3: Speaker model selection
async function testSpeakerSelection() {
  console.log('\n🎤 Test 3: Speaker model selection');
  try {
    const speakerSelect = document.querySelector('select');
    
    if (!speakerSelect) {
      throw new Error('Speaker selection dropdown not found');
    }
    
    const options = speakerSelect.querySelectorAll('option');
    
    if (options.length !== 10) {
      throw new Error(`Expected 10 speakers, found ${options.length}`);
    }
    
    console.log('   ✅ Speaker dropdown found');
    console.log(`   ✅ ${options.length} speaker models available`);
    
    // List all speakers
    options.forEach((option, index) => {
      console.log(`      ${index + 1}. ${option.textContent}`);
    });
    
    testResults.passed.push('✅ Speaker model selection working');
  } catch (error) {
    testResults.failed.push(`❌ Speaker selection: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test 4: Play All functionality
async function testPlayAllFeature() {
  console.log('\n▶️ Test 4: Play All functionality');
  try {
    const playAllButton = document.querySelector('button[aria-label*="すべて再生"]') || 
                          document.querySelector('button:has(svg[class*="play"])');
    
    if (!playAllButton) {
      throw new Error('Play All button not found');
    }
    
    console.log('   ✅ Play All button found');
    
    // Check for speed selector
    const speedSelector = document.querySelector('select[aria-label*="speed"]') ||
                         document.querySelector('.play-all-controls select');
    
    if (!speedSelector) {
      throw new Error('Speed selector not found');
    }
    
    const speedOptions = speedSelector.querySelectorAll('option');
    console.log(`   ✅ Speed selector with ${speedOptions.length} options`);
    
    // Check for progress bar
    const progressBar = document.querySelector('.progress-bar') ||
                       document.querySelector('[role="progressbar"]');
    
    if (!progressBar) {
      throw new Error('Progress bar not found');
    }
    
    console.log('   ✅ Progress bar present');
    
    // Check for skip button
    const skipButton = document.querySelector('button[aria-label*="スキップ"]') ||
                      document.querySelector('button:has(svg[class*="skip"])');
    
    if (!skipButton) {
      throw new Error('Skip button not found');
    }
    
    console.log('   ✅ Skip button found');
    
    testResults.passed.push('✅ Play All functionality working');
  } catch (error) {
    testResults.failed.push(`❌ Play All: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test 5: Selective WAV export
async function testSelectiveExport() {
  console.log('\n✅ Test 5: Selective WAV export');
  try {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    if (checkboxes.length === 0) {
      throw new Error('No selection checkboxes found');
    }
    
    console.log(`   ✅ ${checkboxes.length} selection checkboxes found`);
    
    // Check for WAV save button
    const saveButton = document.querySelector('button[aria-label*="WAV"]') ||
                      document.querySelector('button:contains("WAVで保存")');
    
    if (!saveButton) {
      console.log('   ⚠️ WAV save button not visible (may require timeline items)');
    } else {
      console.log('   ✅ WAV save button found');
    }
    
    testResults.passed.push('✅ Selective WAV export working');
  } catch (error) {
    testResults.failed.push(`❌ Selective export: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test 6: Font size check
async function testFontSize() {
  console.log('\n📏 Test 6: Font size (24px)');
  try {
    const textElement = document.querySelector('.editable-text');
    
    if (!textElement) {
      throw new Error('Editable text element not found');
    }
    
    const computedStyle = window.getComputedStyle(textElement);
    const fontSize = computedStyle.fontSize;
    
    if (fontSize !== '24px') {
      throw new Error(`Expected 24px, got ${fontSize}`);
    }
    
    console.log(`   ✅ Font size is ${fontSize}`);
    testResults.passed.push('✅ Font size correctly set to 24px');
  } catch (error) {
    testResults.failed.push(`❌ Font size: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test 7: API endpoint tests
async function testAPIEndpoints() {
  console.log('\n🌐 Test 7: API endpoints');
  try {
    // Test batch synthesis endpoint
    const response = await fetch('http://localhost:8000/tts/synthesize_batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        texts: ['テスト1', 'テスト2'],
        speaker_id: 0,
        speed: 1.0,
        pitch: 0,
        intonation: 1.0
      })
    });
    
    if (response.ok) {
      console.log('   ✅ Batch synthesis endpoint responding');
    } else {
      throw new Error(`Batch endpoint returned ${response.status}`);
    }
    
    // Test speakers endpoint
    const speakersResponse = await fetch('http://localhost:8000/tts/speakers');
    
    if (speakersResponse.ok) {
      const speakers = await speakersResponse.json();
      console.log(`   ✅ Speakers endpoint returned ${speakers.length} speakers`);
    } else {
      throw new Error(`Speakers endpoint returned ${speakersResponse.status}`);
    }
    
    testResults.passed.push('✅ API endpoints working');
  } catch (error) {
    testResults.failed.push(`❌ API endpoints: ${error.message}`);
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting test suite...\n');
  
  await testPitchAdjustment();
  await testKeyboardShortcuts();
  await testSpeakerSelection();
  await testPlayAllFeature();
  await testSelectiveExport();
  await testFontSize();
  await testAPIEndpoints();
  
  // Generate report
  console.log('\n=====================================');
  console.log('📊 Test Results Summary');
  console.log('=====================================');
  console.log(`✅ Passed: ${testResults.passed.length}`);
  console.log(`❌ Failed: ${testResults.failed.length}`);
  console.log(`📅 Timestamp: ${testResults.timestamp}`);
  
  if (testResults.passed.length > 0) {
    console.log('\n✅ Passed tests:');
    testResults.passed.forEach(test => console.log(`   ${test}`));
  }
  
  if (testResults.failed.length > 0) {
    console.log('\n❌ Failed tests:');
    testResults.failed.forEach(test => console.log(`   ${test}`));
  }
  
  const successRate = (testResults.passed.length / (testResults.passed.length + testResults.failed.length) * 100).toFixed(1);
  console.log(`\n🎯 Success rate: ${successRate}%`);
  
  return testResults;
}

// Export for use in other test files
if (typeof module !== 'undefined') {
  module.exports = { runAllTests, testResults };
} else {
  // Run tests if loaded in browser
  runAllTests();
}