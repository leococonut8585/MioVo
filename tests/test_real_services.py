#!/usr/bin/env python3
"""
Test real services connection with Cloudflare Tunnel
"""

import asyncio
import httpx
import json
import base64
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_tts_synthesis():
    """Test actual TTS synthesis with AivisSpeech"""
    print("\n🎤 Testing TTS synthesis with real AivisSpeech...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Step 1: Get audio query
            print("1. Creating audio query...")
            query_response = await client.post(
                f"{BASE_URL}/tts/audio_query",
                json={"text": "こんにちは。MioVoから実際の音声合成テストです。", "speaker_id": 0}
            )
            
            if query_response.status_code == 200:
                audio_query = query_response.json()
                print(f"   ✅ Audio query created: {len(audio_query.get('accent_phrases', []))} accent phrases")
                
                # Step 2: Synthesize audio
                print("2. Synthesizing audio...")
                synth_response = await client.post(
                    f"{BASE_URL}/tts/synthesize",
                    json={
                        "audio_query": audio_query,
                        "speaker_id": 0,
                        "enable_interrogative_upspeak": False
                    }
                )
                
                if synth_response.status_code == 200:
                    audio_data = synth_response.content
                    print(f"   ✅ Audio synthesized: {len(audio_data)} bytes")
                    
                    # Save to file
                    with open("test_output.wav", "wb") as f:
                        f.write(audio_data)
                    print("   ✅ Saved to test_output.wav")
                    return True
                else:
                    print(f"   ❌ Synthesis failed: {synth_response.status_code}")
                    print(f"   Response: {synth_response.text}")
            else:
                print(f"   ❌ Audio query failed: {query_response.status_code}")
                print(f"   Response: {query_response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    return False

async def test_batch_synthesis():
    """Test batch synthesis"""
    print("\n🎵 Testing batch synthesis...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/tts/synthesize_batch",
                json={
                    "texts": [
                        "これは最初のテキストです。",
                        "次に二番目のテキスト。",
                        "最後に三番目のテキストです。"
                    ],
                    "speaker_id": 0,
                    "speed": 1.0,
                    "pitch": 0,
                    "intonation": 1.0
                }
            )
            
            if response.status_code == 200:
                audio_data = response.content
                print(f"   ✅ Batch audio synthesized: {len(audio_data)} bytes")
                
                # Save batch output
                with open("test_batch_output.wav", "wb") as f:
                    f.write(audio_data)
                print("   ✅ Saved to test_batch_output.wav")
                return True
            else:
                print(f"   ❌ Batch synthesis failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    return False

async def test_rvc_connection():
    """Test RVC service connection"""
    print("\n🎸 Testing RVC service connection...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/rvc/test_connection")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ RVC connected: {data['message']}")
                print(f"   Response time: {data['response_time_ms']:.2f}ms")
                
                # Test GPU info
                gpu_response = await client.get(f"{BASE_URL}/rvc/gpu_info")
                if gpu_response.status_code == 200:
                    gpu_data = gpu_response.json()
                    print(f"   GPU Available: {gpu_data.get('gpu_available', False)}")
                    if gpu_data.get('gpu_name'):
                        print(f"   GPU: {gpu_data['gpu_name']}")
                        print(f"   VRAM: {gpu_data.get('vram_total_gb', 0):.1f}GB")
                return True
            else:
                print(f"   ❌ RVC connection failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    return False

async def test_speakers():
    """Get available speakers"""
    print("\n🗣️ Getting available speakers...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/tts/speakers")
            if response.status_code == 200:
                speakers = response.json()
                print(f"   ✅ Found {len(speakers)} speakers:")
                for speaker in speakers[:5]:  # Show first 5
                    print(f"      - {speaker['name']} (ID: {speaker['id']})")
                return True
            else:
                print(f"   ❌ Failed to get speakers: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 MioVo Real Services Test")
    print(f"📅 {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Check service status first
    print("\n📊 Checking service status...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/services/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Mode: {status['mode']}")
                print(f"✅ AivisSpeech: {'Connected' if status['services']['aivisspeech']['available'] else 'Not available'}")
                print(f"✅ RVC: {'Connected' if status['services']['rvc']['available'] else 'Not available'}")
                
                if status['mode'] != 'production':
                    print("\n⚠️ WARNING: Not in production mode. Set ENABLE_REAL_SERVICES=true")
                    return
        except Exception as e:
            print(f"❌ Failed to check status: {e}")
            return
    
    # Run tests
    results = []
    
    results.append(("Speakers", await test_speakers()))
    results.append(("TTS Synthesis", await test_tts_synthesis()))
    results.append(("Batch Synthesis", await test_batch_synthesis()))
    results.append(("RVC Connection", await test_rvc_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🎯 Success rate: {(passed/len(results)*100):.1f}%")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Real services are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())