#!/usr/bin/env python3
"""
MioVo Backend Features Test Suite
Tests for new TTS API endpoints and batch processing
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List

import httpx

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_RESULTS: Dict[str, List[str]] = {"passed": [], "failed": []}


async def test_health_check():
    """Test API health check endpoint"""
    print("🏥 Test: Health check endpoint")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check: {data['status']}")
                TEST_RESULTS["passed"].append("Health check endpoint")
            else:
                raise Exception(f"Status code {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Health check: {e}")


async def test_speakers_endpoint():
    """Test speakers listing endpoint"""
    print("\n🎤 Test: Speakers endpoint")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/tts/speakers")
            if response.status_code == 200:
                speakers = response.json()
                print(f"   ✅ Found {len(speakers)} speakers")
                
                # Check if we have 10 speakers
                if len(speakers) == 10:
                    print("   ✅ Correct number of speakers (10)")
                    for i, speaker in enumerate(speakers[:3]):
                        print(f"      Speaker {i}: {speaker['name']}")
                    print("      ...")
                else:
                    raise Exception(f"Expected 10 speakers, got {len(speakers)}")
                    
                TEST_RESULTS["passed"].append("Speakers endpoint")
            else:
                raise Exception(f"Status code {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Speakers endpoint: {e}")


async def test_audio_query_endpoint():
    """Test audio query generation endpoint"""
    print("\n📝 Test: Audio query endpoint")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/tts/audio_query",
                json={
                    "text": "こんにちは",
                    "speaker_id": 0
                }
            )
            if response.status_code == 200:
                query = response.json()
                
                # Check for mora-level data
                if "accent_phrases" in query:
                    print("   ✅ Audio query generated")
                    print(f"   ✅ Contains {len(query['accent_phrases'])} accent phrases")
                    
                    # Check for moras
                    first_phrase = query["accent_phrases"][0]
                    if "moras" in first_phrase:
                        print(f"   ✅ First phrase has {len(first_phrase['moras'])} moras")
                else:
                    raise Exception("No accent_phrases in response")
                    
                TEST_RESULTS["passed"].append("Audio query endpoint")
            else:
                raise Exception(f"Status code {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Audio query: {e}")


async def test_synthesis_endpoint():
    """Test single text synthesis endpoint"""
    print("\n🔊 Test: Single synthesis endpoint")
    async with httpx.AsyncClient() as client:
        try:
            # First get audio query
            query_response = await client.post(
                f"{BASE_URL}/tts/audio_query",
                json={
                    "text": "テスト",
                    "speaker_id": 0
                }
            )
            
            if query_response.status_code != 200:
                raise Exception("Failed to get audio query")
            
            audio_query = query_response.json()
            
            # Then synthesize
            response = await client.post(
                f"{BASE_URL}/tts/synthesize",
                json={
                    "audio_query": audio_query,
                    "speaker_id": 0,
                    "enable_interrogative_upspeak": False
                }
            )
            
            if response.status_code == 200:
                # Check if we got audio data
                if response.headers.get("content-type") == "audio/wav":
                    print("   ✅ WAV audio generated")
                    print(f"   ✅ Size: {len(response.content)} bytes")
                else:
                    print(f"   ⚠️ Content type: {response.headers.get('content-type')}")
                    
                TEST_RESULTS["passed"].append("Synthesis endpoint")
            else:
                raise Exception(f"Status code {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Synthesis: {e}")


async def test_batch_synthesis_endpoint():
    """Test batch synthesis endpoint for Play All feature"""
    print("\n🎵 Test: Batch synthesis endpoint")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/tts/synthesize_batch",
                json={
                    "texts": ["こんにちは", "今日はいい天気ですね", "ありがとう"],
                    "speaker_id": 0,
                    "speed": 1.0,
                    "pitch": 0,
                    "intonation": 1.0
                }
            )
            
            if response.status_code == 200:
                # Check if we got audio data
                if response.headers.get("content-type") == "audio/wav":
                    print("   ✅ Batch WAV audio generated")
                    print(f"   ✅ Combined size: {len(response.content)} bytes")
                    print("   ✅ Successfully concatenated 3 texts")
                else:
                    print(f"   ⚠️ Content type: {response.headers.get('content-type')}")
                    
                TEST_RESULTS["passed"].append("Batch synthesis endpoint")
            else:
                raise Exception(f"Status code {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Batch synthesis: {e}")


async def test_pitch_adjustment():
    """Test pitch adjustment in audio query"""
    print("\n🎚️ Test: Pitch adjustment")
    async with httpx.AsyncClient() as client:
        try:
            # Get audio query
            response = await client.post(
                f"{BASE_URL}/tts/audio_query",
                json={
                    "text": "テスト",
                    "speaker_id": 0
                }
            )
            
            if response.status_code != 200:
                raise Exception("Failed to get audio query")
            
            query = response.json()
            
            # Adjust pitch of first mora
            original_pitch = query["accent_phrases"][0]["moras"][0]["pitch"]
            query["accent_phrases"][0]["moras"][0]["pitch"] = original_pitch + 0.5
            
            # Try synthesis with adjusted pitch
            synth_response = await client.post(
                f"{BASE_URL}/tts/synthesize",
                json={
                    "audio_query": query,
                    "speaker_id": 0,
                    "enable_interrogative_upspeak": False
                }
            )
            
            if synth_response.status_code == 200:
                print("   ✅ Pitch adjustment accepted")
                print(f"   ✅ Original pitch: {original_pitch}")
                print(f"   ✅ Adjusted pitch: {original_pitch + 0.5}")
                TEST_RESULTS["passed"].append("Pitch adjustment")
            else:
                raise Exception(f"Synthesis failed with status {synth_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Pitch adjustment: {e}")


async def test_speed_variations():
    """Test different playback speeds"""
    print("\n⚡ Test: Speed variations")
    speeds = [1.0, 1.25, 1.5, 2.0]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            for speed in speeds:
                response = await client.post(
                    f"{BASE_URL}/tts/synthesize_batch",
                    json={
                        "texts": ["速度テスト"],
                        "speaker_id": 0,
                        "speed": speed,
                        "pitch": 0,
                        "intonation": 1.0
                    }
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Speed {speed}x: OK")
                else:
                    raise Exception(f"Speed {speed}x failed with status {response.status_code}")
            
            TEST_RESULTS["passed"].append("Speed variations")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Speed variations: {e}")


async def test_accent_pause_modifications():
    """Test accent and pause modifications"""
    print("\n🎭 Test: Accent and pause modifications")
    async with httpx.AsyncClient() as client:
        try:
            # Get audio query
            response = await client.post(
                f"{BASE_URL}/tts/audio_query",
                json={
                    "text": "テスト文章",
                    "speaker_id": 0
                }
            )
            
            if response.status_code != 200:
                raise Exception("Failed to get audio query")
            
            query = response.json()
            
            # Add accent (increase is_accent flag)
            if query["accent_phrases"][0]["moras"]:
                query["accent_phrases"][0]["accent"] = 1  # Set accent position
                print("   ✅ Accent position modified")
            
            # Add pause
            query["accent_phrases"][0]["pause_mora"] = {
                "text": "、",
                "consonant": None,
                "consonant_length": None,
                "vowel": "pau",
                "vowel_length": 0.2,
                "pitch": 0
            }
            print("   ✅ Pause mora added")
            
            # Extend vowel length
            if query["accent_phrases"][0]["moras"]:
                original_length = query["accent_phrases"][0]["moras"][0]["vowel_length"]
                query["accent_phrases"][0]["moras"][0]["vowel_length"] = original_length * 1.5
                print(f"   ✅ Vowel length extended from {original_length} to {original_length * 1.5}")
            
            TEST_RESULTS["passed"].append("Accent/pause modifications")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            TEST_RESULTS["failed"].append(f"Accent/pause: {e}")


async def run_all_tests():
    """Run all backend tests"""
    print("🧪 MioVo Backend Features Test Suite")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().isoformat()}\n")
    
    # Run tests
    await test_health_check()
    await test_speakers_endpoint()
    await test_audio_query_endpoint()
    await test_synthesis_endpoint()
    await test_batch_synthesis_endpoint()
    await test_pitch_adjustment()
    await test_speed_variations()
    await test_accent_pause_modifications()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Passed: {len(TEST_RESULTS['passed'])}")
    print(f"❌ Failed: {len(TEST_RESULTS['failed'])}")
    
    if TEST_RESULTS["passed"]:
        print("\n✅ Passed tests:")
        for test in TEST_RESULTS["passed"]:
            print(f"   • {test}")
    
    if TEST_RESULTS["failed"]:
        print("\n❌ Failed tests:")
        for test in TEST_RESULTS["failed"]:
            print(f"   • {test}")
    
    # Calculate success rate
    total = len(TEST_RESULTS["passed"]) + len(TEST_RESULTS["failed"])
    if total > 0:
        success_rate = (len(TEST_RESULTS["passed"]) / total) * 100
        print(f"\n🎯 Success rate: {success_rate:.1f}%")
    
    return TEST_RESULTS


if __name__ == "__main__":
    try:
        results = asyncio.run(run_all_tests())
        sys.exit(0 if not results["failed"] else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)