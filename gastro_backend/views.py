from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from google import genai
from google.genai import types
import yt_dlp

# Standard homepage view
def home(request):
    return render(request, 'index.html')

# Core AI recipe distillation engine route listener
@csrf_exempt
def distill_recipe(request):
    if request.method == 'POST':
        try:
            # Parse incoming JSON payload parameters from JavaScript client
            data = json.loads(request.body)
            video_url = data.get('url')
            target_lang = data.get('lang', 'en')
            
            # 1. Fetch the secret API key from our active terminal memory space
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({"error": "Gemini API Key is missing from Render environment variables."}, status=500)
            
            video_context = 'Cooking Recipe Video Stream'
            description_context = ''
            
            # 2. Extract media metadata layer safely using custom browser headers
            try:
                ydl_opts = {
                    'skip_download': True,
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    # Add a standard browser user-agent header to safely bypass simple cloud firewalls
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=False)
                    video_context = info_dict.get('title', video_context)
                    description_context = info_dict.get('description', '')
            except Exception as yt_err:
                print(f"yt-dlp fallback triggered: {str(yt_err)}")
            
            # 3. Initialize the official Google GenAI Client
            client = genai.Client(api_key=api_key)
            
            # 4. Craft a strict prompt instructing Gemini to analyze the specific text data extracted
            prompt_instructions = f"""
            You are a master culinary assistant trained to clean up video cooking instructions.
            Analyze the following specific video stream data:
            URL: {video_url}
            Video Title: {video_context}
            Video Description/Transcript Context: {description_context}
            
            YOUR MISSION:
            1. Extract the exact title of the dish from the provided Video Title (e.g., if it says Chicken Kebab, make the title Chicken Kebab).
            2. Extract all ingredients mentioned in the title or description text details.
            3. Break down the actual cooking process step-by-step based on the provided text details.
            
            CRITICAL DEPLOYMENT INSTRUCTIONS:
            - Do not guess or invent a random dish like spaghetti if the text details mention a specific food item. Use the provided Title and Description text data.
            - Write all output text in very simple, easy-to-read instructions.
            - Translate all content entirely into the chosen language code: '{target_lang}'.
            - Return the response strictly as a valid JSON object matching this schema blueprint, without markdown code block formatting tags:
            {{
                "title": "Clean Dish Title",
                "ingredients": ["Ingredient item 1", "Ingredient item 2"],
                "steps": ["Step 1 description text", "Step 2 description text"]
            }}
            """
            
            # 5. Call gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_instructions,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            # 6. Parse the clean JSON text string back into a Python dictionary
            ai_data = json.loads(response.text)
            return JsonResponse(ai_data, status=200)
            
        except Exception as e:
            return JsonResponse({"error": f"AI Processing Error: {str(e)}"}, status=500)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)